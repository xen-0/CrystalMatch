from __future__ import division

import cv2
import numpy as np

from dls_imagematch.util import Point
from dls_imagematch.match.transformation import Transformation

from .exception import FeatureMatchException
from ._single_match import SingleFeatureMatch
from .detector import FeatureDetector


class FeatureMatcher:
    """ Use feature matching to compare to images and align the second on the first.

    Note this only works correctly under OpenCV v2. Under v3, the function 'orb.detectAndCompute()'
    does not work properly for Python - it incorrectly raises an exception. This is a widely known
    and reported problem but it doesn't seem to have been fixed yet.
    """
    _MIN_MATCHES = 1
    _MAX_MATCHES = 200

    def __init__(self, img1, img2, img1_rect=None, img2_rect=None):
        """ Feature Matching between two images. If rectangular regions are provided, the routine will
        only consider features in those regions. """
        self._detector = FeatureDetector()

        if img1_rect is None:
            img1_rect = img1.bounds()

        if img2_rect is None:
            img2_rect = img2.bounds()

        self.img1 = img1.crop(img1_rect)
        self.img2 = img2.crop(img2_rect)

        self.img1_offset = img1_rect.top_left()
        self.img2_offset = img2_rect.top_left()

    def set_detector(self, method, adaptation=""):
        self._detector = FeatureDetector(method, adaptation)

    def match(self):
        """ Perform a feature matching operation between the two selected images (or image regions if
        specified. The resulting transformation can be applied to a point in Image/Region 1 coordinates
        to map it to its matching point in Image 2 coordinates.
        """
        matches = self._find_matches()
        transform = self._calculate_full_transform(matches)
        return transform

    def match_translation_only(self):
        matches = self._find_matches()
        transform = self._calculate_translation_only_transform(matches)
        return transform

    def _find_matches(self):
        if self._detector.is_consensus_type():
            matches = self._find_matches_for_consensus()
        else:
            matches = self._find_matches_for_method(self._detector)

        # Check that we have actually found some features
        min_matches = self._MIN_MATCHES
        if len(matches) < min_matches:
            message = "Could not find the required minimum number of matches ({})!".format(min_matches)
            raise FeatureMatchException(message)

        return matches

    def _find_matches_for_consensus(self):
        """ Perform feature matching for each method in the consensus list, and aggregate the match results."""
        matches = []
        for method in FeatureDetector.get_consensus_methods(self._detector.adaptation):
            try:
                method_matches = self._find_matches_for_method(method)
                matches.extend(method_matches)
            except FeatureMatchException:
                pass

        return matches

    def _find_matches_for_method(self, method):
        keypoints1, descriptors1 = method.detect_features(self.img1)
        keypoints2, descriptors2 = method.detect_features(self.img2)

        raw_matches = self._brute_force_match(method, descriptors1, descriptors2)
        matches = SingleFeatureMatch.matches_from_raw(raw_matches, keypoints1, keypoints2)
        return matches

    def _brute_force_match(self, method, descriptors_1, descriptors_2):
        """ For two sets of feature descriptors generated from 2 images, attempt to find all the matches,
        i.e. find features that occur in both images.
        """
        # TODO: Try out a FLANN based matcher
        if len(descriptors_1) == 0 or len(descriptors_2) == 0:
            return []

        matcher = cv2.BFMatcher(method.normalization_type(), crossCheck=True)
        matches = matcher.match(descriptors_1, descriptors_2)
        top_matches = sorted(matches, key=lambda x: x.distance)[:self._MAX_MATCHES]

        return top_matches

    def _calculate_translation_only_transform(self, matches):
        translation = self._calculate_median_translation(matches)
        return Transformation(translation, None)

    def _calculate_full_transform(self, matches):
        translation = self._calculate_median_translation(matches)
        homography = self._calculate_homography(matches)
        return Transformation(translation, homography)

    def _calculate_median_translation(self, matches):
        """ For a set of feature matches between two images, find the average (median) translation that maps
        one image to the other.
        """
        deltas = []
        for match in matches:
            point1 = match.point1() + self.img1_offset
            point2 = match.point2() + self.img2_offset
            delta = point2 - point1
            deltas.append(delta)

        # Get median result
        x = -np.median([d.x for d in deltas])
        y = -np.median([d.y for d in deltas])

        return Point(x, y)

    def _calculate_homography(self, matches):
        """ See:
        http://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#findhomography

        The method RANSAC can handle practically any ratio of outliers but it needs a threshold to distinguish
        inliers from outliers. The method LMeDS does not need any threshold but it works correctly only when
        there are more than 50% of inliers. Finally, if there are no outliers and the noise is rather small,
        use the default method (method=0).
        """
        homography = None

        if len(matches) >= 4:
            img1_pts = [m.point1() + self.img1_offset for m in matches]
            img1_pts = np.float32([p.tuple() for p in img1_pts]).reshape(-1, 1, 2)
            img2_pts = [m.point2() + self.img2_offset for m in matches]
            img2_pts = np.float32([p.tuple() for p in img2_pts]).reshape(-1, 1, 2)

            homography, mask = cv2.findHomography(img1_pts, img2_pts, cv2.LMEDS)
            pts = np.float32([[0, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, homography)

        return homography
