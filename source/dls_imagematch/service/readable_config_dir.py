import argparse
import logging
import sys
import re

from os import access, R_OK, listdir

from os.path import join, split, isdir

# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
CONFIG_DIR_NAME = "config"
if IS_BUNDLED:
    CONFIG_DIR = join(".", CONFIG_DIR_NAME)
else:
    CONFIG_DIR = join("..", CONFIG_DIR_NAME)


class ReadableConfigDir(argparse.Action):
    """
    Argument parser action which verifies that the config directory specified is a valid, readable directory.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = self.parse_config_path(values)
        if not isdir(prospective_dir):
            logging.warning("Configuration directory not found, directory will be created: '" + prospective_dir + "'")
            setattr(namespace, self.dest, prospective_dir)
        elif access(prospective_dir, R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            logging.error("Configuration directory is not readable: '" + prospective_dir + "'")
            exit(1)

    def parse_config_path(self, proposed_path):
        """
        Parse a string to return a path for the config directory.
        :param proposed_path: String of the path to the configuration directory.
        :return: Path of config directory.
        """
        prospective_dir = proposed_path
        if isdir(proposed_path) and self._is_config_dir(proposed_path):
            return proposed_path
        config_path, config_dir = split(prospective_dir)
        if not config_dir == CONFIG_DIR_NAME:
            prospective_dir = join(prospective_dir, CONFIG_DIR_NAME)
        return prospective_dir

    @staticmethod
    def _is_config_dir(dir_path):
        for file_path in listdir(dir_path):
            if re.match(".*[.]ini", file_path):
                return True
        return False