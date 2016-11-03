from os.path import realpath

from dls_util.shape.point import Point
from system_test import SystemTest


class TestGlobalAlignmentTransform(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_alignment_on_identical_image(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_1.jpg 871,590"
        self.run_crystal_matching_test(self.test_alignment_with_positive_offset_on_image_b.__name__, cmd_line)

        scale, x_trans, y_trans = self.get_global_transform_from_std_out()

        # Test the global transform - this should be exact
        self.failUnlessEqual(1.0, scale)
        self.failUnlessEqual(0, x_trans)
        self.failUnlessEqual(0, y_trans)

        # Test the given points - this should be highly accurate due as the image being identical
        expected = [
            [Point(871, 590), Point(0, 0), 1, 0],
        ]
        self.failUnlessPoiAlmostEqual(expected)

    def test_alignment_with_positive_offset_on_image_b(self):
        cmd_line = "{resources}/A10_1@-10-10.jpg {resources}/A10_1.jpg 871,590"
        self.run_crystal_matching_test(self.test_alignment_with_positive_offset_on_image_b.__name__, cmd_line)

        scale, x_trans, y_trans = self.get_global_transform_from_std_out()

        # Test the global transform - this should be exact
        self.failUnlessEqual(1.0, scale)
        self.failUnlessEqual(10.0, x_trans)
        self.failUnlessEqual(10.0, y_trans)

        # Test the given points - this should be highly accurate due as the image being identical
        expected = [
            [Point(871, 590), Point(0, 0), 1, 0],
        ]
        self.failUnlessPoiAlmostEqual(expected)

    def test_alignment_with_negative_offset_on_image_b(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_1@-10-10.jpg 871,590"
        self.run_crystal_matching_test(self.test_alignment_with_negative_offset_on_image_b.__name__, cmd_line)

        scale, x_trans, y_trans = self.get_global_transform_from_std_out()

        # Test the global transform - this should be exact
        self.failUnlessEqual(1.0, scale)
        self.failUnlessEqual(-10.0, x_trans)
        self.failUnlessEqual(-10.0, y_trans)

        # Test the given points - this should be highly accurate due as the image being identical
        expected = [
            [Point(871, 590), Point(0, 0), 1, 0],
        ]
        self.failUnlessPoiAlmostEqual(expected)

    def test_alignment_with_mixed_offset_on_image_b(self):
        cmd_line = "{resources}/A10_1@-0-10.jpg {resources}/A10_1@-10-0.jpg 871,590"
        self.run_crystal_matching_test(self.test_alignment_with_positive_offset_on_image_b.__name__, cmd_line)

        scale, x_trans, y_trans = self.get_global_transform_from_std_out()

        # Test the global transform - this should be exact
        self.failUnlessEqual(1.0, scale)
        self.failUnlessEqual(10.0, x_trans)
        self.failUnlessEqual(-10.0, y_trans)

        # Test the given points - this should be highly accurate due as the image being identical
        expected = [
            [Point(871, 590), Point(0, 0), 1, 0],
        ]
        self.failUnlessPoiAlmostEqual(expected)

    def test_alignment_with_mixed_offset_counterpoint_on_image_b(self):
        cmd_line = "{resources}/A10_1@-0-10.jpg {resources}/A10_1@-10-0.jpg 871,590"
        self.run_crystal_matching_test(self.test_alignment_with_positive_offset_on_image_b.__name__, cmd_line)

        scale, x_trans, y_trans = self.get_global_transform_from_std_out()

        # Test the global transform - this should be exact
        self.failUnlessEqual(1.0, scale)
        self.failUnlessEqual(-10.0, x_trans)
        self.failUnlessEqual(10.0, y_trans)

        # Test the given points - this should be highly accurate due as the image being identical
        expected = [
            [Point(871, 590), Point(0, 0), 1, 0],
        ]
        self.failUnlessPoiAlmostEqual(expected)
