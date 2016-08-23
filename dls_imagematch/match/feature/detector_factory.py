from .exception import FeatureDetectorError

from .detector import DetectorType
from .detector.detector import Detector
from .detector.detector_orb import OrbDetector
from .detector.detector_sift import SiftDetector
from .detector.detector_surf import SurfDetector
from .detector.detector_mser import MserDetector
from .detector.detector_brisk import BriskDetector


class DetectorFactory:
    @staticmethod
    def create(type, options=None):
        if type not in DetectorType.LIST_ALL:
            raise FeatureDetectorError("Unknown detector type: {}".format(type))

        if type == DetectorType.ORB:
            detector = OrbDetector()
        elif type == DetectorType.SIFT:
            detector = SiftDetector()
        elif type == DetectorType.SURF:
            detector = SurfDetector()
        elif type == DetectorType.MSER:
            detector = MserDetector()
        elif type == DetectorType.BRISK:
            detector = BriskDetector()
        else:
            detector = Detector(detector=type)

        if options is not None:
            detector_options = options.get_detector_options(type)
            detector.set_from_config(detector_options)

        return detector

    @staticmethod
    def get_all_detectors(options=None):
        detectors = []

        for det in DetectorType.LIST_ALL:
            detector = DetectorFactory.create(det, options)
            detectors.append(detector)
        return detectors

    @staticmethod
    def get_all_free_detectors(options=None):
        detectors = []

        for det in DetectorType.LIST_FREE:
            detector = DetectorFactory.create(det, options)
            detectors.append(detector)
        return detectors
