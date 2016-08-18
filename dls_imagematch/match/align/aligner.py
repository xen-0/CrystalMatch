from ..feature.detector import Detector
from ..feature import FeatureMatcher
from .aligned_images import AlignedImages
from .exception import ImageAlignmentError


class ImageAligner:
    _DEFAULT_DETECTOR = Detector.DEFAULT_DETECTOR
    _DEFAULT_ADAPTATION = Detector.DEFAULT_ADAPTATION

    def __init__(self, img1, img2):
        self._img1 = img1
        self._img2 = img2

        self._detector = self._DEFAULT_DETECTOR
        self._adaptation = self._DEFAULT_ADAPTATION

    # -------- CONFIGURATION -------------------
    def set_detector_type(self, detector):
        if detector is None:
            self._detector = self._DEFAULT_DETECTOR
        else:
            self._detector = detector

    def set_adaptation_type(self, adaptation):
        if adaptation is None:
            self._adaptation = self._DEFAULT_ADAPTATION
        else:
            self._adaptation = adaptation

    # -------- FUNCTIONALITY -------------------
    def align(self):
        img1, img2 = self._get_scaled_mono_images()

        matcher = FeatureMatcher(img1, img2)
        matcher.set_detector(self._detector, self._adaptation)

        match_result = matcher.match_translation_only()

        if not match_result.has_transform():
            raise ImageAlignmentError("Image Alignment failed - no matches found")

        translation = match_result.transform.translation()
        description = self._get_method_description()
        aligned_images = AlignedImages(self._img1, self._img2, translation, description)

        return aligned_images

    def _get_scaled_mono_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Resize image B so it has the same size per pixel as image A
        factor = self._img2.pixel_size / self._img1.pixel_size

        if factor != 1:
            self._img2 = self._img2.rescale(factor)

        return self._img1.to_mono(), self._img2.to_mono()

    def _get_method_description(self):
        description = "Feature matching - " + self._detector
        if self._adaptation != '':
            description += " with " + self._adaptation

        return description
