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
        try:
            request = json.loads(body)
            if self.validate_request(request):
                self._file_manager.set_target_dir(request["target_dir"])
                self._file_manager.set_output_path(request["output_path"])
                self.run_extended_focus_client(self._file_manager)
            else:
                logging.error("Invalid request received: " + body)
                self._send_error_response("Invalid JSON request received - missing objects.")
        except ValueError as e:
            self._send_error_response("Malformed JSON request received - could not decode.")
            logging.error("Malformed JSON request received: " + e.message)

    def run_extended_focus_client(self, file_manager):
        result = self._client.run(file_manager.target_dir(), file_manager.output_path())
        if result == 0:
            self._send_success(file_manager.original_output_path())
        else:
            self._send_error_response("The Extended Focus Service failed - please access the service logs on server.")

    def _send_success(self, output_path):
        response = {"status": 0, "output_path": output_path}
        msg = json.dumps(response)
        self._connection.send(self._output_queue, msg)

    def _send_error_response(self, err_msg):
        response = {"status": 1, "err_msg": err_msg}
        msg = json.dumps(response)
        self._connection.send(self._output_queue, msg)

    @staticmethod
    def validate_request(request):
        keys = request.keys()
        return "output_path" in keys and "target_dir" in keys
