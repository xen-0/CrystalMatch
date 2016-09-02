from feature.detector import DetectorConfig
from feature import FeatureMatcher
from util.shape import Point
from .aligned_images import AlignedImages
from .exception import ImageAlignmentError


class ImageAligner:
    def __init__(self, img1, img2, config_dir):
        self._img1 = img1
        self._img2 = img2

        self._config = DetectorConfig(config_dir)

        self._detector = None

    # -------- CONFIGURATION -------------------
    def set_detector_type(self, detector):
        self._detector = detector

    # -------- FUNCTIONALITY -------------------
    def align(self):
        if self._detector is None:
            return self._default_alignment()

        img1, img2 = self._get_scaled_mono_images()

        matcher = FeatureMatcher(img1, img2, self._config)
        matcher.set_detector(self._detector)

        match_result = matcher.match_translation_only()

        if not match_result.has_transform():
            raise ImageAlignmentError("Image Alignment failed - no matches found. Is "
                                      "{} detector enabled?".format(self._detector))

        translation = match_result.transform.translation()
        description = "Feature matching - " + self._detector
        aligned_images = AlignedImages(self._img1, self._img2, translation, description)

        return aligned_images

    def _default_alignment(self):
        """ Default alignment result with 0 offset. """
        translation = Point()
        description = "DISABLED!"
        return AlignedImages(self._img1, self._img2, translation, description)

    def _get_scaled_mono_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Resize image B so it has the same size per pixel as image A
        factor = self._img2.pixel_size / self._img1.pixel_size

        if factor != 1:
            self._img2 = self._img2.rescale(factor)

        return self._img1.to_mono(), self._img2.to_mono()
