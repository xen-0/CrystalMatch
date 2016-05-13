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

        # Determine offset amount
        x, y = int(transform.x), int(transform.y)

        # Get overlapping regions of images
        overlap_a, overlap_b = Overlayer.get_overlap_regions(img_a, img_b, (x, y))
        if overlap_a is None or overlap_b is None:
            return background

        # Blend the two overlapping regions
        perc_a, perc_b = 0.5, 0.5
        blended = cv2.addWeighted(overlap_a, perc_a, overlap_b, perc_b, 0)
        background.paste(Image(blended), xOff=max(x, 0), yOff=max(y, 0))

        # Define the rectangle that will be pasted to the background image
        w, h = img_b.size
        rect = Rectangle.from_corner(Point(x, y), w, h)
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
        # Determine size of images
        width_a, height_a = img_a.size
        width_b, height_b = img_b.size

        # Corners (top-left, bottom-right) of the overlap rectangle for image A
        x_off, y_off = offset
        x1_a = max(x_off, 0)
        y1_a = max(y_off, 0)
        x2_a = min(x_off+width_b, width_a)
        y2_a = min(y_off+height_b, height_a)

        # Corners of the overlap rectangle for image B
        x1_b = x1_a - x_off
        y1_b = y1_a - y_off
        x2_b = x2_a - x_off
        y2_b = y2_a - y_off

        # Error if paste location is totally outside image
        if x1_a > x2_a or y1_a > y2_a:
            return None, None

        # Get overlap sections of each image
        overlap_a = img_a.img[y1_a:y2_a, x1_a:x2_a]
        overlap_b = img_b.img[y1_b:y2_b, x1_b:x2_b]

        return overlap_a, overlap_b
