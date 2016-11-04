from os.path import realpath
from unittest.case import skip

from system_test import SystemTest


class TestImageScaling(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_alignment_with_smaller_beam_line_image(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_2@0.5.jpg"
        self.run_crystal_matching_test(self.test_alignment_with_smaller_beam_line_image.__name__, cmd_line)

        # Check the global transformation, status and error margin
        scale, x, y = self.get_global_transform_from_std_out()
        self.failUnlessEqual(scale, 0.5)
        self.failUnlessEqual(x, 0)
        self.failUnlessEqual(y, -4)
        matches = self.regex_from_std_out('align_error:(.*)')
        self.failUnlessEqual(1, len(matches))
        self.failUnlessStdOutContains('align_status:1, OK')

    def test_alignment_with_larger_beam_line_image(self):
        cmd_line = "{resources}/A10_2@0.5.jpg {resources}/A10_1.jpg"
        self.run_crystal_matching_test(self.test_alignment_with_larger_beam_line_image.__name__, cmd_line)

        # Check the global transformation, status and error margin
        scale, x, y = self.get_global_transform_from_std_out()
        self.failUnlessEqual(scale, 2.0)
        self.failUnlessEqual(x, 2)
        self.failUnlessEqual(y, 8)
        matches = self.regex_from_std_out('align_error:(.*)')
        self.failUnlessEqual(1, len(matches))
        self.failUnlessStdOutContains('align_status:1, OK')

    @skip("Not implemented")
    def test_alignment_with_smaller_beam_line_image_with_points(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_2@0.5.jpg 871,590"
        self.run_crystal_matching_test(self.test_alignment_with_smaller_beam_line_image_with_points.__name__, cmd_line)

        # Check Points of interest are found and reported at correct co-ordinates
        self.fail("Not implemented.")

    @skip("Not implemented")
    def test_alignment_with_larger_beam_line_image_with_points(self):
        cmd_line = "{resources}/A10_2@0.5.jpg {resources}/A10_1.jpg"
        self.run_crystal_matching_test(self.test_alignment_with_larger_beam_line_image_with_points.__name__, cmd_line)

        # Check Points of interest are found and reported at correct co-ordinates
        self.fail("Not implemented.")
