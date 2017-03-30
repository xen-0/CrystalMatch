import json


class TestRequest:
    """
    Test object used to manually send requests to the ActiveMQ server.  Allows the service to be tested locally.
    """
    def __init__(self, job_id, target_dir, output_dir):
        self.job_id = job_id
        self.target_dir = target_dir
        self.output_dir = output_dir

    def send(self, connection, queue, n=1):
        header = self._msg_headers()
        request = self._msg_body()
        for i in range(n):
            connection.send(queue, request, headers=header)

    def _msg_headers(self):
        return {
            "job_id": self.job_id
        }

    def _msg_body(self):
        json_obj = {
            "job_id": self.job_id,
            "target_dir": self.target_dir,
            "output_path": self.output_dir
        }
        return json.dumps(json_obj)
