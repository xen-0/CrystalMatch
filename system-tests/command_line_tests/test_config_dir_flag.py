from os.path import realpath, join

from system_test import SystemTest


class TestCommandLineConfigFlag(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_config_flag_creates_config_directory(self):
        test_name = "test_config_flag_creates_config_directory"
        config = "--config " + join(self._get_test_output_dir(test_name), "test", "dir", "path")
        self.run_crystal_matching_test(test_name,
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

        # Test that a warning message is shown when the config dir does not exist
        self.failUnlessStdoutContains("WARNING: configuration directory not found, directory will be created")
