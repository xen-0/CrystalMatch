from pkg_resources import require

from version import VersionHandler

require('pygelf==0.2.11')
require("numpy==1.11.1")
require("scipy")

from dls_focusstack.focus.focus_stack_lap_pyramid import FocusStack

from dls_imagematch import logconfig

import argparse
import logging
import re
import sys
import time
import cv2

from dls_util.imaging import Image

from dls_imagematch.service import CrystalMatch
from dls_util.config.argparse_readable_config_dir import ReadableConfigDir
from dls_util.shape import Point
from os.path import split, exists, isdir, isfile, join, abspath, getmtime

from os import makedirs, remove, walk, listdir, access, R_OK

# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
CONFIG_DIR_NAME = "config"
if IS_BUNDLED:
    CONFIG_DIR = join(".", ReadableConfigDir.CONFIG_DIR_NAME)
else:
    CONFIG_DIR = join("..", ReadableConfigDir.CONFIG_DIR_NAME)

class CrystalMatchService:

    def __init__(self):
       pass


    def run(self):
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        total_start = time.clock()
        try:
            parser = self._get_argument_parser()
            args = parser.parse_args()

            # Setup parameters
            config_directory = args.config
            if config_directory is None:
                config_directory = CONFIG_DIR
            scale_override = self._get_scale_override(args)

            focusing_path = args.beamline_stack_path

            selected_points = self._parse_selected_points_from_args(args)
            if "." not in focusing_path:
                files = []
                # Sort names according to creation time
                for file_name in listdir(focusing_path):
                    name = join(focusing_path, file_name)
                    files.append(file(name))
                files.sort(key=lambda x: getmtime(x.name))
                # Run focusstack
                stacker = FocusStack(files,config_directory)
                focused_image = stacker.composite()
            else:
                #works when only one image is passed
                focused_image = Image(cv2.imread(focusing_path))
            # Run match
            service = CrystalMatch(config_directory, scale_override=scale_override)
            service_results = service.perform_match(args.Formulatrix_image.name, focused_image, selected_points)

            service_results.set_beamline_image_path(args.beamline_stack_path)

            total_time = time.clock() - total_start
            service_results.log_final_result(total_time)
            service_results.print_results(args.to_json)
            # Save stacked image
            if "." not in focusing_path:
                focused_image.save(service_results.get_beamline_image_path())

        except IOError as e:
            log.error(e)

    @staticmethod
    def _get_scale_override(args):
        log = logging.getLogger(".".join([__name__]))
        log.addFilter(logconfig.ThreadContextFilter())

        if args.scale is not None:
            try:
                scales = args.scale.split(":")
                assert(len(scales) == 2)
                return float(scales[0]), float(scales[1])
            except AssertionError:
                log.error(AssertionError("Scale flag requires two values separated by a colon':'. Value given: " +
                                    str(args.scale)))
                raise AssertionError("Scale flag requires two values separated by a colon':'. Value given: " +
                                     str(args.scale))

            except ValueError:
                log.error("Scale must be given as a pair of float values separated by a colon (':'). Value given: " +
                                 str(args.scale))
                raise ValueError("Scale must be given as a pair of float values separated by a colon (':'). Value given: " +
                                 str(args.scale))
        return None

    @staticmethod
    def _parse_selected_points_from_args(args):
        """
        Parse the selected points list provided by the command line for validity and returns a list of Point objects.
        :param args: Command line arguments provided by argument parser - must contain 'selected_points'
        :return: List of Selected Points.
        """
        log = logging.getLogger(".".join([__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        selected_points = []
        if args.selected_points:
            point_expected_format = re.compile("[0-9]+,[0-9]+")
            for point_string in args.selected_points:
                point_string = point_string.strip('()')
                match_results = point_expected_format.match(point_string)
                # Check the regex matches the entire string
                # DEV NOTE: can use re.full_match in Python v3
                if match_results is not None and match_results.span()[1] == len(point_string):
                    x, y = map(int, point_string.strip('()').split(','))
                    selected_points.append(Point(x, y))
                else:
                    log.warning("Selected point with invalid format will be ignored - '" + point_string + "'")
        return selected_points

    @staticmethod
    def _get_argument_parser():
        """
        Return an argument parser for the Crystal Matching service.
        :return: Argument parser.
        """
        parser = argparse.ArgumentParser(description="Run Crystal Matching algorithm attempting to translate co-ordinates "
                                                     "on an input image to the coordinate-space of an output image while "
                                                     "accounting for possible movement of crystals in the sample.")
        parser.add_argument('Formulatrix_image',
                            metavar="Formulatrix_image_path",
                            type=file,
                            help='Image file from the Formulatrix - selected_point should correspond to co-ordinates on '
                                 'this image.')
        parser.add_argument('beamline_stack_path',
                            metavar="beamline_stack_path",
                            help="A path pointing at a directory which stores images to be stacked or a path to a stacked image.")
        parser.add_argument('selected_points',
                            metavar="x,y",
                            nargs='*',
                            help="Comma-separated co-ordinates of selected points to be translated from the marked image "
                                 "to the target image.")
        #parser.add_argument('-o','--output',
         #                   metavar="beamline_image_path",
         #                   help="Specify stacked output file - default is to create a file called 'output.tif' in the working "
         #                        "directory. This will overwrite existing files, if the path does not exist the app "
         #                        "will attempt to make it.")
        parser.add_argument('--config',
                            metavar="path",
                            action=ReadableConfigDir,
                            default=join("..", "config"),
                            help="Sets the configuration directory.")
        parser.add_argument('--scale',
                            metavar="scale",
                            help="The scale between the Formulatrix and beamline image given as the resolution of each "
                                 "image separated by a colon. Note this is relative (1:2 is the same as 2:4) and a value "
                                 "must be specified for each image using the format "
                                 "'[Formulatrix_image_resolution]:[beamline_image_resolution]'.")
        parser.add_argument('--to_json',
                            action='store_true',
                            help="Output a JSON object.")
        parser.add_argument('--version',
                            action='version',
                            version=VersionHandler.version_string())

        return parser

    class ReadableConfigDir(argparse.Action):
        """
        Argument parser action which verifies that the config directory specified is a valid, readable directory.
        """
        def __call__(self, parser, namespace, values, option_string=None):
            prospective_dir = self.parse_config_path(values)
            if not sys.path.isdir(prospective_dir):
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

if __name__ == '__main__':
    logconfig.setup_logging()
    service = CrystalMatchService()
    service.run()
