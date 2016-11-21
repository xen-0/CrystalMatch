import logging
from logging import DEBUG, INFO
from logging.handlers import TimedRotatingFileHandler
from sys import stdout

from os import chmod

from dls_imagematch.crystal.align import AlignConfig
from dls_imagematch.crystal.align import ImageAligner
from dls_imagematch.crystal.align.aligned_images import ALIGNED_IMAGE_STATUS_OK
from dls_imagematch.crystal.align.settings import SettingsConfig
from dls_imagematch.crystal.match import CrystalMatchConfig
from dls_imagematch.crystal.match import CrystalMatcher
from dls_imagematch.feature.detector import DetectorConfig
from dls_imagematch.service.service_result import ServiceResult
from dls_util.imaging import Image


class CrystalMatchService:
    def __init__(self, config_directory, log_dir=None, verbose=False, debug=False, scale_override=None):
        """
        Create a Crystal Matching Service object using the configuration parameters provided.
        :param config_directory: Path to the configuration directory.
        :param log_dir: Path override for the log directory.
        :param verbose: Activates verbose logging to std_out.
        :param debug: Activates debugging logging to std_out - overrides verbose mode.
        :param scale_override: Optional override for the pixel sizes of both images - can be None or a
        tuple of the form: ([formulatrix image pixel size], [beam line image pixel size])
        """
        self._config_directory = config_directory

        self._config_settings = SettingsConfig(config_directory, log_dir=log_dir)
        self._config_detector = DetectorConfig(config_directory)
        self._config_align = AlignConfig(config_directory, scale_override=scale_override)
        self._config_crystal = CrystalMatchConfig(config_directory)

        self._set_up_logging(debug, verbose)

    def _set_up_logging(self, debug, verbose):
        # Set up logging
        root_logger = logging.getLogger()
        root_logger.setLevel(DEBUG)
        # Set up stream handler
        if debug:
            self.get_log_stream_handler(DEBUG, root_logger)
        elif verbose:
            self.get_log_stream_handler(INFO, root_logger)
        # Set up file handler
        if self._config_settings.logging.value():
            self.get_log_file_handler(root_logger)

    def get_log_file_handler(self, logger):
        log_file_path = self._config_settings.get_log_file_path()
        try:
            log_file_handler = TimedRotatingFileHandler(log_file_path,
                                                        when=self._config_settings.log_rotation.value(),
                                                        backupCount=self._config_settings.log_count_limit.value())
            log_file_handler.setLevel(self._config_settings.get_log_level())
            # TODO: Add job ID to log format
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            log_file_handler.setFormatter(formatter)
            chmod(log_file_path, 0666)
            logger.addHandler(log_file_handler)
        except IOError:
            logging.error("ERROR: Could not access log file - please check permissions: " + log_file_path)

    @staticmethod
    def get_log_stream_handler(level, logger):
        stream_handler = logging.StreamHandler(stdout)
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)
        if level == DEBUG:
            logging.debug("DEBUG statements visible.")
        elif level == INFO:
            logging.info("INFO statements visible.")

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
        service_result = ServiceResult(job_id, formulatrix_image_path, beamline_image_path, self._config_settings,
                                       json_output=json_output)

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

    def _get_image_output_dir(self):
        image_output_dir = None
        if self._config_settings.log_images.value():
            image_output_dir = self._config_settings.get_image_log_dir()
        return image_output_dir

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
