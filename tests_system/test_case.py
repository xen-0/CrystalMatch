import os

from dls_util.shape import Point
from dls_util.image import Image, Color


class _ImageWithPoints:
    def __init__(self, image_path, points):
        self._path = image_path
        self._points = points

    def path(self):
        return self._path

    def full_path(self, path_prefix):
        return path_prefix + self._path

    def image(self, prefix):
        return Image.from_file(self.full_path(prefix))

    def points(self):
        return self._points

    def set_path(self, path):
        self._path = path
        self._points = []

    def set_points(self, points):
        self._points = points

    def marked_image(self, prefix):
        image = self.image(prefix)
        for point in self._points:
            image.draw_cross(point, Color.Green(), size=30, thickness=5)
        return image


class CrystalTestCase:
    """ Represents a crystal matching system test case. The case contains the paths of the two image files,
    the user selected points in the first image, and the expected result points in the second image.
    """
    def __init__(self, path_prefix, image_1_path, image_2_path, image_1_points, image_2_points):
        self._path_prefix = path_prefix

        self._image1 = _ImageWithPoints(image_1_path, image_1_points)
        self._image2 = _ImageWithPoints(image_2_path, image_2_points)
        self._images = [self._image1, self._image2]

        self.name = image_1_path

    # -------- ACCESSORS -----------------------
    def _get_image(self, img_num):
        self.check_valid_image_number(img_num)
        return self._images[img_num-1]

    def image(self, img_num):
        return self._get_image(img_num).image(self._path_prefix)

    def image_marked(self, img_num):
        return self._get_image(img_num).marked_image(self._path_prefix)

    def image_points(self, img_num):
        return self._get_image(img_num).points()

    def image_path(self, img_num):
        return self._get_image(img_num).full_path(self._path_prefix)

    def set_image_points(self, points, img_num):
        if img_num == 1:
            self._images[0].set_points(points)
            self._images[1].set_points(points)
        else:
            if len(points) != len(self._images[0].points()):
                raise ValueError("Number of points must be the same for each image")

            self._images[1].set_points(points)

    def set_image_path(self, path, img_num):
        self._get_image(img_num).set_path(path)

    # -------- FUNCTIONALITY -----------------------
    def serialize(self):
        """ Generate a string representation of this object that can be written to file. """
        tokens = list()
        tokens.append(self._image1.path())
        tokens.append(self._image2.path())

        for p1, p2 in zip(self._image1.points(), self._image2.points()):
            tokens.append(p1.serialize() + ":" + p2.serialize())

        return ",".join(tokens)

    @staticmethod
    def deserialize(string, image_dir=""):
        """ From format:
            <image 1 path>, <image 2 path>, <x1_1>;<y1_1>:<x1_2>;<y1_2>, <x2_1>;<y2_1>:<x2_2>;<y2_2>, ...
        """
        tokens = string.split(",")
        if len(tokens) < 2:
            raise ValueError("Cannot deserialize crystal test case string.")

        # Get image paths
        image_1_path = tokens[0].strip()
        image_2_path = tokens[1].strip()

        CrystalTestCase.check_file_exists(image_dir, image_1_path)
        CrystalTestCase.check_file_exists(image_dir, image_2_path)

        # Extract selected point coordinates
        points_1 = []
        points_2 = []

        if len(tokens) > 2:
            for point in tokens[2:]:
                point_1, point_2 = CrystalTestCase._extract_points(point)
                points_1.append(point_1)
                points_2.append(point_2)

        # Create test case
        case = CrystalTestCase(image_dir, image_1_path, image_2_path, points_1, points_2)
        case.name = tokens[0].strip() + " -> " + tokens[1].strip()
        return case

    @staticmethod
    def _extract_points(string):
        """ String is the x,y coords of the point in the two images: x1;y1:x2;y2. Return two point objects. """
        point_strings = string.strip().split(":")
        points = [Point.deserialize(ps).intify() for ps in point_strings]
        return points

    @staticmethod
    def check_file_exists(prefix, file_path):
        if not os.path.isfile(prefix + file_path):
            raise ValueError("File: '{}', does not exist!".format(file_path))

    @staticmethod
    def check_valid_image_number(number):
        if number not in [1, 2]:
            raise ValueError("Value must be 1 or 2")
