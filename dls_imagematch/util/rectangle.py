from __future__ import division

from .point import Point


class Rectangle:
    """ Represents an axis-aligned rectangle on a 2D Cartesian plane. Notions of top/bottom and left/right
    are based on a coordinate system as viewed on a computer monitor with x increasing to the right and y
    increasing downwards.
    """
    def __init__(self, pt1, pt2):
        """ Create a rectangle from any two diagonally opposite corner points. """
        self.x1 = min(pt1.x, pt2.x)
        self.y1 = min(pt1.y, pt2.y)
        self.x2 = max(pt1.x, pt2.x)
        self.y2 = max(pt1.y, pt2.y)

    def __str__(self):
        """ String representation of the rectangle, giving the top-left and bottom-right
        corner coordinates."""
        return "Rectangle - (x1: {:.2f}, y1: {:.2f}); " \
               "(x2: {:.2f}, y2: {:.2f})".format(self.x1, self.y1, self.x2, self.y2)

    def width(self):
        """ Gets the width of the rectangle. """
        return self.x2 - self.x1

    def height(self):
        """ Gets the height of the rectangle. """
        return self.y2 - self.y1

    def area(self):
        """ Gets the area of the rectangle. """
        return self.width() * self.height()

    def top_left(self):
        """ Gets the top-left corner: min(x), min(y). """
        return Point(self.x1, self.y1)

    def top_right(self):
        """ Gets the top-right corner: max(x), min(y). """
        return Point(self.x2, self.y1)

    def bottom_left(self):
        """ Gets the bottom-left corner: min(x), max(y). """
        return Point(self.x1, self.y2)

    def bottom_right(self):
        """ Gets the bottom-right corner: max(x), max(y). """
        return Point(self.x2, self.y2)

    def corners(self):
        """ Gets a list of corners that trace the outline of the shape. """
        return [self.top_left(), self.top_right(), self.bottom_right(), self.bottom_left()]

    def center(self):
        """ Gets the center point of the rectangle (as Point object). """
        return Point((self.x1 + self.x2)/2, (self.y1 + self.y2)/2)

    def offset(self, point):
        """ Returns a new rectangle which is the same size as this one but offset (moved by the specified amount). """
        return Rectangle(self.top_left() + point, self.bottom_right() + point)

    def scale(self, factor):
        """ Returns a new rectangle which is a scaled version of this one. """
        f = factor
        return Rectangle(self.top_left() * f, self.bottom_right() * f)

    def intersection(self, rect_b):
        """ Returns a new Rectangle which is the region of overlap between the two Rectangles. """
        if not self.intersects(rect_b):
            return Rectangle(Point(0, 0), Point(0, 0))

        x1 = max(self.x1, rect_b.x1)
        y1 = max(self.y1, rect_b.y1)
        x2 = min(self.x2, rect_b.x2)
        y2 = min(self.y2, rect_b.y2)

        return Rectangle(Point(x1, y1), Point(x2, y2))

    def intersects(self, rect_b):
        """ Returns True if the two Rectangles overlap at all, False otherwise. """
        return not (self.x1 > rect_b.x2 or rect_b.x1 > self.x2 or
                    self.y1 > rect_b.y2 or rect_b.y1 > self.y2)

    def intify(self):
        """ Returns a new Rectangle which is the same as this one but with all of the coordinates
        converted to (rounded) integers. """
        return Rectangle(self.top_left().intify(), self.bottom_right().intify())

    def floatify(self):
        """ Returns a new Rectangle which is the same as this one but with all of the coordinates
        converted to floats. """
        return Rectangle(self.top_left().floatify(), self.bottom_right().floatify())

    @staticmethod
    def from_center(center, width, height):
        """ Create a new Rectangle of the specified dimensions, centered around the specified point. """
        dimensions = Point(width, height) / 2.0
        return Rectangle(center - dimensions, center + dimensions)

    @staticmethod
    def from_corner(top_left, width, height):
        """ Create a new Rectangle of the specified dimensions, with the specified top-left corner. """
        bottom_right = top_left + Point(width, height)
        return Rectangle(top_left, bottom_right)
