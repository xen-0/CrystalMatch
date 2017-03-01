import json
import logging

from stomp import ConnectionListener

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
        job_id = headers["job_id"] if "job_id" in headers.keys() else None
        try:
            request = json.loads(body)
            if self.validate_request(request, job_id, headers['message-id'], headers['subscription']):
                job_id = request["job_id"]
                self._file_manager.set_target_dir(request["target_dir"])
                self._file_manager.set_output_path(request["output_path"])
                self.run_extended_focus_client(job_id,
                                               self._file_manager,
                                               headers['message-id'],
                                               headers['subscription'])
        except ValueError as e:
            err = "Malformed JSON request received: " + e.message
            logging.error(err)
            self._send_error_response(job_id, err,
                                      headers['message-id'], headers['subscription'])

    def run_extended_focus_client(self, job_id, file_manager, message_id, subscription_id):
        result = self._client.run(file_manager.target_dir(), file_manager.output_path())
        if result == 0:
            self._send_success(job_id, file_manager.original_output_path(), message_id, subscription_id)
        else:
            logging.error("Extended Focus client failed.")
            self._send_error_response(job_id,
                                      "The Extended Focus Service failed - please check "
                                      "logs on server for more information.",
                                      message_id,
                                      subscription_id)

    def _send_success(self, job_id, output_path, message_id, subscription_id):
        response = {"job_id": job_id, "response_code": 0, "output_path": output_path}
        msg = json.dumps(response)
        self._connection.send(self._output_queue, msg)
        self._connection.ack(message_id, subscription_id)

    def _send_error_response(self, job_id, err_msg, message_id, subscription_id):
        response = {"job_id": job_id, "response_code": 1, "err_msg": err_msg}
        msg = json.dumps(response)
        self._connection.send(self._output_queue, msg)
        self._connection.ack(message_id, subscription_id)

    def validate_request(self, request, header_job_id, message_id, subscription_id):
        keys = request.keys()
        err = None
        if "output_path" not in keys or "target_dir" not in keys or "job_id" not in keys:
            err = "Invalid request received - required keys missing from request JSON: " + json.dumps(request)
            logging.error(err)
        elif header_job_id is not None and header_job_id != request["job_id"]:
            err = "Mismatched job_id found in request - '" + \
                  header_job_id + "' in header and '" + request["job_id"] + "' in JSON."

        if err is None:
            return True
        logging.error(err)
        self._send_error_response(header_job_id, err, message_id, subscription_id)
        return False
