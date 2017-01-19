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
        """ Generate a representation of this object that can be written to json. """
        return {
            "image": self.path(),
            "points": self._serialize_points()
        }

    def _serialize_points(self):
        output = []
        for point in self.points():
            output.append({"x": point.x, "y": point.y})
        return output

    @staticmethod
    def deserialize(json_object, image_dir):
        path = json_object["image"]
        _ImageWithPoints.check_file_exists(image_dir, path)

        # Extract selected point coordinates
        points = []
        for pt in json_object["points"]:
            points.append(Point(pt["x"], pt["y"]))

        return _ImageWithPoints(path, points)

    @staticmethod
    def check_file_exists(prefix, file_path):
        if not os.path.isfile(join(prefix, file_path)):
            raise ValueError("File: '{}', does not exist!".format(file_path))


class CrystalTestCase:
    """ Represents a crystal matching system test case. The case contains the paths of the two image files,
    the user selected points in the first image, and the expected result points in the second image.
    """
    def __init__(self, path_prefix, image_1, image_2, alignment_offset=Point(0, 0)):
        self._path_prefix = path_prefix

        self._image1 = image_1
        self._image2 = image_2
        self._images = [self._image1, self._image2]
        self._alignment_offset = alignment_offset

        self.name = image_1.path()

    # -------- ACCESSORS -----------------------
    def _get_image(self, img_num):
        self.check_valid_image_number(img_num)
        return self._images[img_num-1]

    def set_offset(self, x, y):
        self._alignment_offset = Point(int(x), int(y))

    def get_offset(self):
        return self._alignment_offset.x, self._alignment_offset.y

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
        output = {
            "offset": self._serialize_offset(),
            "formulatrix": self._image1.serialize(),
            "beamline": self._image2.serialize()
        }
        return output

    @staticmethod
    def create_new(path_prefix, image_path_1, image_path_2):
        img_with_pts_1 = _ImageWithPoints(image_path_1, [])
        img_with_pts_2 = _ImageWithPoints(image_path_2, [])
        return CrystalTestCase(path_prefix, img_with_pts_1, img_with_pts_2)

    @staticmethod
    def deserialize(json_object, image_dir):
        image1 = _ImageWithPoints.deserialize(json_object["formulatrix"], image_dir)
        image2 = _ImageWithPoints.deserialize(json_object["beamline"], image_dir)

        offset = Point(json_object["offset"]["x"], json_object["offset"]["y"])

        # Create test case
        case = CrystalTestCase(image_dir, image1, image2, alignment_offset=offset)
        case.name = json_object["formulatrix"]["image"] + " -> " + json_object["beamline"]["image"]
        return case

    def _serialize_offset(self):
        return {"x": self._alignment_offset.x, "y": self._alignment_offset.y}

    @staticmethod
    def check_valid_image_number(number):
        if number not in [1, 2]:
            raise ValueError("Value must be 1 or 2")
