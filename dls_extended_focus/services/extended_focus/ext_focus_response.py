import json
import logging


class ExtendedFocusServiceResponse:
    def __init__(self, job_id, message_id, subscription_id):
        self._subscription_id = subscription_id
        self._output_path = None
        self._message_id = message_id
        self._job_id = job_id
        self._err_msg = None
        self._err = None

    def is_error(self):
        return self._err_msg is not None

    def get_job_id(self):
        return self._job_id

    def set_job_id(self, job_id):
        self._job_id = job_id

    def set_output_path(self, output_path):
        self._output_path = output_path

    def set_err_message(self, err, err_msg=None):
        logging.error(err_msg)
        self._err = err
        self._err_msg = err_msg

    def send_and_acknowledge(self, connection, destination):
        """
        Send this response on the designated connection and destination
        :param (stomp.Connection) connection: An active stomp connection object.
        :param destination: Destination string for queue or topic.
        """
        body = self._generate_response_body()
        connection.send(destination, body, headers={"job_id": self.get_job_id()})
        connection.ack(self._message_id, self._subscription_id)

    def _generate_response_body(self):
        response = {"job_id": self._job_id}
        if self._err_msg is None:
            response["output_path"] = self._output_path
            response["response_code"] = 0
        else:
            response["err_msg"] = self._err_msg
            response["err_code"] = self._err[0]
            response["err_info"] = self._err[1]
            response["response_code"] = 1
        return json.dumps(response)
