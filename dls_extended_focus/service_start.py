import logging
import time
from logging.handlers import TimedRotatingFileHandler
from sys import stdout

from os.path import split, exists, isdir, realpath, join

from os import makedirs

import stomp
from services.extended_focus_service import ExtendedFocusService


def start_logging(run_dir):
    # TODO: error to console if file logging not active
    # TODO: make log level and backup count configurable
    level = logging.DEBUG
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # File logging
    log_path = join(run_dir, "logs/service/service_runner.log")
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
    run_dir, script_name = split(realpath(__file__))
    start_logging(run_dir)
    ExtendedFocusService(join(run_dir, "config")).start()

    # Send test messages
    connection = stomp.Connection(host_and_ports=[("localhost", 61613)])
    connection.start()
    connection.connect(wait=True)
    request = '{"job_id": "test_job", "target_dir": "/dls/i02-2/data/cm16780/cm16780-1/image_stack/extended_focus_service_test","output_path": "/dls/i02-2/data/cm16780/cm16780-1/image_stack/extended_focus_service_test/output.tif"}'
    connection.send(ExtendedFocusService.INPUT_QUEUE, request)

    while 1:
        # TODO: End when no active services.
        time.sleep(2)

if __name__ == '__main__':
    main()
