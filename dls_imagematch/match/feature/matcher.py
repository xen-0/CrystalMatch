from __future__ import division

import cv2

from .transform_calc import TransformCalculator, TransformCalculationError
from .result import FeatureMatchResult

from .match import SingleFeatureMatch
from .detector import FeatureDetector


class FeatureMatcher:
    """ Use feature matching to compare two images and align the second on the first.

    Performs a feature matching operation between the two selected images. The resulting
    transformation can be applied to a point in Image/Region 1 coordinates to map it to
    its matching point in Image 2 coordinates.

    Note this only works correctly under OpenCV v2. Under v3, the function 'orb.detectAndCompute()'
    does not work properly for Python - it incorrectly raises an exception. This is a widely known
    and reported problem but it doesn't seem to have been fixed yet.
    """
    _MAX_MATCHES = 200
    _DEFAULT_TRANSFORM = TransformCalculator.DEFAULT_METHOD
    _DEFAULT_FILTER = TransformCalculator.DEFAULT_FILTER

    def __init__(self, img1, img2):
        self._detector = FeatureDetector()
        self._transform_method = self._DEFAULT_TRANSFORM
        self._transform_filter = self._DEFAULT_FILTER

        self._keypoint_distance_filter = None

        self.img1 = img1
        self.img2 = img2

    # -------- CONFIGURATION -------------------
    def set_detector(self, method, adaptation=""):
        self._detector = FeatureDetector(method, adaptation)

    def set_transform_method(self, method):
        if method is None:
            self._transform_method = self._DEFAULT_TRANSFORM
        else:
            self._transform_method = method

    def set_transform_filter(self, filter):
        if filter is None:
            self._transform_filter = self._DEFAULT_FILTER
        else:
            self._transform_filter = filter

    def set_keypoint_distance_filter(self, distance_filter):
        self._keypoint_distance_filter = distance_filter

    # -------- FUNCTIONALITY -------------------
    def match(self):
        matches = self._find_matches()

        calc = TransformCalculator()
        calc.set_method(self._transform_method)
        calc.set_filter(self._transform_filter)

        try:
            transform = calc.calculate_transform(matches)
        except TransformCalculationError:
            transform = None

        return self._create_result_object(matches, transform)

    def match_translation_only(self):
        self.set_transform_method(TransformCalculator.TRANSLATION)
        return self.match()

    def _create_result_object(self, matches, transform):
        result = FeatureMatchResult(self.img1, self.img2, matches, transform)
        result.method = self._detector.detector
        result.method_adapt = self._detector.adaptation
        return result

    def _find_matches(self):
        if self._detector.is_consensus_type():
            matches = self._find_matches_for_consensus()
        else:
            matches = self._find_matches_for_method(self._detector)

        return matches

    def _find_matches_for_consensus(self):
        matches = []
        for method in FeatureDetector.get_consensus_methods(self._detector.adaptation):
            method_matches = self._find_matches_for_method(method)
            matches.extend(method_matches)

        return matches

    def _find_matches_for_method(self, method):
        keypoints1, descriptors1 = method.detect_features(self.img1)
        keypoints2, descriptors2 = method.detect_features(self.img2)

        raw_matches = self._brute_force_match(method, descriptors1, descriptors2)
        matches = self._matches_from_raw(raw_matches, keypoints1, keypoints2, method)
        matches = self._filter_matches(matches)
        return matches

    def _matches_from_raw(self, raw_matches, keypoints1, keypoints2, method):
        matches = SingleFeatureMatch.from_cv2_matches(raw_matches, keypoints1, keypoints2, method)
        return matches

    def _filter_matches(self, matches):
        if self._keypoint_distance_filter is not None:
            matches = self._keypoint_distance_filter.filter(matches)
        return matches

    def _brute_force_match(self, method, descriptors_1, descriptors_2):
        """ For two sets of feature descriptors generated from 2 images, attempt to find all the matches,
        i.e. find features that occur in both images. """
        # TODO: Try out a FLANN based matcher
        if len(descriptors_1) == 0 or len(descriptors_2) == 0:
            return []

        matcher = cv2.BFMatcher(method.normalization_type(), crossCheck=True)
        matches = matcher.match(descriptors_1, descriptors_2)
        top_matches = sorted(matches, key=lambda x: x.distance)[:self._MAX_MATCHES]

        return top_matches
