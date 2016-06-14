import cv2

from .exception import FeatureMatchException

_OPENCV_VERSION_ERROR = "Under Windows, this function only works correctly under OpenCV v2 (with Python 2.7) " \
                        "and not under OpenCV v3. This is a widely known and reported problem but it doesn't " \
                        "seem to have been fixed yet. Install Python 2.7 with OpenCV 2.4 and try again."


class FeatureDetector:
    _DETECTOR_TYPES = ["ORB", "SIFT", "SURF", "BRISK", "FAST", "STAR", "MSER", "GFTT", "HARRIS", "Consensus", "Dense", "SimpleBlob"]
    _ADAPTATION_TYPE = ["", "Grid", "Pyramid"]
    _CONSENSUS_DETECTORS = ["ORB", "SIFT", "SURF", "BRISK", "FAST", "STAR", "MSER", "GFTT", "HARRIS"]

    def __init__(self, detector=_DETECTOR_TYPES[0], adaptation=_ADAPTATION_TYPE[0]):

        if detector not in self._DETECTOR_TYPES:
            raise ValueError("No such feature matching detector available: " + detector)
        elif adaptation not in self._ADAPTATION_TYPE:
            raise ValueError("No such feature matching adaptation available: " + adaptation)

        self.detector = str(detector)
        self.adaptation = str(adaptation)

    def normalization_type(self):
        if self.detector in ["SIFT", "SURF"]:
            return cv2.NORM_L2
        else:
            return cv2.NORM_HAMMING

    def is_consensus_type(self):
        return self.detector == "Consensus"

    def detect_features(self, img):
        """ Detect interesting features in the image and generate descriptors. A keypoint identifies the
        location and orientation of a feature, and a descriptor is a vector of numbers that describe the
        various attributes of the feature. By generating descriptors, we can compare the set of features
        on two images and find matches between them.
        """
        detector = self._create_detector()
        extractor = self._create_extractor()

        keypoints = detector.detect(img.img, None)
        keypoints, descriptors = extractor.compute(img.img, keypoints)

        if descriptors is None:
            keypoints, descriptors = [], []
        return keypoints, descriptors

    def _create_detector(self):
        name = self.adaptation + self.detector
        try:
            detector = cv2.FeatureDetector_create(name)
        except AttributeError:
            raise FeatureMatchException(_OPENCV_VERSION_ERROR)
        return detector

    def _create_extractor(self):
        # Sift, Surf, and Orb have their own descriptor extraction methods.
        name = "BRIEF"
        if self.detector in ["SIFT", "SURF", "ORB"]:
            name = self.detector

        try:
            extractor = cv2.DescriptorExtractor_create(name)
        except AttributeError:
            raise FeatureMatchException(_OPENCV_VERSION_ERROR)
        return extractor

    @staticmethod
    def get_consensus_methods(adaptation):
        detectors = []
        for det in FeatureDetector._CONSENSUS_DETECTORS:
            method = FeatureDetector(det, adaptation)
            detectors.append(method)

        return detectors

    @staticmethod
    def types():
        return FeatureDetector._DETECTOR_TYPES

    @staticmethod
    def adaptations():
        return FeatureDetector._ADAPTATION_TYPE
