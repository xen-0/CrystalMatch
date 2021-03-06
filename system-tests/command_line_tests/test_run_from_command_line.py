from os.path import realpath

from system_test import SystemTest


class TestRunFromCommandLine(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_runs_with_image_alignment_only(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg"
        self.run_crystal_matching_test(self.test_runs_with_image_alignment_only.__name__, cmd_line)

        # Check stdout for correct alignment
        self.failUnlessStdOutContains("align_status:1, OK")

    def test_runs_with_images_and_points(self):
        cmd_line = "{resources}/A01_1.jpg {resources}/A01_2.jpg 1068,442 1168,442 1191,1415"
        self.run_crystal_matching_test(self.test_runs_with_images_and_points.__name__, cmd_line)

        # Check that all three points were transformed
        #self.failUnlessStdOutContains("poi:(1065.97, 444.24)")
        self.failUnlessStdOutContains(
            'poi:(1065.97, 444.24) z: None ; (0.97, 4.24) ; 1, OK ; 2.16042916777',
            'poi:(1165.00, 440.00) z: None ; (0.00, 0.00) ; 0, FAIL ; 0',
            'poi:(1191.41, 1411.51) z: None ; (3.41, -1.49) ; 1, OK ; 1.95516816312',
        )

