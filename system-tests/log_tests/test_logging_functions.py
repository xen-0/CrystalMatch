from os.path import realpath, join
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
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_log_level_set_to_warning.__name__, cmd_line)

        # Test for debug and info statements in file
        self.failIfFileContains(join(self._active_log_dir(), "log"),
                                "- root - DEBUG -",
                                "- root - INFO -")
        # TODO: Throw warning

    @skip("Reasons")
    def test_log_frequency(self):
        cmd_line = ""
        self.run_crystal_matching_test(self.test_log_frequency.__name__, cmd_line)
        self.fail()

    @skip("Reasons")
    def test_log_file_count_limit(self):
        cmd_line = ""
        self.run_crystal_matching_test(self.test_log_file_count_limit.__name__, cmd_line)
        self.fail()

    @skip("Reasons")
    def test_log_image_files(self):
        cmd_line = ""
        self.run_crystal_matching_test(self.test_log_image_files.__name__, cmd_line)
        self.fail()

    def _active_log_dir(self):
        return join(self.get_active_test_dir(), "logs")
