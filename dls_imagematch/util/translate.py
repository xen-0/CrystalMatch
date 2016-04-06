from __future__ import division

class Translate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def scale(self, factor):
        return Translate(self.x*factor, self.y*factor)

    def offset(self, trs):
        return Translate(self.x + trs.x, self.y + trs.y)
