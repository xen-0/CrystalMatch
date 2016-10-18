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

    def test_runs_with_images_and_points(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 1068,442 1168,442 1191,1415"
        self.run_crystal_matching_test(self.test_runs_with_images_and_points.__name__, cmd_line)

        # Check that all three points were transformed and that there are no errors
        self.failIfStrErrHasContent()
        self.failUnlessStdoutContains("Image Alignment Completed - Status: 'Good Alignment'",
                                      "*** Crystal Match 1 ***",
                                      "*** Crystal Match 2 ***",
                                      "*** Crystal Match 3 ***")
