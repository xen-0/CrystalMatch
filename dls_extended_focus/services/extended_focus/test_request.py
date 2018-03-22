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
        for i in range(n):
            header = self._msg_headers(n=i)
            request = self._msg_body(n=i)
            connection.send(queue, request, headers=header)

    def _msg_headers(self, n=0):
        return {
            "job_id": self._get_job_id(n)
        }

    def _msg_body(self, n=0):
        json_obj = {
            "job_id": self._get_job_id(n),
            "target_dir": self.target_dir,
            "output_path": self.output_dir
        }
        return json.dumps(json_obj)

    def _get_job_id(self, n):
        return self.job_id if n is 0 else self.job_id + "_" + str(n)
