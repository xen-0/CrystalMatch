import logging
import time
from logging.handlers import TimedRotatingFileHandler
from sys import stdout

from os.path import split, exists, isdir, realpath, join

from os import makedirs

import stomp

from services.extended_focus.ext_focus_config import ExtendedFocusConfig
from services.extended_focus_service import ExtendedFocusService


def start_logging(run_dir, config):
    level = config.log_level.value()
    if level is not None:
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # File logging
        log_path = join(run_dir, "logs/service/service_runner.log")
        log_dir, log_file_name = split(log_path)
        if not exists(log_dir) or not isdir(log_dir):
            makedirs(log_dir)
        log_handler = TimedRotatingFileHandler(log_path, when='H', backupCount=config.log_length.value())
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
    config = ExtendedFocusConfig(join(run_dir, "config"))
    start_logging(run_dir, config)
    ExtendedFocusService(config).start()

    # Send test messages
    connection = stomp.Connection(host_and_ports=[("localhost", 61613)])
    connection.start()
    connection.connect(wait=True)
    request = '{' \
              '"job_id": "test_job",' \
              '"target_dir": "/dls/i02-2/data/cm16780/cm16780-1/image_stack/extended_focus_service_test",' \
              '"output_path": "/dls/i02-2/data/cm16780/cm16780-1/image_stack/extended_focus_service_test/output.tif"' \
              '}'
    connection.send(ExtendedFocusService.INPUT_QUEUE, request, headers={"job_id": "test_job"})

    while 1:
        # TODO: End when no active services.
        time.sleep(2)

if __name__ == '__main__':
    main()
