from __future__ import division

from ..feature import BoundedFeatureMatcher, FeatureMatchException
from dls_imagematch.util import Rectangle, Point


class CrystalMatcher:
    def __init__(self, config):
        self._config = config

    def match(self, crystal_match_set, region_size):
        img1 = crystal_match_set.img1().to_mono()
        img2 = crystal_match_set.img2().to_mono()

        for crystal_match in crystal_match_set.matches:
            img1_rect = crystal_match.img1_region(region_size)
            img2_rect = self.make_search_region(crystal_match_set, crystal_match)

            matcher = BoundedFeatureMatcher(img1, img2, img1_rect, img2_rect)
            self._perform_match(matcher, crystal_match)

    def make_search_region(self, xtal_match_set, xtal_match):
        """ Define a rectangle on image B in which to search for the matching crystal. Its narrow and tall
        as the crystal is likely to move downwards under the effect of gravity. """
        pixel_size = xtal_match.pixel_size()
        search_width, search_height = self._search_size(pixel_size)

        img2_point = xtal_match.img1_point() - xtal_match_set.pixel_offset()
        top_left = img2_point - Point(search_width/2, search_height/4)
        rect = Rectangle.from_corner(top_left, search_width, search_height)

        rect = rect.intersection(xtal_match_set.img2().bounds())
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

