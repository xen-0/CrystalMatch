from .exception import FeatureDetectorError

from .types import DetectorType
from .detector import Detector
from .detector_orb import OrbDetector
from .detector_sift import SiftDetector
from .detector_surf import SurfDetector
from .detector_mser import MserDetector
from .detector_brisk import BriskDetector


class DetectorFactory:
    @staticmethod
    def create(det_type, options=None):
        if det_type not in DetectorType.LIST_ALL:
            raise FeatureDetectorError("Unknown detector type: {}".format(det_type))

        if det_type == DetectorType.ORB:
            detector = OrbDetector()
        elif det_type == DetectorType.SIFT:
            detector = SiftDetector()
        elif det_type == DetectorType.SURF:
            detector = SurfDetector()
        # elif type == DetectorType.MSER:
        #     detector = MserDetector()
        elif det_type == DetectorType.BRISK:
            detector = BriskDetector()
        else:
            detector = Detector(detector=det_type)

        if options is not None:
            detector_options = options.get_detector_options(det_type)
            detector.set_from_config(detector_options)

        if detector.is_non_free():
            default_options = options.get_default_options()
            use_non_free = default_options.use_non_free.value()
            if not use_non_free:
                detector.set_enabled(False)

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
