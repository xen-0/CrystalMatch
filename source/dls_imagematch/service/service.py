import logging
from sys import stdout

from dls_imagematch.crystal.align import AlignConfig
from dls_imagematch.crystal.align import ImageAligner
from dls_imagematch.crystal.align.aligned_images import ALIGNED_IMAGE_STATUS_OK
from dls_imagematch.crystal.match import CrystalMatchConfig
from dls_imagematch.crystal.match import CrystalMatcher
from dls_imagematch.feature.detector import DetectorConfig
from dls_imagematch.feature.draw import MatchPainter
from dls_imagematch.service.service_result import ServiceResult
from dls_util.imaging import Image


class CrystalMatchService:
    def __init__(self, config_directory, verbose=False, debug=False):
        self._config_directory = config_directory

        self._config_detector = DetectorConfig(config_directory)
        self._config_align = AlignConfig(config_directory)
        self._config_crystal = CrystalMatchConfig(config_directory)

        # Set up logging
        if debug:
            self.set_std_out_log_level(logging.DEBUG)
            logging.debug("DEBUG mode set")
        elif verbose:
            self.set_std_out_log_level(logging.INFO)
            logging.info("VERBOSE mode set")

    @staticmethod
    def set_std_out_log_level(level):
        root = logging.getLogger()
        root.setLevel(level)
        ch = logging.StreamHandler(stdout)
        ch.setLevel(level)
        # TODO: Add file logging using format below
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # ch.setFormatter(formatter)
        root.addHandler(ch)

    def perform_match(self, formulatrix_image_path, beamline_image_path, selected_points, job_id=None):
        """
        Perform image alignment and crystal matching returning a results object.
        :param job_id: Optional parameter for command line - returned in results to identify the run.
        :param formulatrix_image_path: File path to the 'before' image from the Formulatrix.
        :param beamline_image_path: File path to the 'after' image from the Beam line.
        :param selected_points: An array of points to match between the images.
        :return: ServiceResult object.
        """
        # Create the images
        image1 = Image.from_file(formulatrix_image_path)
        image2 = Image.from_file(beamline_image_path)

        # Create results object
        service_result = ServiceResult(job_id, formulatrix_image_path, beamline_image_path)

        # Perform alignment
        aligned_images = self._perform_alignment(image1, image2)
        service_result.set_image_alignment_results(aligned_images)

        # Perform Crystal Matching - only proceed if we have a valid alignment
        if aligned_images.alignment_status_code() == ALIGNED_IMAGE_STATUS_OK:
            # Remap points onto image B
            # TODO: refactor transform - use alignment transform object?
            sf, tr = aligned_images.get_alignment_transform()
            if sf != 1.0:
                for i in range(len(selected_points)):
                    selected_points[i] = selected_points[i] * sf
                    # selected_points[i] = selected_points[i] + tr
            match_results = self._perform_matching(aligned_images, selected_points)
            service_result.append_crystal_matching_results(match_results)
        return service_result

    def _perform_alignment(self, formulatrix_image, beamline_image):
        """ Perform alignment on the two images, returning an AlignedImages object. """
        aligner = ImageAligner(formulatrix_image, beamline_image, self._config_align, self._config_detector)
        aligned_images = aligner.align()
        self._log_alignment_status(aligned_images)

        return aligned_images

    def _perform_matching(self, aligned_images, selected_points):
        matcher = CrystalMatcher(aligned_images, self._config_detector)
        matcher.set_from_crystal_config(self._config_crystal)

        crystal_match_results = matcher.match(selected_points)
        self._log_match_results(crystal_match_results)
        # self._popup_match_results(crystal_match_results)

        return crystal_match_results

    @staticmethod
    def _log_alignment_status(aligned):
        status = "Unknown"

        if aligned.is_alignment_good():
            status = "Good Alignment"
        elif aligned.is_alignment_poor():
            status = "Poor Alignment"
        elif aligned.is_alignment_bad():
            status = "Alignment failed!"

        logging.info("Image Alignment Completed - Status: '{}' (Score={:.2f})".format(status, aligned.overlap_metric()))

        match_result = aligned.feature_match_result
        if match_result is not None:
            logging.info("- Matching Time: {:.4f}".format(match_result.time_match()))
            logging.info("- Transform Time: {:.4f}".format(match_result.time_transform()))

    @staticmethod
    def _log_match_results(crystal_results):
        logging.info("Crystal Matching Complete")

        for i, crystal_match in enumerate(crystal_results.get_matches()):
            logging.info("*** Crystal Match {} ***".format(i+1))
            if not crystal_match.is_success():
                logging.info("-- Match Failed")
                continue

            # Matching time
            feature_result = crystal_match.feature_match_result()
            logging.info("- Matching Time: {:.4f}".format(feature_result.time_match()))
            logging.info("- Transform Time: {:.4f}".format(feature_result.time_transform()))

            # Beam position and movement
            pixel1, real1 = crystal_match.get_poi_image_1(), crystal_match.get_poi_image_1_real()
            pixel2, real2 = crystal_match.get_poi_image_2_matched(), crystal_match.get_poi_image_2_matched_real()

            beam_position = "- Beam Position: x={0:.2f} um, y={1:.2f} um ({2} px, " \
                            "{3} px)".format(real2.x, real2.y, int(round(pixel2.x)), int(round(pixel2.y)))

            delta_pixel = pixel2 - pixel1 - crystal_results.pixel_offset()
            delta_real = real2 - real1 - crystal_results.pixel_offset()
            delta = "- Crystal Movement(actual): x={0:.2f} um, y={1:.2f} um ({2} px, " \
                    "{3} px)".format(delta_real.x, delta_real.y, int(round(delta_pixel.x)), int(round(delta_pixel.y)))

            logging.info(beam_position)
            logging.info(delta)

    @staticmethod
    def _popup_match_results(results):
        for i in range(results.num()):
            feature_match_result = results.get_crystal_match(i).feature_match_result()

            painter = MatchPainter(feature_match_result.image1(), feature_match_result.image2())

            image = painter.background_image()
            # image = painter.draw_transform_shapes(self._quad1, self._quad2, image)
            image = painter.draw_matches(feature_match_result.good_matches(), [], image)
            # image = painter.draw_transform_points(self._image1_point, self._image2_point, image)
            image.popup()
