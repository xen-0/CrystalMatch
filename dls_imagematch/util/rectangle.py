from __future__ import division


class Rectangle:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

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
        return self.x1, self.y1

    def top_right(self):
        return self.x2, self.y1

    def bottom_left(self):
        return self.x1, self.y2

    def bottom_right(self):
        return self.x2, self.y2

    def center(self):
        return (self.x1 + self.x2)/2, (self.y1 + self.y2)/2

    def scale(self, factor):
        f = factor
        return Rectangle(self.x1 * f, self.y1 * f, self.x2 * f, self.y2 * f)

    def intersection(self, rect_b):
        if not self.intersects(rect_b):
            return Rectangle(0, 0, 0, 0)

        x1 = max(self.x1, rect_b.x1)
        y1 = max(self.y1, rect_b.y1)
        x2 = min(self.x2, rect_b.x2)
        y2 = min(self.y2, rect_b.y2)

        return Rectangle(x1, y1, x2, y2)

    def intersects(self, rect_b):
        return not (self.x1 > rect_b.x2 or rect_b.x1 > self.x2 or
                    self.y1 > rect_b.y2 or rect_b.y1 > self.y2)

    def to_ints(self):
        return Rectangle(int(round(self.x1, 0)), int(round(self.y1, 0)),
                         int(round(self.x2, 0)), int(round(self.y2, 0)))

    @staticmethod
    def from_center(x, y, width, height):
        x1, y1 = x - width / 2, y - height / 2
        x2, y2 = x + width / 2, y + height / 2
        return Rectangle(x1, y1, x2, y2)

    @staticmethod
    def from_corner(x1, y1, width, height):
        x2, y2 = x1 + width, y1 + height
        return Rectangle(x1, y1, x2, y2)
