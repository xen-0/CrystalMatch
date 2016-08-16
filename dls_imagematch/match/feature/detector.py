import cv2

from .exception import OpenCvVersionError, FeatureMatchException

_OPENCV_VERSION_ERROR = "Under Windows, this function only works correctly under OpenCV v2 (with Python 2.7) " \
                        "and not under OpenCV v3. This is a widely known and reported problem but it doesn't " \
                        "seem to have been fixed yet. Install Python 2.7 with OpenCV 2.4 and try again."


class FeatureDetector:
    # Detector Types
    DET_CONSENSUS = "Consensus"
    DET_ORB = "ORB"
    DET_SIFT = "SIFT"
    DET_SURF = "SURF"
    DET_BRISK = "BRISK"
    DET_FAST = "FAST"
    DET_STAR = "STAR"
    DET_MSER = "MSER"
    DET_GFTT = "GFTT"
    DET_HARRIS = "HARRIS"
    DET_DENSE = "Dense"
    DET_BLOB = "SimpleBlob"

    DETECTOR_TYPES = [DET_ORB, DET_SIFT, DET_SURF, DET_BRISK, DET_FAST, DET_STAR, DET_MSER, DET_GFTT, DET_HARRIS,
                      DET_CONSENSUS, DET_DENSE, DET_BLOB]
    _CONSENSUS_DETECTORS = [DET_ORB, DET_SIFT, DET_SURF, DET_BRISK, DET_FAST, DET_STAR, DET_MSER, DET_GFTT, DET_HARRIS]

    # Adaptation Types
    ADAPT_NONE = ""
    ADAPT_GRID = "Grid"
    ADAPT_PYRAMID = "Pyramid"

    ADAPTATION_TYPES = [ADAPT_NONE, ADAPT_GRID, ADAPT_PYRAMID]

    # Extractor Types
    EXT_ORB = DET_ORB
    EXT_SURF = DET_SURF
    EXT_SIFT = DET_SIFT
    EXT_BRIEF = "BRIEF"

    # Defaults
    DEFAULT_DETECTOR = DETECTOR_TYPES[0]
    DEFAULT_ADAPTATION = ADAPTATION_TYPES[0]

    def __init__(self, detector=DEFAULT_DETECTOR, adaptation=DEFAULT_ADAPTATION):

        if detector not in self.DETECTOR_TYPES:
            raise FeatureMatchException("No such feature matching detector available: " + detector)
        elif adaptation not in self.ADAPTATION_TYPES:
            raise FeatureMatchException("No such feature matching adaptation available: " + adaptation)

        self.detector = str(detector)
        self.adaptation = str(adaptation)

    def normalization_type(self):
        """ Keypoint normalization type for the detector method; used for matching. """
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
            raise OpenCvVersionError(_OPENCV_VERSION_ERROR)
        return detector

    def _create_extractor(self):
        """ Note: SIFT descriptors for a keypoint are an array of 128 integers; SURF descriptors are an
        array of 64 floats (in range -1 to 1); all others are arrays of 32 ints (in range 0 to 255. """
        # Sift, Surf, and Orb have their own descriptor extraction methods.
        name = self.get_extractor_name(self.detector)

        try:
            extractor = cv2.DescriptorExtractor_create(name)
        except AttributeError:
            raise OpenCvVersionError(_OPENCV_VERSION_ERROR)
        return extractor

    @staticmethod
    def get_consensus_methods(adaptation):
        detectors = []
        for det in FeatureDetector._CONSENSUS_DETECTORS:
            method = FeatureDetector(det, adaptation)
            detectors.append(method)

        return detectors

    @staticmethod
    def get_extractor_name(detector_name):
        fd = FeatureDetector
        name = fd.EXT_BRIEF
        if detector_name in [fd.DET_ORB, fd.DET_SIFT, fd.DET_SURF]:
            name = detector_name
        return name

    @staticmethod
    def types():
        return FeatureDetector.DETECTOR_TYPES

    @staticmethod
    def adaptations():
        return FeatureDetector.ADAPTATION_TYPES
