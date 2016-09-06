from __future__ import division

from util import Rectangle, Point
from feature import BoundedFeatureMatcher
from .results import CrystalMatcherResults
from .match import CrystalMatch


class CrystalMatcher:
    DEFAULT_REGION_SIZE = 100
    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 400
    DEFAULT_VERTICAL_SHIFT = 0.75

    def __init__(self, aligned_images, detector_config, crystal_config=None):
        self._aligned_images = aligned_images
        self._image1 = aligned_images.image1.to_mono()
        self._image2 = aligned_images.image2.to_mono()
        self._pixel_size = self._image1.pixel_size()

        self._region_size_real = self.DEFAULT_REGION_SIZE
        self._search_width_real = self.DEFAULT_WIDTH
        self._search_height_real = self.DEFAULT_HEIGHT
        self._search_vertical_shift = self.DEFAULT_VERTICAL_SHIFT
        self._transform_method = None
        self._transform_filter = None

        self._detector_config = detector_config
        if crystal_config is not None:
            self.set_from_crystal_config(crystal_config)

    # -------- CONFIGURATION -------------------
    def set_from_crystal_config(self, config):
        self._region_size_real = config.region_size.value()
        self._search_width_real = config.search_width.value()
        self._search_height_real = config.search_height.value()
        self._search_vertical_shift = config.vertical_shift.value()
        self._transform_method = config.transform_method.value()
        self._transform_filter = config.transform_filter.value()

    def set_detector_config(self, config):
        self._detector_config = config

    def set_real_region_size(self, size):
        self._region_size_real = size

    def set_real_search_size(self, width, height):
        self._search_width_real = width
        self._search_height_real = height

    def set_search_shift(self, value):
        self._search_vertical_shift = value

    def set_transform_method(self, method):
        self._transform_method = method

    def set_transform_filter(self, filter):
        self._transform_filter = filter

    # -------- FUNCTIONALITY -------------------
    def match(self, image1_points):
        images = self._aligned_images
        match_results = CrystalMatcherResults(images)

        for point in image1_points:
            result = self._match_single_point(point)
            match_results.matches.append(result)

        return match_results

    def _match_single_point(self, point):
        image1_rect = self.make_target_region(point)
        image2_rect = self.make_search_region(point)

        feature_matcher = BoundedFeatureMatcher(self._image1, self._image2, self._detector_config,
                                                image1_rect, image2_rect)

        result = CrystalMatch(point, self._pixel_size)
        self._perform_match(feature_matcher, result)

        return result

    def _perform_match(self, feature_matcher, crystal_match):
        feature_matcher.set_use_all_detectors()
        feature_matcher.set_transform_method(self._transform_method)
        feature_matcher.set_transform_filter(self._transform_filter)

        result = feature_matcher.match()
        crystal_match.set_feature_match_result(result)

    def make_target_region(self, center):
        size = self._region_size_pixels()
        return Rectangle.from_center(center, size, size)

    def make_search_region(self, image1_point):
        """ Define a rectangle on image B in which to search for the matching crystal. Its narrow and tall
        as the crystal is likely to move downwards under the effect of gravity. """
        images = self._aligned_images
        search_width, search_height = self._search_size_pixels()
        vertical_shift = self._search_vertical_shift

        image2_point = image1_point - images.pixel_offset()
        top_left = image2_point - Point(search_width/2, search_height*(1-vertical_shift))
        rect = Rectangle.from_corner(top_left, search_width, search_height)

        rect = rect.intersection(images.image2.bounds())
        return rect

    def _region_size_pixels(self):
        return self._region_size_real / self._pixel_size

    def _search_size_pixels(self):
        width = self._search_width_real / self._pixel_size
        height = self._search_height_real / self._pixel_size
        return width, height
