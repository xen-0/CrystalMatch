import cv2

from dls_imagematch.util import Image, Rectangle, Point, Color


class Overlayer:
    @staticmethod
    def create_overlay_image(img1, img2, offset, rect_color=Color.Black()):
        """ For the two images, A and B, where the position of B is offset from that of A, overlay
        image B onto image A at the appropriate position. The overlaid area will ve a blending of the
        two images. A rectangle will be drawn around the area.
        """
        # Make a copy of A, the background image
        background = img1.copy()

        # Get overlapping regions of images
        overlap_a, overlap_b = Overlayer.get_overlap_regions(img1, img2, offset)
        if overlap_a is None or overlap_b is None:
            return background

        # Blend the two overlapping regions
        # Todo: handle case where overlap doesn't work because images are different sizes
        perc_a, perc_b = 0.5, 0.5
        blended = cv2.addWeighted(overlap_a.img, perc_a, overlap_b.img, perc_b, 0)
        background.paste(Image(blended), Point(max(offset.x, 0), max(offset.y, 0)))
        background = background.to_channels(3)

        # Define the rectangle that will be pasted to the background image
        w, h = img2.size
        rect = Rectangle.from_corner(offset, w, h)
        background.draw_rectangle(rect, color=rect_color)

        return background

    @staticmethod
    def get_overlap_regions(img1, img2, offset):
        """ For the two images, A and B, where the position of B is offset from that of A,
        return two new images that are the overlapping segments of the original images.

        As a simple example, if image B is smaller than A and it is completely contained
        within the borders of the image A, then we will simply return the whole of image B,
        and the section of image A that it overlaps. e.g., if A is 100x100 pixels, B is
        14x14 pixels, and the offset is (x=20, y=30), then the returned section of A will
        be (20:34, 30:44).

        If image B only partially overlaps image A, only the overlapping sections of each
        are returned.
        """
        rect_a = img1.bounds()
        rect_b = img2.bounds().offset(offset)
        overlap_a_rect = rect_a.intersection(rect_b)
        overlap_a = img1.crop(overlap_a_rect)

        rect_a = img1.bounds().offset(-offset)
        rect_b = img2.bounds()
        overlap_b_rect = rect_a.intersection(rect_b)
        overlap_b = img2.crop(overlap_b_rect)

        return overlap_a, overlap_b