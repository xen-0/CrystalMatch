from os.path import realpath, join

from system_test import SystemTest


class TestCrsytalStageConfigFile(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_crystal_config_file_default_match_expected(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_2.jpg"
        test_name = self.test_crystal_config_file_default_match_expected.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        test_settings_file = join(self.get_active_test_dir(), 'config', 'crystal.ini')
        expected_settings_file = join(self.substitute_tokens("{expected}"), "crystal.ini")
        self.failUnlessFilesMatch(expected_settings_file, test_settings_file)

    def test_crystal_stage_disabled_by_changing_perform_poi_analysis_option(self):
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_2.jpg 123,123 456,456 " \
                   "--config {resources}/configs/config_disable_poi_stage"
        test_name = self.test_crystal_stage_disabled_by_changing_perform_poi_analysis_option.__name__
        self.run_crystal_matching_test(test_name, cmd_line)
        self.fail("incomplete")

    def test_crystal_stage_disabled_is_reported_correctly_in_json(self):
        self.fail("incomplete")
