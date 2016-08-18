
from .exception import FeatureDetectorError

from .detector import DetectorType
from .detector.detector import Detector
from .detector.detector_orb import OrbDetector


class DetectorFactory:
    @staticmethod
    def create(type, options=None):
        if type not in DetectorType.LIST_ALL:
            raise FeatureDetectorError("Unknown detector type: {}".format(type))

        if type == DetectorType.ORB:
            detector = OrbDetector()
        else:
            detector = Detector(detector=type)

        return detector

    @staticmethod
    def get_all_detectors():
        detectors = []

        for det in DetectorType.LIST_ALL:
            detector = DetectorFactory.create(det)
            detectors.append(detector)
        return detectors
