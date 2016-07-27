from __future__ import division

import cv2
import numpy as np

from dls_imagematch.util import Point
from ..transform import HomographyTransformation, Translation, AffineTransformation


class TransformCalculator:
    """ For a set of matches which map points between two images, this class finds the approximate
    transformation that will map any point in the first image to the equivalent point in the second.
    The transformation can include translation, rotation, scale, and skew components.

    Clients can choose from four different methods:
    * INCLUDE_ALL - the transform will be calculated using all of the matches. This will
        be less reliable if there are many outliers.
    * LMEDS - uses the least median of squares method to automatically cull outliers. This method
        only works correctly when > 50% of matches are inliers.
    * RANSAC - uses the random sample consensus method to cull outliers. This uses an error threshold
        to distinguish outliers from inliers (can be set by the client).
    * TRANSLATION - calculate a translation only transformation by simply taking the median x and y
        components of the matches.

    Note: at least 4 matches are required to calculate a full transformation. If there are fewer than
    this, the class will fall back on the TRANSLATION method.

    If the 'mark unused' flag is set, the methods LMEDS and RANSAC will mark any outlier match objects
    as being unused.

    For more information on homography calculation and definition of methods, see:
    http://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#findhomography
    """
    TRANSLATION = 0
    HOMO_INCLUDE_ALL = 1
    HOMO_RANSAC = 2
    HOMO_LMEDS = 3
    AFFINE_FULL = 4
    AFFINE_RIGID = 5

    METHOD_NAMES = ["Affine - Full (6 DoF)", "Affine - Rigid (5 DoF)", "Homography - RANSAC",
                    "Homography - LMEDS", "Homography - Include All", "Average Translation"]

    METHOD_VALUES = [AFFINE_FULL, AFFINE_RIGID, HOMO_RANSAC,
                     HOMO_LMEDS, HOMO_INCLUDE_ALL, TRANSLATION]

    RANSAC_METHODS = [HOMO_RANSAC]
    HOMO_METHODS = [HOMO_RANSAC, HOMO_LMEDS, HOMO_INCLUDE_ALL]
    AFFINE_METHODS = [AFFINE_FULL, AFFINE_RIGID]

    _MIN_TRANSFORM_MATCHES = 4
    _DEFAULT_METHOD = HOMO_RANSAC
    _DEFAULT_RANSAC_THRESHOLD = 5.0

    @staticmethod
    def METHOD_FROM_NAME(name):
        index = TransformCalculator.METHOD_NAMES.index(name)
        return TransformCalculator.METHOD_VALUES[index]

    def __init__(self):
        self._method = self._DEFAULT_METHOD
        self._ransac_threshold = self._DEFAULT_RANSAC_THRESHOLD
        self._use_pre_filter = False

    # -------- CONFIGURATION -------------------
    def set_homography_method(self, method):
        if method is None:
            self._method = self._DEFAULT_METHOD
        elif method in self.METHOD_NAMES:
            self._method = self.METHOD_FROM_NAME(method)
        elif method in self.METHOD_VALUES:
            self._method = method
        else:
            raise ValueError("Not a valid homography method")

    def set_ransac_threshold(self, threshold):
        self._ransac_threshold = threshold

    def enable_pre_filter(self, enable):
        self._use_pre_filter = enable

    # -------- FUNCTIONALITY -------------------
    def calculate_transform(self, matches):
        method = self._method
        use_translation = method == self.TRANSLATION
        can_do_transform = self._has_enough_matches_for_transform(matches)

        if use_translation or not can_do_transform:
            transform, mask = self._calculate_median_translation(matches)
        elif method in self.HOMO_METHODS:
            transform, mask = self._calculate_homography_transform(matches)
        elif method in self.AFFINE_METHODS:
            transform, mask = self._calculate_affine_transform(matches)
        else:
            raise ValueError("Unrecognised method type")

        self._set_matches_reprojection_error(matches, transform)
        self._mark_unused_matches(matches, mask)

        return transform

    def _calculate_median_translation(self, matches):
        matches, mask = self._pre_filter(matches)

        deltas = [m.point2() - m.point1() for m in matches]
        x = -np.median([d.x for d in deltas])
        y = -np.median([d.y for d in deltas])
        point = Point(x, y)
        transform = Translation(point)

        return transform, mask

    def _calculate_homography_transform(self, matches):
        transform = None
        matches, mask = self._pre_filter(matches)

        if self._has_enough_matches_for_transform(matches):
            img1_pts, img2_pts = self._get_np_points(matches)
            homo_method = self.get_homography_method_code()

            homography, new_mask = cv2.findHomography(img1_pts, img2_pts, homo_method, self._ransac_threshold)
            mask = self._combine_masks(mask, new_mask)
            transform = HomographyTransformation(homography)

        return transform, mask

    def _calculate_affine_transform(self, matches):
        """ Note: internally, estimateRigidTransform uses some sort of RANSAC method as a filter, but with
        hardcoded (and not very good) parameters. """
        transform = None
        matches, mask = self._pre_filter(matches)

        if self._has_enough_matches_for_transform(matches):
            img1_pts, img2_pts = self._get_np_points(matches)
            use_full = self._method == self.AFFINE_FULL

            affine = cv2.estimateRigidTransform(img1_pts, img2_pts, fullAffine=use_full)
            affine = np.array([affine[0], affine[1], [0, 0, 1]], np.float32)
            transform = AffineTransformation(affine)

        return transform, mask

    def _has_enough_matches_for_transform(self, matches):
        return len(matches) >= self._MIN_TRANSFORM_MATCHES

    def _pre_filter(self, matches):
        mask = [True] * len(matches)

        if self._use_pre_filter:
            mask = self._make_pre_filter_mask(matches)
            matches = [m for (m, i) in zip(matches, mask) if i]

        return matches, mask

    def _make_pre_filter_mask(self, matches):
        mask = [True] * len(matches)

        if self._has_enough_matches_for_transform(matches):
            img1_pts, img2_pts = self._get_np_points(matches)
            _, mask = cv2.findHomography(img1_pts, img2_pts, cv2.RANSAC, self._ransac_threshold)
            mask = self._sanitize_mask(mask)

        return mask

    def get_homography_method_code(self):
        method = self._method

        if method == self.HOMO_INCLUDE_ALL:
            return 0
        elif method == self.HOMO_LMEDS:
            return cv2.LMEDS
        elif method == self.HOMO_RANSAC:
            return cv2.RANSAC
        else:
            return -1

    @staticmethod
    def _combine_masks(mask1, mask2):
        """ Create a new mask by combining the two masks. Mask 2 has a length equal to the number of True elements in
        Mask 1. Each element in Mask 2 corresponds to a True element in Mask 1"""
        total_mask = []
        j = 0
        for bit in mask1:
            total_mask.append(bit and mask2[j])
            if bit:
                j += 1

        return total_mask

    @staticmethod
    def _get_np_points(matches):
        img1_pts = [m.point1().tuple() for m in matches]
        img1_pts = np.float32(img1_pts).reshape(-1, 1, 2)
        img2_pts = [m.point2().tuple() for m in matches]
        img2_pts = np.float32(img2_pts).reshape(-1, 1, 2)
        return img1_pts, img2_pts

    @staticmethod
    def _sanitize_mask(mask):
        return [m in [1, [1], True] for m in mask]

    @staticmethod
    def _mark_unused_matches(matches, mask):
        mask = TransformCalculator._sanitize_mask(mask)
        for match, include in zip(matches, mask):
            match.set_in_transformation(include)

    @staticmethod
    def _set_matches_reprojection_error(matches, transform):
        point1s = [m.point1() for m in matches]
        projected_point2s = transform.transform_points(point1s)

        for i, match in enumerate(matches):
            match.set_point2_projected(projected_point2s[i])
