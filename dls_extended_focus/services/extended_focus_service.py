import json
import logging
import time
from random import randint
from threading import Thread
from time import sleep

import stomp
from stomp import ConnectionListener
from stomp.exception import ConnectFailedException

from services.extended_focus.ext_focus_response import ExtendedFocusServiceResponse
from services.extended_focus.helicon_client import HeliconRunner
from util.file_path_manager import FilePathManager


class ServiceState:
    """State handler for Service."""
    IDLE = 0
    PROCESSING = 1

    def __init__(self):
        self._value = self.IDLE

    def set_processing(self):
        self._value = self.PROCESSING

    def set_idle(self):
        self._value = self.IDLE

    def can_perform_safe_shutdown(self):
        return self._value == self.IDLE


class ExtendedFocusService(ConnectionListener):
    INPUT_QUEUE = '/queue/vmxi_extended_focus_service.input'
    OUTPUT_QUEUE = '/topic/vmxi_extended_focus_service.output'
    SERVICE_NAME = 'Extended Focus Service'

    def __init__(self, config):
        self._config = config
        self._id = randint(10000, 99999)
        self._host = self._config.host.value()
        self._port = self._config.port.value()
        self._connection = None
        self.log("Setting id: " + str(self._id))
        self._file_manager = FilePathManager(self._config)
        self._client = HeliconRunner(self._config.parent_directory())
        self._service_state = ServiceState()
        self._service_should_run = False

    def start(self):
        """
        Start the service and starts a monitoring thread which attempts to recover if the connection drops or
        cannot connect.
        """
        self._service_should_run = True
        keep_alive_thread = Thread(target=self._run_keep_alive_thread)
        keep_alive_thread.start()

    def safe_stop(self):
        self._service_should_run = False
        while not self._service_state.can_perform_safe_shutdown():
            sleep(1)
        # Wait for an additional second to make sure the ACK has time to reach the server.
        sleep(1)
        self._connection.disconnect()

    def force_stop(self):
        self._service_should_run = False
        if self.is_connected():
            self._connection.disconnect()

    def is_connected(self):
        return self._connection is not None and self._connection.is_connected()

    def on_message(self, headers, body):
        super(ExtendedFocusService, self).on_message(headers, body)
        if self._service_should_run:
            self._service_state.set_processing()
            # Start constructing a response
            job_id = headers['job_id'] if 'job_id' in headers.keys() else None
            response = ExtendedFocusServiceResponse(job_id, headers['message-id'], headers['subscription'])
            request, response = self._parse_and_validate_request(body, response)
            if response.is_error():
                response.send_and_acknowledge(self._connection, self.OUTPUT_QUEUE)
            else:
                self._run_extended_focus_client(response, self._file_manager)
        self._service_state.set_idle()

    def send_test_request(self, test_request, num_requests):
        """
        Send a test message to the ActiveMQ service - if the service is not connected this request is ignored.
        :param TestRequest test_request: A TestRequest object representing the message to send.
        :param num_requests: The number of requests to send to the active MQ.
        """
        if self.is_connected():
            test_request.send(self._connection, self.INPUT_QUEUE, n=num_requests)

    def _run_keep_alive_thread(self):
        """
        Monitors the stomp connection every 2 seconds and attempts to revive the connection when dropped.
        """
        while self._service_should_run:
            if not self.is_connected():
                self._connect_and_subscribe()
            time.sleep(2)

    def _connect_and_subscribe(self):
        try:
            self.log("Starting service, connecting to '" + self._host + ":" + str(self._port) + "'...")
            self._connection = stomp.Connection(host_and_ports=[(self._host, self._port)])
            self._connection.set_listener(self.SERVICE_NAME, self)
            self._connection.start()
            self._connection.connect(wait=True)
            self._connection.subscribe(destination=self.INPUT_QUEUE, id=self._id, ack='client-individual')
        except ConnectFailedException as e:
            logging.error(e.message)

    def _run_extended_focus_client(self, response, file_manager):
        updated_response = self._client.run(response, file_manager)
        updated_response.send_and_acknowledge(self._connection, self.OUTPUT_QUEUE)

    def _parse_and_validate_request(self, body, response):
        """
        Validate the request and set an error response if necessary
        :param body: The body content of the request message.
        :param response: The request object - should contain the job_id if it was included in the headers.
        :return: The request as a parsed JSON object and a response object (possibly with an updated error message)
        """
        try:
            request = json.loads(body)
            keys = request.keys()

            # Check and set the job_id against the header - ensures errors are reported against the correct job in GDA.
            header_job_id = response.get_job_id()
            if "job_id" not in keys:
                response.set_err_message('"job_id" missing from JSON request.')
                return request, response
            elif header_job_id is not None and header_job_id != request["job_id"]:
                err = "Mismatched job_id found in request - '" + \
                      header_job_id + "' in header and '" + request["job_id"] + "' in JSON."
                response.set_err_message(err)
            response.set_job_id(request['job_id'])
            response.set_output_path(request["output_path"])

            # Check keys exist
            if "output_path" not in keys or "target_dir" not in keys:
                err = "Invalid request received - required keys missing from request JSON: " + json.dumps(request)
                response.set_err_message(err)
                return request, response

            # Set and validate the file manager
            self._file_manager.set_target_dir(request["target_dir"])
            self._file_manager.set_output_path(request["output_path"])
            err_msg = self._file_manager.validate()
            if err_msg is not None:
                response.set_err_message(err_msg)
                return request, response

            # Checks complete
            return request, response
        except ValueError as e:
            response.set_err_message("Malformed JSON request received: " + e.message)
            return None, response

    @staticmethod
    def log(msg):
        logging.info("ExtendedFocusService: " + msg)
