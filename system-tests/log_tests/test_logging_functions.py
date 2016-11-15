from os.path import realpath, join
from os import listdir
from unittest.case import skip

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

    @skip("Reasons")
    def test_log_image_files(self):
        cmd_line = ""
        self.run_crystal_matching_test(self.test_log_image_files.__name__, cmd_line)
        self.fail()

    def _active_log_dir(self):
        return join(self.get_active_test_dir(), "logs")
