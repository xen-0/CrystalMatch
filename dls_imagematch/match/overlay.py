import cv2

from dls_imagematch.util import Image, Rectangle, Point


class Overlayer:
    @staticmethod
    def create_overlay_image(img_a, img_b, transform):
        """ For the two images, A and B, where the position of B is offset from that of A, overlay
        image B onto image A at the appropriate position. The overlaid area will ve a blending of the
        two images. A rectangle will be drawn around the area.
        """
        # Make a copy of A, the background image
        background = img_a.copy()

        # Get overlapping regions of images
        offset = transform.to_point()
        overlap_a, overlap_b = Overlayer.get_overlap_regions(img_a, img_b, offset)
        if overlap_a is None or overlap_b is None:
            return background

        # Blend the two overlapping regions
        perc_a, perc_b = 0.5, 0.5
        blended = cv2.addWeighted(overlap_a.img, perc_a, overlap_b.img, perc_b, 0)
        background.paste(Image(blended), xOff=max(offset.x, 0), yOff=max(offset.y, 0))

        # Define the rectangle that will be pasted to the background image
        w, h = img_b.size
        rect = Rectangle.from_corner(offset, w, h)
        background.draw_rectangle(rect)

        return background

    @staticmethod
    def get_overlap_regions(img_a, img_b, offset):
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
        rect_a = img_a.bounds()
        rect_b = img_b.bounds().offset(offset)
        overlap_a_rect = rect_a.intersection(rect_b)
        overlap_a = img_a.sub_image(overlap_a_rect)

        rect_a = img_a.bounds().offset(-offset)
        rect_b = img_b.bounds()
        overlap_b_rect = rect_a.intersection(rect_b)
        overlap_b = img_b.sub_image(overlap_b_rect)

        return overlap_a, overlap_b
