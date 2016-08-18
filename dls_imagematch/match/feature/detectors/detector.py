import cv2

from .feature import Feature
from ..exception import OpenCvVersionError, FeatureMatchException

_OPENCV_VERSION_ERROR = "Under Windows, this function only works correctly under OpenCV v2 (with Python 2.7) " \
                        "and not under OpenCV v3. This is a widely known and reported problem but it doesn't " \
                        "seem to have been fixed yet. Install Python 2.7 with OpenCV 2.4 and try again."


class Detector:
    """ Uses OpenCV algorithms to detect interesting features in an image and quantify them with an
    array of numerical descriptors.

    A range of different detector methods are available, each with different properties. Each detector
    may work more effectively on some images than on others.
    """
    # Detector Types
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

    DETECTOR_TYPES = [DET_ORB, DET_SIFT, DET_SURF, DET_BRISK, DET_FAST, DET_STAR, DET_MSER,
                      DET_GFTT, DET_HARRIS, DET_DENSE, DET_BLOB]

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

    def __init__(self, detector=DEFAULT_DETECTOR):
        """ Supply a detector name to use that detector with all its default parameters. """
        if detector not in self.DETECTOR_TYPES:
            raise FeatureMatchException("No such feature matching detector available: " + detector)

        self._detector = detector
        self._adaptation = self.DEFAULT_ADAPTATION
        self._extractor = self._default_extractor(detector)
        self._normalization = self._default_normalization(detector)

    # -------- ACCESSORS -----------------------
    def detector(self):
        return self._detector

    def adaptation(self):
        return self._adaptation

    def extractor(self):
        return self._extractor

    def normalization(self):
        return self._normalization

    # -------- CONFIGURATION ------------------
    def set_adaptation(self, adaptation):
        if adaptation not in self.ADAPTATION_TYPES:
            raise FeatureMatchException("No such feature matching adaptation available: " + adaptation)
        self._adaptation = adaptation

    # -------- FUNCTIONALITY -------------------
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

        features = []
        if descriptors is None:
            return features

        for kp, descriptor in zip(keypoints, descriptors):
            feature = Feature(kp, descriptor)
            features.append(feature)

        return features

    def _create_detector(self):
        return self._create_default_detector(self._detector, self._adaptation)

    def _create_extractor(self):
        return self._create_default_extractor(self._extractor)

    @staticmethod
    def get_all_default_detectors():
        detectors = []
        for det in Detector.DETECTOR_TYPES:
            method = Detector(det)
            detectors.append(method)
        return detectors

    @staticmethod
    def _default_extractor(detector_name):
        """ SIFT, SURF, and ORB have their own descriptor extraction methods. All others use the BRIEF
        extractor."""
        det = Detector
        name = det.EXT_BRIEF
        if detector_name in [det.DET_ORB, det.DET_SIFT, det.DET_SURF]:
            name = detector_name
        return name

    @staticmethod
    def _default_normalization(detector):
        """ Keypoint normalization type for the detector method; used for matching. """
        if detector in [Detector.DET_SIFT, Detector.DET_SURF]:
            return cv2.NORM_L2
        else:
            return cv2.NORM_HAMMING

    @staticmethod
    def _create_default_detector(detector, adaptation):
        """ Create a detector of the specified type with all the default parameters"""
        name = adaptation + detector
        try:
            detector = cv2.FeatureDetector_create(name)
        except AttributeError:
            raise OpenCvVersionError(_OPENCV_VERSION_ERROR)
        return detector

    @staticmethod
    def _create_default_extractor(extractor):
        """ Note: SIFT descriptors for a keypoint are an array of 128 integers; SURF descriptors are an
        array of 64 floats (in range -1 to 1); all others are arrays of 32 ints (in range 0 to 255. """
        try:
            extractor = cv2.DescriptorExtractor_create(extractor)
        except AttributeError:
            raise OpenCvVersionError(_OPENCV_VERSION_ERROR)
        return extractor
