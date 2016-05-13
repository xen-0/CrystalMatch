from __future__ import division


class Rectangle:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

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
