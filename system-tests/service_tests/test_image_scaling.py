from os.path import realpath

from system_test import SystemTest


class TestImageScaling(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_alignment_with_smaller_beam_line_image(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_2@0.5.jpg"
        self.run_crystal_matching_test(self.test_alignment_with_smaller_beam_line_image.__name__, cmd_line)

        # Check the global transformation, status and error margin
        self.failUnlessStdOutContains(
            'align_transform:0.5, (2.00, 8.00)',
            'align_status:1, OK',
            # TODO: Could extract the values and test via thresholding?
            'align_error:8.'
        )

    def test_alignment_with_larger_beam_line_image(self):
        cmd_line = "{resources}/A10_2@0.5.jpg {resources}/A10_1.jpg"
        self.run_crystal_matching_test(self.test_alignment_with_larger_beam_line_image.__name__, cmd_line)

        # Check the global transformation, status and error margin
        self.failUnlessStdOutContains(
            'align_transform:2, (0.00, -4.00)',
            'align_status:1, OK',
            # TODO: Could extract the values and test via thresholding?
            'align_error:7.'
        )

    def test_alignment_with_smaller_beam_line_image_with_points(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_2@0.5.jpg"
        self.run_crystal_matching_test(self.test_alignment_with_smaller_beam_line_image_with_points.__name__, cmd_line)

        # Check Points of interest are found and reported at correct co-ordinates
        self.fail("Not implemented.")

    def test_alignment_with_larger_beam_line_image_with_points(self):
        cmd_line = "{resources}/A10_2@0.5.jpg {resources}/A10_1.jpg"
        self.run_crystal_matching_test(self.test_alignment_with_larger_beam_line_image_with_points.__name__, cmd_line)

        # Check Points of interest are found and reported at correct co-ordinates
        self.fail("Not implemented.")
