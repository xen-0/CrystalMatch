import json
import logging

from stomp import ConnectionListener

from services.extended_focus.helicon_client import HeliconRunner


class ExtendedFocusServiceRequestHandler(ConnectionListener):
    # TODO: add on error method?
    def __init__(self, connection, output_queue_name, config_dir):
        super(ExtendedFocusServiceRequestHandler, self).__init__()
        self._connection = connection
        self._output_queue = output_queue_name
        self._client = HeliconRunner(config_dir)

    def on_message(self, headers, body):
        super(ExtendedFocusServiceRequestHandler, self).on_message(headers, body)
        try:
            request = json.loads(body)
            if self.validate_request(request):
                self.run_extended_focus_client(request["target_dir"], request["output_path"])
            else:
                logging.error("Invalid request received: " + body)
                self._send_error_response("Invalid JSON request received - missing objects.")
        except ValueError as e:
            self._send_error_response("Malformed JSON request received - could not decode.")
            logging.error("Malformed JSON request received: " + e.message)

    def run_extended_focus_client(self, target_dir, output_path):
        result = self._client.run(target_dir, output_path)
        if result == 0:
            self._send_success(output_path)
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
