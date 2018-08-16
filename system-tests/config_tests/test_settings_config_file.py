from os.path import realpath, join

from system_test import SystemTest


class TestSettingsConfigFile(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_settings_config_file_defaults_match_expected(self):
        """ Test the default contents of the Settings config file against expected output. """
        cmd_line = "{resources}/A10_1.jpg {resources}/A10_2.jpg"
        test_name = self.test_settings_config_file_defaults_match_expected.__name__
        self.run_crystal_matching_test(test_name, cmd_line)

        #test_settings_file = join(self.get_active_test_dir(), 'config', 'settings.ini')
        #expected_settings_file = join(self.substitute_tokens("{expected}"), "settings.ini")
        #self.failUnlessFilesMatch(expected_settings_file, test_settings_file)
