import argparse
import logging
import re
import cv2
from os.path import split, exists, isdir, isfile, join, abspath, getmtime

from os import listdir, makedirs

from dls_focusstack.focus.focus_stack_lap_pyramid import FocusStack
from dls_imagematch import logconfig
from dls_imagematch.service import readable_config_dir
from dls_imagematch.version import VersionHandler
from dls_imagematch.service.readable_config_dir import ReadableConfigDir
from dls_util.shape import Point
from dls_util.imaging import Image

class ParserManager:

    def __init__(self):
        self.parser = None

    def build_parser(self):
        """Return an argument parser for the Crystal Matching service.
        :return: Argument parser.
        """
        parser = argparse.ArgumentParser(
            description="Run Crystal Matching algorithm attempting to translate co-ordinates "
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
        parser.add_argument('-o','--output',
                           metavar="stacked_image_path",
                           default="processed.tif",
                           help="Specify stacked output file - default is to create a file called 'processed.tif' in the working "
                                "directory. This will overwrite existing files, if the path does not exist the app "
                                "will attempt to make it.")
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
        parser.add_argument('-j', '--job',
                            metavar="job_id",
                            help="Specify a job_id - this will be reported in the output to help identify this run.")
        parser.add_argument('--to_json',
                            action='store_true',
                            help="Output a JSON object.")
        parser.add_argument('--version',
                            action='version',
                            version=VersionHandler.version_string())
        self.parser = parser


    def _get_args(self):
        return self.parser.parse_args()

    def get_config_dir(self):
        config_directory = self._get_args().config
        if config_directory is None:
            config_directory = readable_config_dir.CONFIG_DIR
        return config_directory

    def get_scale_override(self):
        scale =  self._get_args().scale
        log = logging.getLogger(".".join([__name__]))
        log.addFilter(logconfig.ThreadContextFilter())

        if scale is not None:
            try:
                scales = scale.split(":")
                assert (len(scales) == 2)
                return float(scales[0]), float(scales[1])
            except AssertionError:
                log.error(AssertionError("Scale flag requires two values separated by a colon':'. Value given: " +
                                         str(scale)))
                raise AssertionError("Scale flag requires two values separated by a colon':'. Value given: " +
                                     str(scale))

            except ValueError:
                log.error("Scale must be given as a pair of float values separated by a colon (':'). Value given: " +
                          str(scale))
                raise ValueError(
                    "Scale must be given as a pair of float values separated by a colon (':'). Value given: " +
                    str(scale))
        return None

    def parse_selected_points_from_args(self):
        """Parse the selected points list provided by the command line for validity and returns a list of Point objects.
        :param args: Command line arguments provided by argument parser - must contain 'selected_points'
        :return: List of Selected Points.
         """
        log = logging.getLogger(".".join([__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        selected_points = []
        if self._get_args().selected_points:
            point_expected_format = re.compile("[0-9]+,[0-9]+")
            for point_string in self._get_args().selected_points:
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

    # TODO: this function is doing too much - split it!
    def get_focused_image(self):
        focusing_path = self._get_args().beamline_stack_path
        if "." not in focusing_path:
            files = []
            # Sort names according to creation time
            for file_name in listdir(focusing_path):
                name = join(focusing_path, file_name)
                files.append(file(name))
            files.sort(key=lambda x: getmtime(x.name))
            # Run focusstack
            stacker = FocusStack(files, self._get_args().config)
            focused_image = stacker.composite()
            focused_image.save(self._get_output_path())
        else:
            focused_image = Image(cv2.imread(focusing_path))

        return focused_image

    def get_formulatrix_image_path(self):
        return self._get_args().Formulatrix_image.name

    def get_focused_image_path(self):
        focusing_path = self._get_args().beamline_stack_path
        if "." not in focusing_path:
            focusing_path =  self._get_output_path()
        return abspath(focusing_path)

    def _get_output_path(self):
        output_path = abspath(self._get_args().output)
        self._process_dir_path(output_path)
        return output_path

    def get_to_json(self):
        return self._get_args().to_json

    def get_job_id(self):
        return self._get_args().job

    def _process_dir_path(self, path):
        output_dir, output_file = split(path)
        if output_dir is not "":
            if not (exists(output_dir) and isdir(output_dir)):
                makedirs(output_dir)
