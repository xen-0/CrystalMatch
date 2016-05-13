from __future__ import division

import math


class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __add__(self, p):
        return Point(self.x+p.x, self.y+p.y)

    def __sub__(self, p):
        return Point(self.x-p.x, self.y-p.y)

    def __mul__(self, scalar):
        return Point(self.x*scalar, self.y*scalar)

    def __div__(self, scalar):
        return Point(self.x/scalar, self.y/scalar)

    def __floordiv__(self, scalar):
        return Point(self.x/scalar, self.y/scalar)

    def __truediv__(self, scalar):
        return Point(self.x/scalar, self.y/scalar)

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.x, self.y)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def distance_to(self, p):
        return (self - p).length()

    def intify(self):
        return Point(int(round(self.x, 0)), int(round(self.y, 0)))

    def floatify(self):
        return Point(float(self.x), float(self.y))

    def tuple(self):
        return self.x, self.y

    @staticmethod
    def from_array(arr):
        return Point(arr[0], arr[1])


