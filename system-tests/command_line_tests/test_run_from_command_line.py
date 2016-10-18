from os.path import realpath

from system_test import SystemTest


class TestRunFromCommandLine(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_runs_with_image_alignment_only(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_runs_with_image_alignment_only.__name__, cmd_line)

        # Check stderr for content and stdout for correct alignment
        self.failIfStrErrHasContent()
        self.failUnlessStdoutContains("Image Alignment Completed - Status: 'Good Alignment'",
                                      "Crystal Matching Complete")
