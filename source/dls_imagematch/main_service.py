import argparse
import logging
import re
import sys

from dls_imagematch.service import CrystalMatchService
from dls_imagematch.version import VersionHandler
from dls_util.config.argparse_readable_config_dir import ReadableConfigDir
from dls_util.shape import Point

# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
if IS_BUNDLED:
    CONFIG_DIR = "./" + ReadableConfigDir.CONFIG_DIR_NAME + "/"
else:
    CONFIG_DIR = "../" + ReadableConfigDir.CONFIG_DIR_NAME + "/"


def main():
    parser = _get_argument_parser()
    args = parser.parse_args()

    # Setup parameters
    config_directory = args.config
    if config_directory is None:
        config_directory = CONFIG_DIR
    debug = hasattr(args, "debug") and args.debug
    scale_override = _get_scale_override(args)

    # Run service
    service = CrystalMatchService(config_directory, log_dir=args.log, job_id=args.job,
                                  verbose=args.verbose, debug=debug, scale_override=scale_override)
    selected_points = _parse_selected_points_from_args(args)
    service_results = service.perform_match(args.image_input.name,
                                            args.image_output.name,
                                            selected_points,
                                            json_output=args.to_json)
    service_results.print_results()


def _get_scale_override(args):
    if args.scale is not None:
        try:
            scales = args.scale.split(":")
            assert(len(scales) == 2)
            return float(scales[0]), float(scales[1])
        except AssertionError:
            raise AssertionError("Scale flag requires two values separated by a colon':'. Value given: " +
                                 str(args.scale))
        except ValueError:
            raise ValueError("Scale must be given as a pair of float values separated by a colon (':'). Value given: " +
                             str(args.scale))
    return None


def _parse_selected_points_from_args(args):
    """
    Parse the selected points list provided by the command line for validity and returns a list of Point objects.
    :param args: Command line arguments provided by argument parser - must contain 'selected_points'
    :return: List of Selected Points.
    """
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
                logging.warning("Selected point with invalid format will be ignored - '" + point_string + "'")
    return selected_points


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
                        help="The scale between the Formulatrix and beamline given as two floats separated by a colon, "
                             "note this is relative (1:2 is the same as 2:4) and a value must be specified for each "
                             "image using the format '[input_image_resolution]:[output_image_resolution]'.")
    parser.add_argument('--version',
                        action='version',
                        version=VersionHandler.version_string())
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        help="Increase output verbosity.")
    parser.add_argument('-d', '--debug',
                        action="store_true",
                        help="Output debug information to the console.")
    parser.add_argument('-j', '--job',
                        metavar="job_id",
                        help="Specify a job_id - this will be reported in the output to help identify this run.")
    parser.add_argument('--to_json',
                        action='store_true',
                        help="Output a JSON object.")
    parser.add_argument('--log',
                        metavar="path",
                        help="Write log files to the directory specified by path.")
    return parser


if __name__ == '__main__':
    main()
