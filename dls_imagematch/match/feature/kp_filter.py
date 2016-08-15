from .detector import FeatureDetector


class KeypointDistanceFilter:
    def __init__(self):
        self._brief_max = 100
        self._orb_max = 100
        self._surf_max = 100
        self._sift_max = 100

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

    @staticmethod
    def _check_value( value):
        if value < 1 or value > 100:
            raise ValueError("Keypoint distance filter value must be between 1 and 100 inclusive")

    def filter(self, matches):
        good_matches = []

        for match in matches:
            extractor = FeatureDetector.get_extractor_name(match.method())
            if extractor == FeatureDetector.EXT_SURF:
                limit = 0.01 * self._surf_max
            elif extractor == FeatureDetector.EXT_SIFT:
                limit = 10 * self._sift_max
            elif extractor == FeatureDetector.EXT_ORB:
                limit = self._orb_max
            elif extractor == FeatureDetector.EXT_BRIEF:
                limit = self._brief_max

            if match.distance() <= limit:
                good_matches.append(match)

        return good_matches
