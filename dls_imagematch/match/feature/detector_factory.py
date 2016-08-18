
from .exception import FeatureDetectorError

from .detectors.detector import Detector


class DetectorFactory:
    @staticmethod
    def create(type, options=None):
        if type not in Detector.DETECTOR_TYPES:
            raise FeatureDetectorError("Unknown detector type: {}".format(type))

        detector = Detector(detector=type)

        return detector

    @staticmethod
    def get_all_detectors():
        return Detector.get_all_default_detectors()
