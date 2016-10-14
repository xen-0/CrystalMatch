import sys
import argparse
import re
from os import access, R_OK, path
from dls_imagematch.service import CrystalMatchService
from dls_util.shape import Point

# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
if IS_BUNDLED:
    CONFIG_DIR = "./config/"
else:
    CONFIG_DIR = "../config/"


def main():
    parser = _get_argument_parser()
    args = parser.parse_args()

    selected_points = _parse_selected_points_from_args(args)
    config_directory = args.config
    if config_directory is None:
        config_directory = CONFIG_DIR

    service = CrystalMatchService(config_directory)
    service.perform_match(args.image_marked.name, args.image_target.name, selected_points)


def _parse_selected_points_from_args(args):
    """
    Parse the selected points list provided by the command line for validity and returns a list of Point objects.
    :param args: Command line arguments provided by argument parser - must contain 'selected_points'
    :return: List of Selected Points.
    """
    selected_points = []
    point_expected_format = re.compile("[0-9]+,[0-9]+")
    for point_string in args.selected_points:
        point_string = point_string.strip('()')
        match = point_expected_format.match(point_string)
        # Check the regex matches the entire string
        # DEV NOTE: can use re.full_match in Python v3
        if match is not None and match.span()[1] == len(point_string):
            x, y = map(int, point_string.strip('()').split(','))
            selected_points.append(Point(x, y))
        else:
            print ("WARNING: Selected point with invalid format will be ignored - '" + point_string + "'")
    return selected_points


def _get_argument_parser():
    """
    Return an argument parser for the Crystal Matching service.
    :return: Argument parser.
    """
    parser = argparse.ArgumentParser(description="Run Crystal Matching algorithm attempting to translate co-ordinates "
                                                 "from a marked image to the target image.")
    parser.add_argument('image_marked',
                        metavar="marked_image",
                        type=file,
                        help='Image file corresponding to the co-ordinates provided.')
    parser.add_argument('image_target',
                        metavar="target_image",
                        type=file,
                        help='Image file on which to find translated co-ordinates.')
    parser.add_argument('selected_points',
                        metavar="x,y",
                        nargs='+',
                        help="Comma-separated co-ordinates of selected points to be translated from the marked image "
                             "to the target image.")
    parser.add_argument('--config',
                        metavar="config_dir",
                        action=ReadableConfigDir,
                        help="Sets the configuration directory."
                        )
    return parser


class ReadableConfigDir(argparse.Action):
    """
    Argument parser action which verifies that the config directory specified is a valid, readable directory.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not path.isdir(prospective_dir):
            print ("WARNING: configuration directory not found, directory will be created: '" + prospective_dir + "'")
        elif access(prospective_dir, R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            print ("ERROR: configuration directory is not readable: '" + prospective_dir + "'")
            exit(1)

if __name__ == '__main__':
    main()
