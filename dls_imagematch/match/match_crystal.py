
from .match_feature import FeatureMatcher
from .aligned_images import AlignedImages
from dls_imagematch.util import Translate, Rectangle, Point


class CrystalMatcher:
    SEARCH_WIDTH = 200
    SEARCH_HEIGHT = 400

    def __init__(self):
        pass

    def match(self, aligned_images, img_a_rect):
        crystal_aligned = self._perform_match(aligned_images, img_a_rect)
        return crystal_aligned

    def _perform_match(self, aligned_images, img_a_rect):
        crystal_img_a = aligned_images.img_a.crop(img_a_rect)
        crystal_img_b, img_b_rect = self._make_image_b_region(aligned_images, img_a_rect)

        crystal_img_a_gray = crystal_img_a.to_mono()
        crystal_img_b_gray = crystal_img_b.to_mono()

        method = "Consensus"
        adapt = 'Pyramid'

        FeatureMatcher.POPUP_RESULTS = True
        matcher = FeatureMatcher(crystal_img_b_gray, crystal_img_a_gray)
        matcher.match(method, adapt)

        crystal_translate = matcher.net_transform
        position = Translate(img_b_rect.x1, img_b_rect.y1)
        position = position.offset(crystal_translate)

        img_b = aligned_images.img_b
        crystal_aligned = AlignedImages(img_b, crystal_img_a, position)
        return crystal_aligned

    def _make_image_b_region(self, aligned_images, img_a_rect):
        img_b = aligned_images.img_b

        # Find the center of the rectangle in image A, convert to image B coords
        center_a = img_a_rect.center()
        center_b = center_a - aligned_images.pixel_offset()

        # Determine size (in pixels) of the search box in image B
        width = self.SEARCH_WIDTH / img_b.pixel_size
        height = self.SEARCH_HEIGHT / img_b.pixel_size

        # Create a rectangle area of image B in which to search
        # Its tall because crystal likely to move downwards under gravity
        top_left = center_b - Point(width/2, width/2)
        rect = Rectangle.from_corner(top_left, width, height)

        rect = rect.intersection(img_b.bounds())
        region = img_b.crop(rect)
        return region, rect
