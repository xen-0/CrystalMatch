from os.path import realpath

from system_test import SystemTest


class TestLoggingFunctions(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_log_file_is_created(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_log_file_is_created.__name__, cmd_line)

        # Check default log directory exists.
        self.failUnlessDirContainsFile(self.get_active_test_dir(), "debug.log")

