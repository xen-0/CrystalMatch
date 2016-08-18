
from .exception import FeatureDetectorError

from .detectors import DetectorType
from .detectors.detector import Detector


class DetectorFactory:
    @staticmethod
    def create(type, options=None):
        if type not in DetectorType.LIST_ALL:
            raise FeatureDetectorError("Unknown detector type: {}".format(type))

        detector = Detector(detector=type)

        return detector

    @staticmethod
    def get_all_detectors():
        detectors = []

        for det in DetectorType.LIST_ALL:
            detector = DetectorFactory.create(det)
            detectors.append(detector)
        return detectors
