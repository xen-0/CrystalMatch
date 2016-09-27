from __future__ import division

import unittest

from dls_util.shape import Rectangle, Point


class TestRectangle(unittest.TestCase):
    def setUp(self):
        self.RECT_CORNER_TEST_CASES = [(Point(0, 0), Point(0, 0)),
                                       (Point(0, 0), Point(1, 1)),
                                       (Point(0, 0), Point(50, 20)),
                                       (Point(-22.4, -57.98), Point(-10, 154.3)),
                                       (Point(10, -11), Point(15, -20))]

        self.POINT_TEST_CASES = [Point(0, 0),
                                 Point(1, 1),
                                 Point()]

    def test_corners_and_dimensions_correctly_calculated(self):
        for corner1, corner2 in self.RECT_CORNER_TEST_CASES:
            # Arrange
            rect = Rectangle(corner1, corner2)

            x1 = min(corner1.x, corner2.x)
            x2 = max(corner1.x, corner2.x)
            y1 = min(corner1.y, corner2.y)
            y2 = max(corner1.y, corner2.y)
            width = x2 - x1
            height = y2 - y1

            # Check dimensions
            self.assertEquals(rect.width(), width)
            self.assertEquals(rect.height(), height)
            self.assertEquals(rect.area(), width * height)

            # Test that all corners are correct
            self.assertEqual(rect.top_left().x, x1)
            self.assertEquals(rect.top_left().y, y1)
            self.assertEquals(rect.bottom_left().x, x1)
            self.assertEquals(rect.bottom_left().y, y2)
            self.assertEquals(rect.top_right().x, x2)
            self.assertEquals(rect.top_right().y, y1)
            self.assertEquals(rect.bottom_right().x, x2)
            self.assertEquals(rect.bottom_right().y, y2)

    def test_center_point_correctly_calculated(self):
        for corner1, corner2 in self.RECT_CORNER_TEST_CASES:
            # Arrange
            rect = Rectangle(corner1, corner2)

            center_x = (corner1.x + corner2.x) / 2.0
            center_y = (corner1.y + corner2.y) / 2.0

            self.assertAlmostEquals(rect.center().x, center_x)
            self.assertAlmostEquals(rect.center().y, center_y)


if __name__ == '__main__':
    unittest.main()