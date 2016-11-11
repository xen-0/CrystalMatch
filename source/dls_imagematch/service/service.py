import logging
from sys import stdout

from dls_imagematch.crystal.align import AlignConfig
from dls_imagematch.crystal.align import ImageAligner
from dls_imagematch.crystal.align.aligned_images import ALIGNED_IMAGE_STATUS_OK
from dls_imagematch.crystal.align.settings import SettingsConfig
from dls_imagematch.crystal.match import CrystalMatchConfig
from dls_imagematch.crystal.match import CrystalMatcher
from dls_imagematch.feature.detector import DetectorConfig
from dls_imagematch.feature.draw import MatchPainter
from dls_imagematch.service.service_result import ServiceResult
from dls_util.imaging import Image


class CrystalMatchService:
    def __init__(self, config_directory, verbose=False, debug=False, scale_override=None):
        """
        Create a Crystal Matching Service object using the configuration parameters provided.
        :param config_directory: Path to the configuration directory.
        :param verbose: Activates verbose logging to std_out.
        :param debug: Activates debugging logging to std_out - overrides verbose mode.
        :param scale_override: Optional override for the pixel sizes of both images - can be None or a
        tuple of the form: ([formulatrix image pixel size], [beam line image pixel size])
        """
        self._config_directory = config_directory

        self._config_settings = SettingsConfig(config_directory)
        self._config_detector = DetectorConfig(config_directory)
        self._config_align = AlignConfig(config_directory, scale_override=scale_override)
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

    def perform_match(self, formulatrix_image_path, beamline_image_path, input_poi, job_id=None, json_output=False):
        """
        Perform image alignment and crystal matching returning a results object.
        :param job_id: Optional parameter for command line - returned in results to identify the run.
        :param formulatrix_image_path: File path to the 'before' image from the Formulatrix.
        :param beamline_image_path: File path to the 'after' image from the Beam line.
        :param input_poi: An array of points of interest to match between the images.
        :param json_output: Option to output a json object to std_out instead.
        :return: ServiceResult object.
        """
        # Create the images
        image1 = Image.from_file(formulatrix_image_path)
        image2 = Image.from_file(beamline_image_path)

        # Create results object
        service_result = ServiceResult(job_id, formulatrix_image_path, beamline_image_path, json_output=json_output)

        # Perform alignment
        try:
            aligned_images, scaled_poi = self._perform_alignment(image1, image2, input_poi)
            service_result.set_image_alignment_results(aligned_images)

            # Perform Crystal Matching - only proceed if we have a valid alignment
            if aligned_images.alignment_status_code() == ALIGNED_IMAGE_STATUS_OK:
                match_results = self._perform_matching(aligned_images, scaled_poi)
                service_result.append_crystal_matching_results(match_results)
        except Exception as e:
            logging.error("ERROR: " + e.message)
            service_result.set_err_state(e)

        return service_result

    def _perform_alignment(self, formulatrix_image, beamline_image, formulatrix_points):
        """
        Perform alignment on the two images, returning an AlignedImages object. As the formulatrix image will be
        scaled the formulatrix_points will alos be scaled to map to the new resolution.
        :param formulatrix_image: image on which points are selected (this will be resized)
        :param beamline_image: image onto which points are projected
        :param formulatrix_points: points on the formulatrix image - these will be rescaled along
        with the formulatrix_image
        :return: An AlignedImages object and a scaled array of formulatrix points.
        """
        aligner = ImageAligner(formulatrix_image, beamline_image, self._config_align, self._config_detector)
        aligned_images = aligner.align()
        scaled_formulatrix_points = aligner.scale_points(formulatrix_points)
        self._log_alignment_status(aligned_images)

        return aligned_images, scaled_formulatrix_points

    def _perform_matching(self, aligned_images, selected_points):
        matcher = CrystalMatcher(aligned_images, self._config_detector)
        matcher.set_from_crystal_config(self._config_crystal)

        crystal_match_results = matcher.match(selected_points)
        logging.info("Crystal Matching Complete")
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
            logging.debug("- Matching Time: {:.4f}".format(match_result.time_match()))
            logging.debug("- Transform Time: {:.4f}".format(match_result.time_transform()))

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
