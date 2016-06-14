from __future__ import division

from dls_imagematch.match.feature.matcher import FeatureMatcher
from dls_imagematch.util import Rectangle, Point


class CrystalMatcher:

    def __init__(self, config):
        self._config = config

    def match(self, crystal_match_set, region_size):
        img1 = crystal_match_set.img1().to_mono()
        img2 = crystal_match_set.img2().to_mono()

        method = "Consensus"
        adapt = ''

        for crystal_match in crystal_match_set.matches:
            img1_rect = crystal_match.img1_region(region_size)
            img2_rect = self.make_image2_region(crystal_match_set.img2(),
                                                crystal_match_set.pixel_offset(), img1_rect)

            # TODO: Handle normal failure gracefully (i.e. not enough matches)
            matcher = FeatureMatcher(img1, img2, img1_rect, img2_rect)
            matcher.set_detector(method, adapt)
            transform = matcher.match()

            crystal_match.set_transformation(transform)

    def make_image2_region(self, img2, align_offset, img1_rect):
        # Find the center of the rectangle in image A, convert to image B coords
        center_a = img1_rect.center()
        center_b = center_a - align_offset

        # Determine size (in pixels) of the search box in image B
        width = self._config.search_width.value() / img2.pixel_size
        height = self._config.search_height.value() / img2.pixel_size

        # Create a rectangle area of image B in which to search
        # Its tall because crystal likely to move downwards under gravity
        top_left = center_b - Point(width/2, height/4)
        rect = Rectangle.from_corner(top_left, width, height)

        rect = rect.intersection(img2.bounds())
        return rect
