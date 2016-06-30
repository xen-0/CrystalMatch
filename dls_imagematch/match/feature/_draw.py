from __future__ import division

import cv2

from dls_imagematch.util import Point, Image, Color


class FeaturePainter:
    MAX_IMAGE_SIZE = 900

    @staticmethod
    def draw_matches(img1, img2, matches, highlight_matches=[]):
        """ Implementation of a function that is available in OpenCV 3 but not in OpenCV 2.
        Makes an image that is a side-by-side of the two images, with detected features highlighted and lines
        drawn between matching features in the two images.
        """
        PAD = 5

        # Create a new output image that concatenates the two images together
        w1, h1 = img1.size
        w2, h2 = img2.size
        img1_pos, img2_pos = Point(PAD, PAD), Point(2*PAD + w1, PAD)

        # vertical center for img1
        if h2 > h1:
            img1_pos = Point(PAD, PAD + 0.5*(h2-h1))

        out = Image.blank(w1+w2+3*PAD, 2*PAD + max(h1, h2))
        out.paste(img1, img1_pos)
        out.paste(img2, img2_pos)

        out, factor = FeaturePainter._rescale_to_max_size(out)

        # For each pair of points we have between both images draw circles, then connect a line between them
        for match in matches:
            point1 = (match.img_point1() + img1_pos) * factor
            point2 = (match.img_point2() + img2_pos) * factor
            # Draw a small circle at both co-ordinates
            out.draw_circle(point=point1, radius=4, color=Color.Blue(), thickness=1)
            out.draw_circle(point=point2, radius=4, color=Color.Blue(), thickness=1)

            # Draw a line between the two points
            out.draw_line(point1, point2, color=Color.Blue(), thickness=1)

        for match in highlight_matches:
            point1 = (match.img_point1() + img1_pos) * factor
            point2 = (match.img_point2() + img2_pos) * factor
            # Draw a small circle at both co-ordinates
            out.draw_circle(point=point1, radius=4, color=Color.Yellow(), thickness=2)
            out.draw_circle(point=point2, radius=4, color=Color.Yellow(), thickness=2)

            # Draw a line between the two points
            out.draw_line(point1, point2, color=Color.Yellow(), thickness=2)

        return out

    @staticmethod
    def _rescale_to_max_size(image, max_size=MAX_IMAGE_SIZE):
        width, height = image.width, image.height
        factor = max_size / max(width, height)
        rescaled = image.rescale(factor)
        return rescaled, factor

    @staticmethod
    def draw_keypoints(img, keypoints):
        """ Draw the list of keypoints to the specified image and display it as a popup window. """
        marked_img = cv2.drawKeypoints(img.img, keypoints, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return Image(marked_img)