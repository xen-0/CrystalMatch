from random import randint


class Color:
    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def bgra(self):
        return self.b, self.g, self.r, self.a

    def bgr(self):
        return self.b, self.g, self.r

    def mono(self):
        return int(round(0.3*self.r + 0.6*self.g + 0.1*self.b))

    @staticmethod
    def Random():
        return Color(randint(0, 255), randint(0, 255), randint(0, 255), 255)

    @staticmethod
    def TransparentBlack(): return Color(0, 0, 0, 0)

    @staticmethod
    def TransparentWhite(): return Color(255, 255, 255, 0)

    @staticmethod
    def White(): return Color(255, 255, 255)

    @staticmethod
    def Black(): return Color(0, 0, 0)

    @staticmethod
    def Grey(): return Color(128, 128, 128)

    @staticmethod
    def Blue(): return Color(0, 0, 255)

    @staticmethod
    def Red(): return Color(255, 0, 0)

    @staticmethod
    def Green(): return Color(0, 255, 0)

    @staticmethod
    def Yellow(): return Color(255, 255, 0)

    @staticmethod
    def Cyan(): return Color(0, 255, 255)

    @staticmethod
    def Magenta(): return Color(255, 0, 255)

    @staticmethod
    def Orange(): return Color(255, 128, 0)

    @staticmethod
    def Purple(): return Color(128, 0, 255)
