from pkg_resources import require

from dls_focusstack.main_service import FocusStackService
from dls_imagematch import logconfig

require("numpy==1.11.1")
require('pygelf==0.2.11')

import argparse
import logging
import re
import sys

from dls_imagematch.service import CrystalMatch
from dls_util.config.argparse_readable_config_dir import ReadableConfigDir
from dls_util.shape import Point
from os.path import join


# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
if IS_BUNDLED:
    CONFIG_DIR = join(".", ReadableConfigDir.CONFIG_DIR_NAME)
else:
    CONFIG_DIR = join("..", ReadableConfigDir.CONFIG_DIR_NAME)

class CrystalMatchService:

    def __init__(self):
       pass


    def run(self):
        parser = self._get_argument_parser()
        args = parser.parse_args()

        # Setup parameters
        config_directory = args.config
        if config_directory is None:
            config_directory = CONFIG_DIR
        scale_override = self._get_scale_override(args)

        # Run service
        service = CrystalMatch(config_directory, log_dir=args.log, scale_override=scale_override)
        selected_points = self._parse_selected_points_from_args(args)
        service_results = service.perform_match(args.image_input.name,
                                                args.image_output.name,
                                                selected_points)



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
        parser.add_argument('image_input',
                            metavar="Formulatrix_image",
                            type=file,
                            help='Image file from the Formulatrix - selected_point should correspond to co-ordinates on '
                                 'this image.')
        parser.add_argument('image_output',
                            metavar="beamline_image",
                            type=file,
                            help='Image file on which to find translated co-ordinates.')
        parser.add_argument('selected_points',
                            metavar="x,y",
                            nargs='*',
                            help="Comma-separated co-ordinates of selected points to be translated from the marked image "
                                 "to the target image.")
        parser.add_argument('--config',
                            metavar="path",
                            action=ReadableConfigDir,
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
        parser.add_argument('--log',
                            metavar="path",
                            help="Write log files to the directory specified by path.")
        return parser


if __name__ == '__main__':
    logconfig.setup_logging()
    service = CrystalMatchService()
    service.run()
