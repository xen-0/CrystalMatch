from feature import FeatureMatcher
from util.shape import Point
from .aligned_images import AlignedImages
from .exception import ImageAlignmentError


class ImageAligner:
    def __init__(self, img1, img2, align_config=None, detector_config=None):
        self._img1 = img1
        self._img2 = img2

        self._align_config = align_config
        self._detector_config = detector_config

    # -------- CONFIGURATION -------------------
    def set_align_config(self, config):
        self._align_config = config

    def set_detector_config(self, config):
        self._detector_config = config

    # -------- FUNCTIONALITY -------------------
    def align(self):
        """ Perform image alignment, returning an AlignedImages object. """
        self._check_config()

        if not self._align_config.use_alignment.value():
            return self._default_alignment()

        detector = self._get_detector()
        match_result = self._perform_match(detector)
        aligned_images = self._generate_alignment(match_result, detector)

        return aligned_images

    def _default_alignment(self):
        """ Default alignment result with 0 offset. """
        translation = Point()
        description = "DISABLED!"
        return AlignedImages(self._img1, self._img2, translation, self._align_config, description)

    def _check_config(self):
        """ Raises an exception if configuration has not been properly set. """
        if self._align_config is None:
            raise ImageAlignmentError("Must set Alignment config before performing alignment")
        elif self._detector_config is None:
            raise ImageAlignmentError("Must set Detector config before performing alignment")

    def _get_detector(self):
        """ Get the selected detector and raise and exception if it is disabled. """
        detector = self._align_config.align_detector.value()
        enabled = self._detector_config.is_detector_enabled(detector)
        if not enabled:
            raise ImageAlignmentError("Cannot perform image alignment as detector '{}' is disabled.".format(detector))

        return detector

    def _perform_match(self, detector):
        """ Perform feature matching between the two images. """
        img1, img2 = self._get_scaled_mono_images()
        matcher = FeatureMatcher(img1, img2, self._detector_config)
        matcher.set_detector(detector)
        match_result = matcher.match_translation_only()
        return match_result

    def _generate_alignment(self, match_result, detector):
        """ Generate a translation that maps image 2 to image 1 based on the feature match results. """
        if not match_result.has_transform():
            raise ImageAlignmentError("Image Alignment failed - no matches found.")

        translation = match_result.transform().translation()
        description = "Feature matching - " + detector
        aligned_images = AlignedImages(self._img1, self._img2, translation, self._align_config, description)
        return aligned_images

    def _get_scaled_mono_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Resize image B so it has the same size per pixel as image A
        factor = self._img2.pixel_size / self._img1.pixel_size

        if factor != 1:
            self._img2 = self._img2.rescale(factor)

        return self._img1.to_mono(), self._img2.to_mono()
