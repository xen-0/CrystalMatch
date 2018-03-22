from os.path import realpath, join, exists
from os import listdir

from system_test import SystemTest


class TestLoggingFunctions(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_log_dir_is_created(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_log_dir_is_created.__name__, cmd_line)

        # Check default log directory exists.
        self.failUnlessDirContainsFileRegex(self._active_log_dir(), "log*")

    def test_log_dir_not_present_if_logging_disabled(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_log_dir_not_present_if_logging_disabled.__name__, cmd_line)

        # Test that log directory does not exist
        self.failIfDirExists(self._active_log_dir())

    def test_log_directory_can_be_set_in_log_file(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_log_directory_can_be_set_in_log_file.__name__, cmd_line)

        # Test that log files exist in specified location
        log_dir_path = join(self.get_active_test_dir(), "test", "dir", "test_dir")
        self.failUnlessDirContainsFileRegex(log_dir_path, "log*")

    def test_log_level_set_to_debug(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_log_level_set_to_debug.__name__, cmd_line)

        # Test for debug and info statements in file
        self.failUnlessFileContains(join(self._active_log_dir(), "log"),
                                    "- root - DEBUG -",
                                    "- root - INFO -")

    def test_log_level_set_to_warning(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 345"
        self.run_crystal_matching_test(self.test_log_level_set_to_warning.__name__, cmd_line)

        # Test for debug and info statements in file
        log_file_path = join(self._active_log_dir(), "log")
        self.failIfFileContains(log_file_path,
                                "- root - DEBUG -",
                                "- root - INFO -")
        self.failUnlessFileContains(log_file_path,
                                    "- root - WARNING - Selected point with invalid format will be ignored")

    def test_log_frequency_in_seconds(self):
        """
        Note: Hard to test - set option to seconds, run a set which should take longer than a second and test
        for multiple log files in the output.
        """
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 345,345 567,567 123,123 345,345 567,567 123,123"
        self.run_crystal_matching_test(self.test_log_frequency_in_seconds.__name__, cmd_line)

        # Check for multiple log files
        log_files = listdir(self._active_log_dir())
        self.failUnless(len(log_files) > 1)
        for f in log_files:
            self.failUnless(f.startswith("log"))

    def test_log_frequency_in_hours(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 345,345 567,567 123,123 345,345 567,567 123,123"
        self.run_crystal_matching_test(self.test_log_frequency_in_hours.__name__, cmd_line)

        # Check for single log file
        log_files = listdir(self._active_log_dir())
        self.failUnlessEqual(1, len(log_files))
        self.failUnless(log_files[0].startswith("log"))

    def test_log_file_count_limit(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 345,345 567,567 123,123 345,345 567,567 123,123"
        self.run_crystal_matching_test(self.test_log_file_count_limit.__name__, cmd_line)

        # Check for logs files have been overwritten and one additional file exists
        log_files = listdir(self._active_log_dir())
        self.failUnlessEqual(2, len(log_files))
        self.failUnless(log_files[0].startswith("log"))
        self.failUnless(log_files[1].startswith("log"))
        self.failUnlessEqual(log_files[0], "log")
        self.failIfEqual(log_files[1], "log")

    def test_log_image_files(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 345,345 567,567 123,123"
        self.run_crystal_matching_test(self.test_log_image_files.__name__, cmd_line)

        # Test poi results against log file images
        poi_array = self.get_poi_from_std_out()
        log_image_dir = join(self._active_log_dir(), "images")
        self._verify_logged_image_files(log_image_dir, poi_array)

    def test_log_images_with_custom_directory(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 345,345 567,567 123,123"
        self.run_crystal_matching_test(self.test_log_images_with_custom_directory.__name__, cmd_line)

        # Test for image logs files in custom directory
        poi_array = self.get_poi_from_std_out()
        log_image_dir = join(self.get_active_test_dir(), "test", "dir", "images")
        self._verify_logged_image_files(log_image_dir, poi_array)

    def test_log_images_not_present_if_option_disabled(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 345,345 567,567 123,123"
        self.run_crystal_matching_test(self.test_log_images_not_present_if_option_disabled.__name__, cmd_line)

        # Assert that the images directory does not exist in the default location
        self.failUnless(exists(self._active_log_dir()))
        self.failIf(exists(join(self._active_log_dir(), "images")))

    def test_log_images_not_present_if_all_logging_disabled(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 345,345 567,567 123,123"
        self.run_crystal_matching_test(self.test_log_images_not_present_if_all_logging_disabled.__name__, cmd_line)

        # Assert that the entire log file is absent in the default location
        self.failIf(exists(self._active_log_dir()))
        self.failIf(exists(join(self._active_log_dir(), "images")))
        self.failIf(exists(join(self.get_active_test_dir(), "images")))

    def test_logging_flag_overrides_default_log_dirs(self):
        cmd_line = "--log test/logging/flag/ {resources}/A01_1.jpg {resources}/A01_2.jpg 345,345 567,567 123,123"
        self.run_crystal_matching_test(self.test_logging_flag_overrides_default_log_dirs.__name__, cmd_line)

        # Check specified log dir exists
        self.failIfDirExists(join(self.get_active_test_dir(), "logs"))
        log_dir = join(self.get_active_test_dir(), "test", "logging", "flag")
        log_image_dir = join(log_dir, "images")
        self.failUnlessDirContainsFile(log_dir, "log")
        self._verify_logged_image_files(log_image_dir, self.get_poi_from_std_out())

    def test_logging_flag_overrides_log_dir_in_settings_file(self):
        cmd_line = "--log test/logging/flag/ {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_logging_flag_overrides_log_dir_in_settings_file.__name__, cmd_line)

        # Check log dir exists and default and settings file dirs are absent
        self.failIfDirExists(join(self.get_active_test_dir(), "logs"))
        self.failIfDirExists(join(self.get_active_test_dir(), "should"))  # should/be/overidden set in config file
        log_dir = join(self.get_active_test_dir(), "test", "logging", "flag")
        self.failUnlessDirContainsFile(log_dir, "log")

    def test_logging_flag_ignored_if_logging_disabled(self):
        cmd_line = "--log test/logging/flag/ {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_logging_flag_ignored_if_logging_disabled.__name__, cmd_line)

        # Check that all log dirs are missing
        self.failIfDirExists(join(self.get_active_test_dir(), "logs"))
        self.failIfDirExists(join(self.get_active_test_dir(), "should"))  # should/be/overidden set in config file
        self.failIfDirExists(join(self.get_active_test_dir(), "test"))

    def test_logging_flag_with_invalid_path_reports_error(self):
        cmd_line = "--log test/log:ging/flag/ {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_logging_flag_with_invalid_path_reports_error.__name__, cmd_line)

        # Check std_err for error message return value for failure
        try:
            self.failUnlessStdErrContains(
                "ERROR:root:Could not create find/create directory, path may be invalid: test/log:ging/flag/")
            self.failUnlessRunFailed()
        except AssertionError:
            # Note - this error is only really possible in Windows, if the file has been created successfully then
            # this is probably a Linux system and the test should pass.
            self.failUnlessDirContainsFile(join(self.get_active_test_dir(), "test", "log:ging", "flag"), "log")

    def _verify_logged_image_files(self, log_image_dir, poi_array):
        # Check log files
        self.failUnless(exists(log_image_dir))
        log_images = listdir(log_image_dir)
        for image_name in log_images:
            self.failUnless("Match_" in image_name)
            self.failUnless(image_name.endswith(".jpg"))

        # Verify images are only output for successful matches (this may change)
        failures = 0
        passes = 0
        for poi in poi_array:
            if poi[2] == 1.0:
                passes += 1
            else:
                failures += 1
        self.failUnless(passes > 0 and failures > 0, "Should test both passes and failures")
        self.failUnlessEqual(len(log_images), passes)

    def _active_log_dir(self):
        return join(self.get_active_test_dir(), "logs")

    def test_log_file_contains_job_id_if_set(self):
        cmd_line = "-j test_job_123 {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_log_file_contains_job_id_if_set.__name__, cmd_line)

        # Verify that the log file contains the job ID
        self.failUnlessFileContains(join(self._active_log_dir(), "log"),
                                    ' - root - INFO - test_job_123 - job_id:"test_job_123"')
