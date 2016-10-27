from __future__ import print_function

import logging

from dls_imagematch.crystal.align.aligned_images import ALIGNED_IMAGE_STATUS_NOT_SET
from dls_util.shape.point import Point


class ServiceResult:
    """
    NOTE: This should be the only class allowed to print() to the console - elsewhere use logging.
    Results class which determines the format and structure of output reported to the console. This is also intended to
    standardise the handling of errors for the wrapper service.
    """
    def __init__(self, job_id, formulatrix_image_path, beamline_image_path):
        self.SEPARATOR = " ; "
        self._job_id = job_id
        self._image_path_formulatrix = formulatrix_image_path
        self._image_path_beamline = beamline_image_path
        self._alignment_transform = None
        self._alignment_status_code = ALIGNED_IMAGE_STATUS_NOT_SET
        self._alignment_error = 0.0
        self._match_results = []

    def set_image_alignment_results(self, aligned_images):
        """
        Harvest the output data from an image alignment operation.
        :param aligned_images: An AlignedImages object.
        :return:
        """
        self._alignment_transform = aligned_images.pixel_offset()
        self._alignment_status_code = aligned_images.alignment_status_code()
        self._alignment_error = aligned_images.overlap_metric()

    def append_crystal_matching_results(self, crystal_matcher_results):
        """
        Append any CrystalMatch objects from a CrystalMatcherResults object into an internal array - necessary when
        performing multiple passes of the algorithm or when farming points out to multiple processes.
        :param crystal_matcher_results: CrystalMatcherResults object.
        """
        self._match_results = self._match_results + crystal_matcher_results.get_matches()

    def _print_alignment_transform(self):
        if self._alignment_transform is None:
            return str(Point(0, 0))
        return str(self._alignment_transform)

    def _print_crystal_match_results(self, output_list):
        if len(self._match_results) > 0:
            output_list.append("\nco-ordinates ; transform ; status ; mean error")
        for crystal_match in self._match_results:
            line = "poi:"
            line += str(crystal_match.get_transformed_point()) + self.SEPARATOR
            line += str(crystal_match.get_delta()) + self.SEPARATOR
            line += str(crystal_match.get_status()) + self.SEPARATOR
            line += str(crystal_match.feature_match_result().mean_transform_error())
            output_list.append(line)

    def print_results(self):
        """
        Print the contents of this results object to the console.
        """
        output = ['job_id:"' + self._job_id + '"',
                  'input_image:"' + self._image_path_formulatrix + '"',
                  'output_image:"' + self._image_path_beamline + '"',
                  'align_transform:' + self._print_alignment_transform(),
                  'align_status:' + str(self._alignment_status_code),
                  'align_error:' + str(self._alignment_error)
                  ]

        self._print_crystal_match_results(output)

        # Print separately to log file and console
        logging.info("\n*************************************\nRESULTS\n")
        for log_msg in output:
            logging.info(log_msg)
        logging.info("\n*************************************\n")
        for line in output:
            print(line)
