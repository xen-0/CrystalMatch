from __future__ import division

import cv2
import numpy as np
from itertools import izip

from dls_imagematch.util import Point
from dls_imagematch.match.transformation import Transformation
from dls_imagematch.match.translation import Translation


class MatchHomographyCalculator:
    """ For explanation of homography calculation and definition of methods, see:
    http://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#findhomography

    The method RANSAC can handle practically any ratio of outliers but it needs a threshold to distinguish
    inliers from outliers. The method LMeDS does not need any threshold but it works correctly only when
    there are more than 50% of inliers. Finally, if there are no outliers and the noise is rather small,
    use the default method (method=0).
    """
    _MIN_HOMOGRAPHY_MATCHES = 4

    _DEFAULT_RANSAC_THRESHOLD = 5.0

    INCLUDE_ALL = 0
    RANSAC = cv2.RANSAC
    LMEDS = cv2.LMEDS

    METHOD_NAMES = ["LMEDS", "RANSAC", "Include All"]
    METHOD_VALUES = [LMEDS, RANSAC, INCLUDE_ALL]

    def __init__(self):
        self._mark_unused = True
        self._translation_only = False
        self._method = self.RANSAC
        self._ransac_threshold = self._DEFAULT_RANSAC_THRESHOLD

    def set_translation_only(self, translation_only):
        self._translation_only = translation_only

    def set_mark_unused(self, mark_unused):
        self._mark_unused = mark_unused

    def set_homography_method(self, method):
        if method not in self.METHOD_VALUES:
            raise ValueError("Not a valid homography method")

        self._method = method

    def set_ransac_threshold(self, threshold):
        self._ransac_threshold = threshold

    def calculate_transform(self, matches):
        can_do_transform = self._has_enough_matches_for_full_transform(matches)

        if self._translation_only or not can_do_transform:
            transform = self._calculate_median_translation(matches)
        else:
            homography, mask = self._calculate_homography(matches)
            transform = Transformation(homography)
            if self._mark_unused:
                self._mark_unused_matches(matches, mask)

        return transform

    @staticmethod
    def _calculate_median_translation(matches):
        """ For a set of feature matches between two images, find the average (median) translation that maps
        one image to the other. """
        deltas = [m.point2() - m.point1() for m in matches]
        x = -np.median([d.x for d in deltas])
        y = -np.median([d.y for d in deltas])
        point = Point(x, y)

        return Translation(point)

    def _calculate_homography(self, matches):
        homography = None

        if self._has_enough_matches_for_full_transform(matches):
            img1_pts = [m.point1().tuple() for m in matches]
            img1_pts = np.float32(img1_pts).reshape(-1, 1, 2)
            img2_pts = [m.point2().tuple() for m in matches]
            img2_pts = np.float32(img2_pts).reshape(-1, 1, 2)

            homography, mask = cv2.findHomography(img1_pts, img2_pts, self._method, self._ransac_threshold)

        return homography, mask

    def _has_enough_matches_for_full_transform(self, matches):
        return len(matches) >= self._MIN_HOMOGRAPHY_MATCHES

    @staticmethod
    def _mark_unused_matches(matches, mask):
        for match, mask in izip(matches, mask):
            if not mask:
                match.remove_from_transformation()
