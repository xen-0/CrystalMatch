import unittest

from dls_imagematch.util import Rectangle, Point


class TestRectangle(unittest.TestCase):
    def setUp(self):
        self.rect_corners = [[Point(0, 0), Point(0, 0)],
                             [Point(0, 0), Point(1, 1)],
                             [Point(0, 0), Point(50, 20)],
                             [Point(-22.4, -57.98), Point(-10, 154.3)],
                             [Point(10, -11), Point(15, -20)]]

    def test_basic_geometry(self):
        for corners in self.rect_corners:
            corner1, corner2 = corners[0], corners[1]
            rect = Rectangle(corner1, corner2)

            x1, x2 = min(corner1.x, corner2.x), max(corner1.x, corner2.x)
            y1, y2 = min(corner1.y, corner2.y), max(corner1.y, corner2.y)
            width = x2 - x1
            height = y2 - y1

            # Check dimensions
            self.assertEquals(rect.width(), width)
            self.assertEquals(rect.height(), height)
            self.assertEquals(rect.area(), width * height)

            # Test that all corners are correct
            self.assertEquals(rect.top_left().x, x1)
            self.assertEquals(rect.top_left().y, y1)
            self.assertEquals(rect.bottom_left().x, x1)
            self.assertEquals(rect.bottom_left().y, y2)
            self.assertEquals(rect.top_right().x, x2)
            self.assertEquals(rect.top_right().y, y1)
            self.assertEquals(rect.bottom_right().x, x2)
            self.assertEquals(rect.bottom_right().y, y2)


if __name__ == '__main__':
    unittest.main()