from __future__ import division

from .match_results import CrystalMatchResults, _CrystalMatch
from ..feature import BoundedFeatureMatcher, FeatureMatchException
from dls_imagematch.util import Rectangle, Point


class CrystalMatcher:
    def __init__(self, config):
        self._config = config

    def match(self, aligned_images, selected_img1_points, region_size):

        img1 = aligned_images.img1.to_mono()
        img2 = aligned_images.img2.to_mono()
        pixel_size = img1.pixel_size

        match_results = CrystalMatchResults(aligned_images)

        for point in selected_img1_points:
            img1_rect = self.make_target_region(point, region_size)
            img2_rect = self.make_search_region(aligned_images, point)

            matcher = BoundedFeatureMatcher(img1, img2, img1_rect, img2_rect)
            result = _CrystalMatch(point, pixel_size)
            self._perform_match(matcher, result)
            match_results.matches.append(result)

        return match_results

    def make_target_region(self, center, region_size):
        return Rectangle.from_center(center, region_size, region_size)

    def make_search_region(self, aligned_images, img1_point):
        """ Define a rectangle on image B in which to search for the matching crystal. Its narrow and tall
        as the crystal is likely to move downwards under the effect of gravity. """
        pixel_size = aligned_images.img1.pixel_size
        search_width, search_height = self._search_size(pixel_size)

        img2_point = img1_point - aligned_images.pixel_offset()
        top_left = img2_point - Point(search_width/2, search_height/4)
        rect = Rectangle.from_corner(top_left, search_width, search_height)

        rect = rect.intersection(aligned_images.img2.bounds())
        return rect

    def _search_size(self, pixel_size):
        width = self._config.search_width.value() / pixel_size
        height = self._config.search_height.value() / pixel_size
        return width, height

    @staticmethod
    def _perform_match(matcher, crystal_match):
        try:
            matcher.set_detector("Consensus")
            transform = matcher.match()
            crystal_match.set_transformation(transform)
        except FeatureMatchException:
            pass

