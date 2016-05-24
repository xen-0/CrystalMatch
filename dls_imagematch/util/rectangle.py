from __future__ import division

from .point import Point


class Rectangle:
    def __init__(self, pt1, pt2):
        """ Create a rectangle from two corner points. """
        self.x1 = min(pt1.x, pt2.x)
        self.y1 = min(pt1.y, pt2.y)
        self.x2 = max(pt1.x, pt2.x)
        self.y2 = max(pt1.y, pt2.y)

    def __str__(self):
        return "Rectangle - (x1: {:.2f}, y1: {:.2f}); " \
               "(x2: {:.2f}, y2: {:.2f})".format(self.x1, self.y1, self.x2, self.y2)

    def width(self):
        return self.x2 - self.x1

    def height(self):
        return self.y2 - self.y1

    def area(self):
        return self.width() * self.height()

    def top_left(self):
        return Point(self.x1, self.y1)

    def top_right(self):
        return Point(self.x2, self.y1)

    def bottom_left(self):
        return Point(self.x1, self.y2)

    def bottom_right(self):
        return Point(self.x2, self.y2)

    def corners(self):
        return [self.top_left(), self.top_right(), self.bottom_right(), self.bottom_left()]

    def center(self):
        return Point((self.x1 + self.x2)/2, (self.y1 + self.y2)/2)

    def offset(self, point):
        return Rectangle(self.top_left() + point, self.bottom_right() + point)

    def scale(self, factor):
        f = factor
        return Rectangle(self.top_left() * f, self.bottom_right() * f)

    def intersection(self, rect_b):
        if not self.intersects(rect_b):
            return Rectangle(Point(0, 0), Point(0, 0))

        x1 = max(self.x1, rect_b.x1)
        y1 = max(self.y1, rect_b.y1)
        x2 = min(self.x2, rect_b.x2)
        y2 = min(self.y2, rect_b.y2)

        return Rectangle(Point(x1, y1), Point(x2, y2))

    def intersects(self, rect_b):
        return not (self.x1 > rect_b.x2 or rect_b.x1 > self.x2 or
                    self.y1 > rect_b.y2 or rect_b.y1 > self.y2)

    def intify(self):
        return Rectangle(self.top_left().intify(), self.bottom_right().intify())

    def floatify(self):
        return Rectangle(self.top_left().floatify(), self.bottom_right().floatify())

    @staticmethod
    def from_center(center, width, height):
        dimensions = Point(width, height) / 2.0
        return Rectangle(center - dimensions, center + dimensions)

    @staticmethod
    def from_corner(top_left, width, height):
        bottom_right = top_left + Point(width, height)
        return Rectangle(top_left, bottom_right)
