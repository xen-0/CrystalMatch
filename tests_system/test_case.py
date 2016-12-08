import os

from os.path import join

from dls_util.shape import Point
from dls_util.imaging import Image, Color


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

    def add_point(self, point):
        self._points.append(point)

    def delete_poi(self, index):
        del self._points[index]

    def update_poi(self, index, point):
        if index >= len(self._points):
            self._points.append(point)
        else:
            self._points[index] = point

    def set_points(self, points):
        self._points = points

    def marked_image(self, prefix):
        image = self.image(prefix)
        for point in self._points:
            image.draw_cross(point, Color.green(), size=30, thickness=5)
        return image

    def has_points(self):
        return any(self._points)

    def num_points(self):
        return len(self._points)

    def serialize(self):
        """ Generate a string representation of this object that can be written to file. """
        str_points = [p.serialize() for p in self.points()]
        return self.path() + "," + ":".join(str_points)

    @staticmethod
    def deserialize(string, image_dir=""):
        """ From format:
            <image path>,<x1>;<y1>:<x2>;<y2>:...
        """
        tokens = string.split(",")
        if len(tokens) != 2:
            raise ValueError("Cannot deserialize crystal test case string.")

        path = tokens[0].strip()
        str_points = [p for p in tokens[1].strip().split(":") if any(p)]

        _ImageWithPoints.check_file_exists(image_dir, path)

        # Extract selected point coordinates
        points = []
        for str_point in str_points:
            point = Point.deserialize(str_point)
            points.append(point)

        return _ImageWithPoints(path, points)

    @staticmethod
    def check_file_exists(prefix, file_path):
        if not os.path.isfile(join(prefix, file_path)):
            raise ValueError("File: '{}', does not exist!".format(file_path))


class CrystalTestCase:
    """ Represents a crystal matching system test case. The case contains the paths of the two image files,
    the user selected points in the first image, and the expected result points in the second image.
    """
    def __init__(self, path_prefix, image_1, image_2):
        self._path_prefix = path_prefix

        self._image1 = image_1
        self._image2 = image_2
        self._images = [self._image1, self._image2]

        self.name = image_1.path()

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

    def max_num_points(self):
        return max(len(self.image_points(1)), len(self.image_points(2)))

    def get_points_at_index(self, index):
        points_1 = self.image_points(1)
        points_2 = self.image_points(2)
        pt_1 = points_1[index] if len(points_1) > index else None
        pt_2 = points_2[index] if len(points_2) > index else None
        return pt_1, pt_2

    def image_path(self, img_num):
        return self._get_image(img_num).full_path(self._path_prefix)

    def add_poi(self, point_1, point_2):
        self._image1.add_point(point_1)
        self._image2.add_point(point_2)

    def update_poi(self, index, point_1, point_2):
        self._image1.update_poi(index, point_1)
        self._image2.update_poi(index, point_2)

    def delete_poi(self, index):
        self._image1.delete_poi(index)
        self._image2.delete_poi(index)

    def set_image_path(self, path, img_num):
        self._get_image(img_num).set_path(path)

    def is_testable_case(self):
        testable = self._image1 is not None and self._image2 is not None \
                   and self._image1.has_points() \
                   and self._image1.num_points() == self._image2.num_points()

        return testable

    # -------- FUNCTIONALITY -----------------------
    def serialize(self):
        """ Generate a string representation of this object that can be written to file. """
        return self._image1.serialize() + "," + self._image2.serialize()

    @staticmethod
    def create_new(path_prefix, image_path_1, image_path_2):
        img_with_pts_1 = _ImageWithPoints(image_path_1, [])
        img_with_pts_2 = _ImageWithPoints(image_path_2, [])
        return CrystalTestCase(path_prefix, img_with_pts_1, img_with_pts_2)

    @staticmethod
    def deserialize(string, image_dir=""):
        """ From format:
            <image 1 path>,<x1>;<y1>:<x2>;<y2>,<image 2 path>,<x1>;<y1>:<x2>;<y2>
        """
        tokens = string.split(",")
        if len(tokens) != 4:
            raise ValueError("Cannot deserialize crystal test case string.")

        string1 = tokens[0] + "," + tokens[1]
        image1 = _ImageWithPoints.deserialize(string1, image_dir)

        string2 = tokens[2] + "," + tokens[3]
        image2 = _ImageWithPoints.deserialize(string2, image_dir)

        # Create test case
        case = CrystalTestCase(image_dir, image1, image2)
        case.name = tokens[0].strip() + " -> " + tokens[2].strip()
        return case

    @staticmethod
    def check_valid_image_number(number):
        if number not in [1, 2]:
            raise ValueError("Value must be 1 or 2")
