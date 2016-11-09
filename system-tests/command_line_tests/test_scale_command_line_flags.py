from os.path import realpath

from nose_parameterized import parameterized

from system_test import SystemTest


class TestScaleCommandLineFlags(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_scale_is_read_from_configuration_file_when_flags_not_set(self):
        cmd_line = "{resources}/A10_2@0.5.jpg {resources}/A10_2@0.75.jpg"
        test_name = self.test_scale_is_read_from_configuration_file_when_flags_not_set.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        # Test for accurate global alignment
        self.failUnlessGlobalAlignmentIsValid(1.5)

    def test_set_scale_flag_for_input_image_only(self):
        cmd_line = "--scale_input 1.33333 {resources}/A10_2@0.75.jpg {resources}/A10_2.jpg"
        test_name = self.test_set_scale_flag_for_input_image_only.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        # Test for accurate global alignment
        self.failUnlessGlobalAlignmentIsValid(1.333)

    def test_set_scale_flag_for_output_image_only(self):
        cmd_line = "--scale_output 0.75 {resources}/A10_2@0.75.jpg {resources}/A10_2.jpg"
        test_name = self.test_set_scale_flag_for_output_image_only.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        # Test for accurate global alignment
        self.failUnlessGlobalAlignmentIsValid(1.333)

    def test_set_scale_flag_for_output_image_only_scaled_by_10(self):
        cmd_line = "--scale_input 10 --scale_output 7.5 {resources}/A10_2@0.75.jpg {resources}/A10_2.jpg"
        test_name = self.test_set_scale_flag_for_output_image_only_scaled_by_10.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        # Test for accurate global alignment
        self.failUnlessGlobalAlignmentIsValid(1.333)

    def test_set_scale_flags_for_both_images(self):
        cmd_line = "--scale_input 2 --scale_output 1.333333 {resources}/A10_2@0.5.jpg {resources}/A10_2@0.75.jpg"
        test_name = self.test_set_scale_flags_for_both_images.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        # Test for accurate global alignment
        self.failUnlessGlobalAlignmentIsValid(1.5)

    @parameterized.expand(
        [
            ["input-string", "--scale_input not_a_val"],
            ["output-string", "--scale_output not_a_val"],
            ["input-invalid", "--scale_input 0.5.4"],
            ["output-invalid", "--scale_output 0.5.4"],
        ]
    )
    def test_scale_flags_with_invalid_value_raises_error(self, name, cmd_input):
        cmd_line = cmd_input + " {resources}/A10_2@0.5.jpg {resources}/A10_2@0.75.jpg"
        test_name = "test_scale_flags_with_invalid_value_raises_error-" + name
        self.run_crystal_matching_test(test_name, cmd_line)
        self.failUnlessStdErrContainsRegex("error: argument --scale_(output|input): invalid float value: ")

    def test_scale_flag_with_values_causing_incorrect_alignment_returns_failure(self):
        # Run app wit scale deliberately inverted
        cmd_line = "--scale_input 7.5 --scale_output 10 {resources}/A10_2@0.75.jpg {resources}/A10_2.jpg"
        test_name = self.test_scale_flag_with_values_causing_incorrect_alignment_returns_failure.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        self.failUnlessStdOutContains("align_status:0, FAIL")

    def test_scaling_causing_invalid_overlap_of_matched_areas_returns_failure(self):
        """ Note: This test was added to cover a specific issue which caused a crash using the parameters below. The
        scaling causes an invalid alignment match where the proposed solution does not contain intersecting regions
        of interest causing an None value to be returned. """
        cmd_line = "{resources}/A10_2.jpg {resources}/A10_2@0.5.jpg 756,412 --scale_input 1 --scale_output 0.5"
        test_name = self.test_scaling_causing_invalid_overlap_of_matched_areas_returns_failure.__name__
        self.run_crystal_matching_test(test_name, cmd_line)
        self.failUnlessStdOutContains("align_status:0, FAIL")

    def failUnlessGlobalAlignmentIsValid(self, expected_scale):
        scale, x_trans, y_trans = self.get_global_transform_from_std_out()
        self.failUnlessAlmostEqual(expected_scale, scale, delta=0.001)
        self.failUnlessAlmostEqual(0, x_trans, delta=1)
        self.failUnlessAlmostEqual(0, y_trans, delta=1)
        self.failUnlessStdOutContains("align_status:1, OK")
