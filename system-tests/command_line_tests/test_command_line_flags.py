from os.path import realpath

from system_test import SystemTest


class TestCommandLineFlags(SystemTest):
    """
    Test the VERBOSE and DEBUG command line flags
    """
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_debug_flag_outputs_debug_text_to_console(self):
        cmd_line = "--debug {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_debug_flag_outputs_debug_text_to_console.__name__, cmd_line)

        # Check for known debug-level statement in the command line
        self.failUnlessStdOutContains("DEBUG statements visible.")

    def test_debug_flag_shortcut_operates_correctly(self):
        cmd_line = "-d {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_debug_flag_shortcut_operates_correctly.__name__, cmd_line)

        # Check for known debug-level statement in the command line
        self.failUnlessStdOutContains("DEBUG statements visible.")

    def test_verbose_flag_outputs_info_text_to_console(self):
        cmd_line = "--verbose {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_verbose_flag_outputs_info_text_to_console.__name__, cmd_line)

        # Check for known Info-level statement in the command line
        self.failUnlessStdOutContains("INFO statements visible.")

    def test_verbose_flag_shortcut_operates_correctly(self):
        cmd_line = "-v {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_verbose_flag_shortcut_operates_correctly.__name__, cmd_line)

        # Check for known Info-level statement in the command line
        self.failUnlessStdOutContains("INFO statements visible.")

    def test_version_flag_displays_version_number(self):
        cmd_line = "--version"
        self.run_crystal_matching_test(self.test_version_flag_displays_version_number.__name__, cmd_line)

        # Check for version flag on stdout
        self.failUnlessStdErrContainsRegex("v[0-9]+[.][0-9]+[.][0-9]+")

    def test_job_id_does_not_appear_in_output_when_not_set(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_job_id_does_not_appear_in_output_when_not_set.__name__, cmd_line)

        # Check for job_id in output
        self.failIfStdOutContains("job_id:")

    def test_job_id_flag_displays_job_id_in_output(self):
        cmd_line = "--job test_case {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_job_id_flag_displays_job_id_in_output.__name__, cmd_line)

        # Check for job_id in output
        self.failUnlessStdOutContains('job_id:"test_case"')

    def test_job_id_shortcut_flag_displays_job_id_in_output(self):
        cmd_line = "-j test_case {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_job_id_shortcut_flag_displays_job_id_in_output.__name__, cmd_line)

        # Check for job_id in output
        self.failUnlessStdOutContains('job_id:"test_case"')

    def test_json_flag_prints_json_to_console(self):
        cmd_line = "--to_json {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_json_flag_prints_json_to_console.__name__, cmd_line)

        # Check that the output contains JSON instead of human-readable output
        self.failUnlessStdOutContains(
            '"status": {"msg": "OK", "code": 1}'
        )
        self.failIfStdOutContains('align_status:1, OK')