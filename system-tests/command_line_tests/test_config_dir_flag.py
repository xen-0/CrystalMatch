from os.path import realpath, join

from system_test import SystemTest


class TestCommandLineConfigFlag(SystemTest):
    def setUp(self):
        self._set_directory_paths(realpath(__file__))

    def test_config_flag_creates_config_directory(self):
        test_name = "test_config_flag_creates_config_directory"
        config = "--config " + join(self._get_test_output_dir(test_name), "test", "dir", "path")
        self._run_crystal_matching_test(test_name,
                                        config + " " + "../../input/A01_1.jpg ../../input/A01_2.jpg 1068,442")

        # Check configuration directory exists
        expected_config_dir = join(self._get_test_output_dir(test_name), "test", "dir", "path", "config")
        expected_files = ["align.ini",
                          "crystal.ini",
                          "det_blob.ini",
                          "det_brisk.ini",
                          "det_dense.ini",
                          "det_fast.ini",
                          "det_gftt.ini",
                          "det_harris.ini",
                          "det_mser.ini",
                          "det_orb.ini",
                          "det_sift.ini",
                          "det_star.ini",
                          "det_surf.ini",
                          "licensing.ini"]
        self.failUnlessDirExists(expected_config_dir)
        self.failUnlessDirContainsFiles(expected_config_dir, expected_files)
