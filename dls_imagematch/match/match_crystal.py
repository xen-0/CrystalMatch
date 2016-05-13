
from .match_feature import FeatureMatcher
from .aligned_images import AlignedImages
from dls_imagematch.util import Translate, Rectangle


class CrystalMatcher:
    SEARCH_WIDTH = 200
    SEARCH_HEIGHT = 400

    def __init__(self):
        pass

    def match(self, aligned_images, img_a_rect):
        crystal_aligned = self._perform_match(aligned_images, img_a_rect)
        return crystal_aligned

    def _perform_match(self, aligned_images, img_a_rect):
        crystal_img_a = aligned_images.img_a.sub_image(img_a_rect)
        crystal_img_b, img_b_rect = self._make_image_b_region(aligned_images, img_a_rect)

        crystal_img_a_gray = crystal_img_a.make_gray()
        crystal_img_b_gray = crystal_img_b.make_gray()

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
        align_offset = aligned_images.pixel_offset()
        img_b = aligned_images.img_b

        # Find the center of the rectangle in image A
        center_a = img_a_rect.center()

        # Convert the center to Image B coordinates
        center_b = center_a[0] - align_offset[0], center_a[1] - align_offset[1]

        # Determine size (in pixels) of the search box in image B
        width = self.SEARCH_WIDTH / img_b.pixel_size
        height = self.SEARCH_HEIGHT / img_b.pixel_size

        # Create a rectangle area of image B in which to search
        # Its tall because crystal likely to move downwards under gravity
        x1 = center_b[0] - (width / 2.0)
        y1 = center_b[1] - (width / 2.0)
        rect = Rectangle.from_corner(x1, y1, width, height)

        rect = rect.intersection(img_b.bounds())
        region = img_b.sub_image(rect)
        return region, rect
