from __future__ import division

from .match_results import CrystalMatchResults
from .single_match_result import SingleCrystalMatch
from ..feature import BoundedFeatureMatcher, FeatureMatchException
from dls_imagematch.util import Rectangle, Point


class CrystalMatcher:
    DEFAULT_REGION_SIZE = 50
    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 400

    def __init__(self, aligned_images):
        self._aligned_images = aligned_images
        self._img1 = aligned_images.img1.to_mono()
        self._img2 = aligned_images.img2.to_mono()
        self._pixel_size = self._img1.pixel_size

        self._region_size_real = self.DEFAULT_REGION_SIZE
        self._search_width_real = self.DEFAULT_WIDTH
        self._search_height_real = self.DEFAULT_HEIGHT
        self._transform_method = None
        self._transform_filter = None

    # -------- CONFIGURATION -------------------
    def set_real_region_size(self, size):
        self._region_size_real = size

    def set_real_search_size(self, width, height):
        self._search_width_real = width
        self._search_height_real = height

    def set_transform_method(self, method):
        self._transform_method = method

    def set_transform_filter(self, filter):
        self._transform_filter = filter

    # -------- FUNCTIONALITY -------------------
    def match(self, img1_points):
        images = self._aligned_images
        match_results = CrystalMatchResults(images)

        for point in img1_points:
            result = self._match_single_point(point)
            match_results.matches.append(result)

        return match_results

    def _match_single_point(self, point):
        img1_rect = self.make_target_region(point)
        img2_rect = self.make_search_region(point)

        feature_matcher = BoundedFeatureMatcher(self._img1, self._img2, img1_rect, img2_rect)
        result = SingleCrystalMatch(point, self._pixel_size)
        self._perform_match(feature_matcher, result)

        return result

    def _perform_match(self, feature_matcher, crystal_match):
        try:
            feature_matcher.set_detector("Consensus")
            feature_matcher.set_transform_method(self._transform_method)
            feature_matcher.set_transform_filter(self._transform_filter)

            result = feature_matcher.match()
            crystal_match.set_feature_match_result(result)
        except FeatureMatchException:
            pass

    def make_target_region(self, center):
        size = self._region_size_pixels()
        return Rectangle.from_center(center, size, size)

    def make_search_region(self, img1_point):
        """ Define a rectangle on image B in which to search for the matching crystal. Its narrow and tall
        as the crystal is likely to move downwards under the effect of gravity. """
        images = self._aligned_images
        search_width, search_height = self._search_size_pixels()

        img2_point = img1_point - images.pixel_offset()
        top_left = img2_point - Point(search_width/2, search_height/4)
        rect = Rectangle.from_corner(top_left, search_width, search_height)

        rect = rect.intersection(images.img2.bounds())
        return rect

    def _region_size_pixels(self):
        return self._region_size_real / self._pixel_size

    def _search_size_pixels(self):
        width = self._search_width_real / self._pixel_size
        height = self._search_height_real / self._pixel_size
        return width, height
