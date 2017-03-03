import json

# noinspection PyPackageRequirements
from stomp import ConnectionListener

from services.extended_focus.ext_focus_response import ExtendedFocusServiceResponse
from services.extended_focus.helicon_client import HeliconRunner


class ExtendedFocusServiceRequestHandler(ConnectionListener):
    def __init__(self, connection, file_manager, output_queue_name, config_dir):
        super(ExtendedFocusServiceRequestHandler, self).__init__()
        self._connection = connection
        self._file_manager = file_manager
        self._output_queue = output_queue_name
        self._client = HeliconRunner(config_dir)

    def on_error(self, headers, body):
        self._connection.nack(headers['message-id'], headers['subscription'])

    def on_message(self, headers, body):
        super(ExtendedFocusServiceRequestHandler, self).on_message(headers, body)
        # Start constructing a response
        job_id = headers['job_id'] if 'job_id' in headers.keys() else None
        response = ExtendedFocusServiceResponse(job_id, headers['message-id'], headers['subscription'])
        request, response = self.validate_request(body, response)
        if response.is_error():
            response.send_and_acknowledge(self._connection, self._output_queue)
        else:
            # Configure response
            response.set_job_id(request["job_id"])
            response.set_output_path(request["output_path"])

            # Set file manager
            self._file_manager.set_target_dir(request["target_dir"])
            self._file_manager.set_output_path(request["output_path"])

            self.run_extended_focus_client(response, self._file_manager)

    def run_extended_focus_client(self, response, file_manager):
        updated_response = self._client.run(response, file_manager)
        updated_response.send_and_acknowledge(self._connection, self._output_queue)

    @staticmethod
    def validate_request(body, response):
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

            # Perform other checks
            if "output_path" not in keys or "target_dir" not in keys:
                err = "Invalid request received - required keys missing from request JSON: " + json.dumps(request)
                response.set_err_message(err)
            # TODO: Check files exist and are accessible - prevent unnecessary timeout if we know this is going to fail
            return request, response
        except ValueError as e:
            response.set_err_message("Malformed JSON request received: " + e.message)
            return None, response
