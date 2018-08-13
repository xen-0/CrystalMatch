from pkg_resources import require

import logconfig
from version import VersionHandler

require('pygelf==0.2.11')
require("numpy==1.11.1")
require("scipy")
import argparse
import logging

from os.path import split, exists, isdir, isfile

from os import makedirs, remove
from sys import stdout

import sys
import time

from dls_util.config.argparse_readable_config_dir import ReadableConfigDir
from focus.focus_stack_lap_pyramid import FocusStack

# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
if IS_BUNDLED:
    CONFIG_DIR = "./" + ReadableConfigDir.CONFIG_DIR_NAME + "/"
else:
    CONFIG_DIR = "../" + ReadableConfigDir.CONFIG_DIR_NAME + "/"


class FocusStackService:

    def __init__(self):
        pass

    def run(self):
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        try:
            t1 = time.clock()
            parser = self._get_argument_parser()
            args = parser.parse_args()
            self._process_output_file_path(args.output)
            log.info("Focusstack started, first image, " + args.image_stack[0].name)

            stacker = FocusStack(args.image_stack, args.config)

            focused_image = stacker.composite()
            focused_image.save(args.output)
            calculation_time = time.clock() - t1

            extra = {'stack_time': calculation_time}
            log = logging.LoggerAdapter(log, extra)
            log.info("Crystal Match Focusstack finished")

        except IOError as e:
            log.error(e)

    @staticmethod
    def _get_argument_parser():
        parser = argparse.ArgumentParser(description="Takes a z-stack of images and creates a composite using the "
                                                     "in-focus sections of each image.")
        parser.add_argument('image_stack',
                            metavar="image_path",
                            type=file,
                            nargs="+",
                            help="A list of image files - each image represents a level of the z-stack.")
        parser.add_argument('-o', '--output',
                            metavar="output_path",
                            help="Specify output file - default is to create a file called 'output.png' in the working "
                                 "directory. This will overwrite existing files, if the path does not exist the app "
                                 "will attempt to make it.")
        parser.add_argument('--config',
                            metavar="path",
                            action=ReadableConfigDir,
                            default="./config",
                            help="Path to the config directory. If it does not exist one will be created with "
                                 "default settings.")
        return parser

    @staticmethod
    def _process_output_file_path(path):
        output_dir, output_file = split(path)
        if output_dir is not "":
            if not (exists(output_dir) and isdir(output_dir)):
                makedirs(output_dir)
        if exists(path) and isfile(path):
            remove(path)


if __name__ == '__main__':
    service = FocusStackService()
    logconfig.setup_logging()
    service.run()
