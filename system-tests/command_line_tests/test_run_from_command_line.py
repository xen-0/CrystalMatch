from os.path import realpath

from system_test import SystemTest


class TestRunFromCommandLine(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_runs_with_image_alignment_only(self):
        cmd_line = "-v {resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_runs_with_image_alignment_only.__name__, cmd_line)

        # Check stdout for correct alignment
        self.failUnlessStdOutContains("Image Alignment Completed - Status: 'Good Alignment'",
                                      "Crystal Matching Complete")

    def test_runs_with_images_and_points(self):
        cmd_line = "-v {resources}/A01_1.jpg {resources}/A01_2.jpg 1068,442 1168,442 1191,1415"
        self.run_crystal_matching_test(self.test_runs_with_images_and_points.__name__, cmd_line)

        # Check that all three points were transformed
        self.failUnlessStdOutContains(
            "Image Alignment Completed - Status: 'Good Alignment'",
            "*** Crystal Match 1 ***",
            "Crystal Movement(delta): x=0.97 um, y=4.24 um",
            "*** Crystal Match 2 ***",
            "Match Failed",
            "*** Crystal Match 3 ***",
            "Crystal Movement(delta): x=3.41 um, y=-1.49 um")
