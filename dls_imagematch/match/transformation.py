import cv2
import numpy as np

from dls_imagematch.util import Point, Image


class Transformation:
    def __init__(self, translation, homography_matrix=None):
        self._translation = translation
        self._homography = homography_matrix
        self._homography_inverse = None

        if self._homography is not None:
            _, self._homography_inverse = cv2.invert(self._homography)

        self._translation_only = self._homography is None

    def translation(self):
        return self._translation

    def transform_image(self, image, output_size):
        if self._translation_only:
            offset = self._translation.to_point()
            warped = Image.blank(output_size[0], output_size[1], image.channels)
            warped.paste(image, offset)
        else:
            warped = cv2.warpPerspective(image.img, self._homography, output_size)
            warped = Image(warped)

        return warped

    def inverse_transform_image(self, image, output_size):
        if self._translation_only:
            offset = - self._translation.to_point()
            warped = Image.blank(output_size[0], output_size[1], image.channels)
            warped.paste(image, offset)
        else:
            warped = cv2.warpPerspective(image.img, self._homography_inverse, output_size)
            warped = Image(warped)

        return warped

    def transform_points(self, points):
        if self._translation_only:
            transformed = [p + self._translation.to_point() for p in points]
        else:
            np_array = self._points_to_np_array(points)
            transformed = cv2.perspectiveTransform(np_array, self._homography)
            transformed = self._np_array_to_points(transformed)

        return transformed

    def inverse_transform_points(self, points):
        if self._translation_only:
            transformed = [p - self._translation.to_point() for p in points]
        else:
            np_array = self._points_to_np_array(points)
            transformed = cv2.perspectiveTransform(np_array, self._homography_inverse)
            transformed = self._np_array_to_points(transformed)

        return transformed

    @staticmethod
    def _points_to_np_array(points):
        points_list = [[p.x, p.y] for p in points]
        np_array = np.float32(points_list).reshape(-1, 1, 2)
        return np_array

    @staticmethod
    def _np_array_to_points(np_array):
        points = []
        for p in np_array:
            points.append(Point(p[0][0], p[0][1]))

        return points
