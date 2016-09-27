import sys
import argparse
import re
from dls_util.shape import Point
from os.path import dirname
from sys import path
from service import CrystalMatchService
path.append(dirname(path[0]))

# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
if IS_BUNDLED:
    CONFIG_DIR = "./config/"
else:
    CONFIG_DIR = "../config/"


def main():
    parser = get_argument_parser()
    args = parser.parse_args()

    selected_points = parse_selected_points_from_args(args)

    service = CrystalMatchService(CONFIG_DIR)
    service.perform_match(args.image_marked.name, args.image_target.name, selected_points)


def parse_selected_points_from_args(args):
    """
    Parse the selected points list provided by the command line for validity and returns a list of Point objects.
    :param args: Command line arguments provided by argument parser - must contain 'selected_points'
    :return: List of Selected Points.
    """
    selected_points = []
    point_expected_format = re.compile("[0-9]+,[0-9]+")
    for point_string in args.coordinates:
        point_string = point_string.strip('()')
        if point_expected_format.fullmatch(point_string) is not None:
            x, y = map(int, point_string.strip('()').split(','))
            selected_points.append(Point(x, y))
        else:
            print ("WARNING: Selected point with invalid format will be ignored - '" + point_string + "'")
    return selected_points


def get_argument_parser():
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
    return parser


if __name__ == '__main__':
    main()
