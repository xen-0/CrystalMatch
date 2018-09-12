from os.path import realpath

from system_test import SystemTest


class TestCommandLineFlags(SystemTest):
    """
    Test the VERBOSE and DEBUG command line flags
    """
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_version_flag_displays_version_number(self):
        cmd_line = "--version"
        self.run_crystal_matching_test(self.test_version_flag_displays_version_number.__name__, cmd_line)

        # Check for version flag on stdout
        self.failUnlessStdErrContainsRegex("v[0-9]+[.][0-9]+[.][0-9]+")

    def test_json_flag_prints_json_to_console(self):
        cmd_line = "--to_json {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_json_flag_prints_json_to_console.__name__, cmd_line)

        # Check that the output contains JSON instead of human-readable output
        self.failUnlessStdOutContains(
            '"status": {"msg": "OK", "code": 1}'
        )
        self.failIfStdOutContains('align_status:1, OK')
