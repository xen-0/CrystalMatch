import logging
from logging.handlers import TimedRotatingFileHandler
from os import makedirs
from os.path import split, exists, isdir, realpath, join
from sys import stdout

from gui.ext_focus_service_gui import ExtendedFocusServiceGUI
from services.extended_focus.ext_focus_config import ExtendedFocusConfig
from services.extended_focus_service import ExtendedFocusService
from version import VersionHandler


def start_logging(config):
    level = config.log_level.value()
    if level is not None:
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # File logging
        log_dir = join(get_root_dir(), "logs", "service")
        log_path = join(log_dir, "service_runner.log")
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


def get_root_dir():
    """
    During development the config and log files appear in the package - these should be removed during deployment #
    to cause this method to deafult to the directory above. This allows the configuration file to remain
    persistent between versions.
    :return: Root dir
    """
    run_dir, script = split(realpath(__file__))
    config_dir = join(run_dir, "config")
    if exists(config_dir) and isdir(config_dir):
        return run_dir
    else:
        return join(run_dir, "..")


def main():
    print "Starting Extended Focus Service, " + VersionHandler.version()
    config = ExtendedFocusConfig(join(get_root_dir(), "config"))
    start_logging(config)
    service = ExtendedFocusService(config)

    gui = ExtendedFocusServiceGUI(service)
    gui.mainloop()


if __name__ == '__main__':
    main()
