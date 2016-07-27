from __future__ import division

import cv2

from dls_imagematch.util import Point, Image, Color


class FeaturePainter:
    DEFAULT_IMAGE_SIZE = 900
    DEFAULT_PADDING = 5
    DEFAULT_BACK_COLOR = Color.Black()

    def __init__(self, img1, img2):
        self._img1 = img1
        self._img2 = img2

        self._img1_position = Point(0, 0)
        self._img2_position = Point(0, 0)
        self._scale_factor = 1
        self._background_image = None

        self._image_size = self.DEFAULT_IMAGE_SIZE
        self._padding = self.DEFAULT_PADDING
        self._back_color = self.DEFAULT_BACK_COLOR

        self._create_background_image()

    # -------- CONFIGURATION -------------------
    def set_image_size(self, size):
        self._image_size = size
        self._create_background_image()

    def set_padding(self, padding):
        self._padding = padding
        self._create_background_image()

    def set_back_color(self, color):
        self._back_color = color
        self._create_background_image()

    # -------- FUNCTIONALITY -------------------
    def background_image(self):
        return self._background_image.copy()

    def _create_background_image(self):
        self._calculate_image_positions()

        w, h = self._calculate_background_image_size()
        img = Image.blank(w, h)
        img.paste(self._img1, self._img1_position)
        img.paste(self._img2, self._img2_position)

        img, factor = self._rescale_to_max_size(img)
        self._background_image = img
        self._scale_factor = factor

    def _calculate_image_positions(self):
        pad = self._padding
        w1, h1 = self._img1.size
        w2, h2 = self._img2.size

        self._img1_position = Point(pad, pad)
        self._img2_position = Point(2 * pad + w1, pad)

        if h2 > h1:
            self._img1_position += Point(0, pad + 0.5*(h2-h1))
        elif h2 > h1:
            self._img2_position += Point(0, pad + 0.5*(h1-h2))

    def _calculate_background_image_size(self):
        pad = self._padding
        w1, h1 = self._img1.size
        w2, h2 = self._img2.size

        w_img = w1 + w2 + 3 * pad
        h_img = 2 * pad + max(h1, h2)
        return w_img, h_img

    def _rescale_to_max_size(self, image):
        width, height = image.width, image.height
        factor = self._image_size / max(width, height)
        rescaled = image.rescale(factor)
        return rescaled, factor

    def draw_transform_points(self, img1_point, img2_point, img=None):
        if img is None:
            img = self._background_image.copy()

        if img1_point is not None:
            point1 = self._point_to_img_coords(img1_point, 1)
            img.draw_cross(point1, Color.Green(), size=10, thickness=2)

        if img2_point is not None:
            point2 = self._point_to_img_coords(img2_point, 2)
            img.draw_cross(point2, Color.Green(), size=10, thickness=2)

        return img

    def draw_transform_quads(self, quad1, quad2, img=None):
        if img is None:
            img = self._background_image.copy()

        f1 = lambda x: self._point_to_img_coords(x, 1)
        f2 = lambda x: self._point_to_img_coords(x, 2)

        img.draw_line(f2(quad2[0]), f2(quad2[1]), Color.Orange(), 2)
        img.draw_line(f2(quad2[1]), f2(quad2[2]), Color.Orange(), 2)
        img.draw_line(f2(quad2[2]), f2(quad2[3]), Color.Orange(), 2)
        img.draw_line(f2(quad2[3]), f2(quad2[0]), Color.Orange(), 2)

        img.draw_line(f1(quad1[0]), f1(quad1[1]), Color.Orange(), 2)
        img.draw_line(f1(quad1[1]), f1(quad1[2]), Color.Orange(), 2)
        img.draw_line(f1(quad1[2]), f1(quad1[3]), Color.Orange(), 2)
        img.draw_line(f1(quad1[3]), f1(quad1[0]), Color.Orange(), 2)

        return img

    def draw_matches(self, matches, highlight_matches=[], img=None):
        """ Implementation of a function that is available in OpenCV 3 but not in OpenCV 2.
        Makes an image that is a side-by-side of the two images, with detected features highlighted and lines
        drawn between matching features in the two images.
        """
        if img is None:
            img = self._background_image.copy()

        for match in matches:
            color = Color.Blue() if match.is_in_transformation() else Color.SlateGray()
            self._draw_match(img, match, color, thickness=1, radius=4)

        for match in highlight_matches:
            self._draw_match(img, match, Color.Yellow(), thickness=2, radius=4)
            color = Color.Blue() if match.is_in_transformation() else Color.SlateGray()
            self._draw_match(img, match, color, thickness=1, radius=4)

        return img

    def _draw_match(self, img, match, color, thickness, radius):
        point1 = self._point_to_img_coords(match.img_point1(), 1)
        point2 = self._point_to_img_coords(match.img_point2(), 2)

        # Draw a small circle at both co-ordinates
        img.draw_circle(point1, radius, color, thickness)
        img.draw_circle(point2, radius, color, thickness)

        # Draw a line between the two points
        img.draw_line(point1, point2, color, thickness)

    def _point_to_img_coords(self, point, img_num):
        img_position = self._img1_position
        if img_num == 2:
            img_position = self._img2_position
        return (point + img_position) * self._scale_factor

    @staticmethod
    def draw_keypoints(img, keypoints):
        """ Draw the list of keypoints to the specified image and display it as a popup window. """
        marked_img = cv2.drawKeypoints(img.img, keypoints, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return Image(marked_img)
