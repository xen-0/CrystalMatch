import logging
import time
from logging.handlers import TimedRotatingFileHandler
from sys import stdout

from os.path import split, exists, isdir

from os import makedirs

import stomp
from services.extended_focus_service import ExtendedFocusService


def start_logging():
    # TODO: set log file path
    # TODO: error to console if file logging not active
    level = logging.DEBUG
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # File logging
    log_path = "../logs/service/service_runner.log"
    log_dir, log_file_name = split(log_path)
    if not exists(log_dir) or not isdir(log_dir):
        makedirs(log_dir)
    log_handler = TimedRotatingFileHandler(log_path, when='H', backupCount=672)
    log_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    root_logger.addHandler(log_handler)

    # Console logging
    stream_handler = logging.StreamHandler(stdout)
    stream_handler.setLevel(level)
    root_logger.addHandler(stream_handler)
    # TODO: add some logging!


def main():
    start_logging()
    # TODO: set config file path
    ExtendedFocusService("../config").start()

    # Send test messages
    connection = stomp.Connection(host_and_ports=[("localhost", 61613)])
    connection.start()
    connection.connect(wait=True)
    request = '{"job_id": "test_job", "target_dir": "/dls/i02-2/data/cm16780/cm16780-1/image_stack/extended_focus_service_test","output_path": "/dls/i02-2/data/cm16780/cm16780-1/image_stack/extended_focus_service_test/output.tif"}'
    # request = '{"target_dir": "C:\\\\Users\\\\marcs\\\\Developer\\\\Diamond\\\\diamond-imagematch\\\\test-images\\\\Focus Stacking\\\\VMXI-AA005-G07-1-R0DRP1\\\\levels","output_path": "C:\\\\Users\\\\marcs\\\\Desktop\\\\service_output.jpg"}'
    connection.send(ExtendedFocusService.INPUT_QUEUE, request)

    while 1:
        # TODO: End when no active services.
        time.sleep(2)

if __name__ == '__main__':
    main()
