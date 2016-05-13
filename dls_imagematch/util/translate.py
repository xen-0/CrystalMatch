from __future__ import division

from .point import Point


class Translate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "x: {:.4f}; y: {:.4f}".format(self.x, self.y)

    def scale(self, factor):
        return Translate(self.x*factor, self.y*factor)

    def offset(self, trs):
        return Translate(self.x + trs.x, self.y + trs.y)

    def to_point(self):
        return Point(self.x, self.y)
