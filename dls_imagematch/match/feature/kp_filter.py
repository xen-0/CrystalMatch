from .exception import KeypointFilterError
from .detectors.detector import Detector


class KeypointDistanceFilter:
    """ Allows filtering to be applied to a list of feature matches that filters based on the match's
    keypoint distance. For each image keypoint (feature), a list of descriptors is generated. This is a
    list of numerical values that describe the feature.

    When finding matches, the matching algorithm examines each feature from one image and finds the feature
    that is most like it in the other image. This 'likeness' is calculated as the distance between the two
    features' descriptor vectors and so is a measure of how good the match is.

    This class allows the user to set limits on the maximum keypoint distance that is acceptable for a
    match to be considered valid. Matches that exceed this distance are excluded. This serves as an excellent
    first pass to easily filter out obviously bad matches, and so can significantly reduce the time required
    to calculate a transformation.

    There are multiple methods which can be used to describe the keypoint (i.e., to generate a descriptor
    vector) but the typical keypoint distances for each method fall in different ranges.

    Roughly:
    ORB: 10 - 100
    SURF: 0.2 - 1
    SIFT: 100 - 500
    BRIEF: 10 - 100

    We limit the range of acceptable values for each method from 1-100 and then for SIFT and SURF, we just
    multiply the value by a constant factor to get it in the correct range.
    """
    _FACTOR_SURF = 0.01
    _FACTOR_SIFT = 10

    _RANGE_MIN = 1
    _RANGE_MAX = 100
    
    _DEFAULT_VALUE = 50

    def __init__(self):
        default = self._DEFAULT_VALUE
        self._brief_max = default
        self._orb_max = default
        self._surf_max = default
        self._sift_max = default

    def set_orb_max(self, value):
        self._check_value(value)
        self._orb_max = value

    def set_surf_max(self, value):
        self._check_value(value)
        self._surf_max = value

    def set_sift_max(self, value):
        self._check_value(value)
        self._sift_max = value

    def set_brief_max(self, value):
        self._check_value(value)
        self._brief_max = value

    def _check_value(self, value):
        if value < self._RANGE_MIN or value > self._RANGE_MAX:
            raise KeypointFilterError("Keypoint distance filter value must be between 1 and 100 inclusive")

    def filter(self, detector, matches):
        good_matches = []

        for match in matches:
            extractor = detector.extractor()
            if extractor == Detector.EXT_SURF:
                limit = self._surf_max * self._FACTOR_SURF
            elif extractor == Detector.EXT_SIFT:
                limit = self._sift_max * self._FACTOR_SIFT
            elif extractor == Detector.EXT_ORB:
                limit = self._orb_max
            elif extractor == Detector.EXT_BRIEF:
                limit = self._brief_max

            if match.distance() <= limit:
                good_matches.append(match)

        return good_matches
