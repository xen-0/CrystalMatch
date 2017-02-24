import json
import logging

from stomp import ConnectionListener

from services.extended_focus.helicon_client import HeliconRunner


class ExtendedFocusServiceRequestHandler(ConnectionListener):
    # TODO: add on error method?
    def __init__(self, connection, file_manager, output_queue_name, config_dir):
        super(ExtendedFocusServiceRequestHandler, self).__init__()
        self._connection = connection
        self._file_manager = file_manager
        self._output_queue = output_queue_name
        self._client = HeliconRunner(config_dir)

    def on_message(self, headers, body):
        super(ExtendedFocusServiceRequestHandler, self).on_message(headers, body)
        # TODO: test this on the live activeMQ server
        job_id = headers["job_id"] if "job_id" in headers.keys() else ""
        try:
            request = json.loads(body)
            if self.validate_request(request):
                if job_id == "":
                    # TODO: Consult with GDA team - should mismatched job_id be a fatal error?
                    job_id = request["job_id"]
                self._file_manager.set_target_dir(request["target_dir"])
                self._file_manager.set_output_path(request["output_path"])
                self.run_extended_focus_client(job_id, self._file_manager)
            else:
                logging.error("Invalid request received: " + body)
                self._send_error_response(job_id, "Invalid JSON request received - missing objects.")
        except ValueError as e:
            self._send_error_response(job_id, "Malformed JSON request received - could not decode: " + body)
            logging.error("Malformed JSON request received: " + e.message)

    def run_extended_focus_client(self, job_id, file_manager):
        result = self._client.run(file_manager.target_dir(), file_manager.output_path())
        if result == 0:
            self._send_success(job_id, file_manager.original_output_path())
        else:
            self._send_error_response(job_id, "The Extended Focus Service failed - "
                                              "please access the service logs on server.")

    def _send_success(self, job_id, output_path):
        response = {"job_id": job_id, "response_code": 0, "output_path": output_path}
        msg = json.dumps(response)
        self._connection.send(self._output_queue, msg)

    def _send_error_response(self, job_id, err_msg):
        response = {"job_id": job_id, "response_code": 1, "err_msg": err_msg}
        msg = json.dumps(response)
        self._connection.send(self._output_queue, msg)

    @staticmethod
    def validate_request(request):
        keys = request.keys()
        return "output_path" in keys and "target_dir" in keys and "job_id" in keys
