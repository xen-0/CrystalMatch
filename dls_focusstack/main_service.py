import argparse
import logging
from logging import DEBUG, INFO

from os.path import split, exists, isdir, isfile

from os import makedirs, remove
from sys import stdout

CONFIG_FILE = "../config/focus_stack.ini"


class FocusStackService:

    def __init__(self):
        pass

    def run(self):
        try:
            parser = self._get_argument_parser()
            args = parser.parse_args()
            self._set_up_logging(args.debug, args.verbose)
            self._process_output_file_path(args.output)
        except IOError as e:
            self._handle_error(e)

    @staticmethod
    def _get_argument_parser():
        parser = argparse.ArgumentParser(description="Takes a z-stack of images and creates a composite using the "
                                                     "in-focus sections of each image.")
        parser.add_argument('image_stack',
                            metavar="image_path",
                            type=file,
                            nargs="*",
                            help="A list of image files - each image represents a level of the z-stack.")
        parser.add_argument('-o', '--output',
                            metavar="output_path",
                            help="Specify output file - default is to create a file called 'output.png' in the working "
                                 "directory. This will overwrite existing files, if the path does not exist the app "
                                 "will attempt to make it.")
        parser.add_argument('-v', '--verbose',
                            action="store_true",
                            help="Increase output verbosity.")
        parser.add_argument('-d', '--debug',
                            action="store_true",
                            help="Output debug information to the console.")
        return parser

    @staticmethod
    def _process_output_file_path(path):
        output_dir, output_file = split(path)
        if output_dir is not "":
            if not (exists(output_dir) and isdir(output_dir)):
                makedirs(output_dir)
        if exists(path) and isfile(path):
            remove(path)

    def _set_up_logging(self, debug, verbose):
        # Set up logging
        root_logger = logging.getLogger()
        root_logger.setLevel(DEBUG)
        # Set up stream handler
        if debug:
            self._add_log_stream_handler(DEBUG, root_logger)
        elif verbose:
            self._add_log_stream_handler(INFO, root_logger)

    @staticmethod
    def _add_log_stream_handler(level, logger):
        stream_handler = logging.StreamHandler(stdout)
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)
        if level == DEBUG:
            logging.debug("DEBUG statements visible.")
        elif level == INFO:
            logging.info("INFO statements visible.")

    @staticmethod
    def _handle_error(e):
        """
        A placeholder method for dealing with errors raised during runtime - these need to be reported in JSON mode.
        :param e: Exception being raised
        """
        logging.error(e)


if __name__ == '__main__':
    service = FocusStackService()
    service.run()
