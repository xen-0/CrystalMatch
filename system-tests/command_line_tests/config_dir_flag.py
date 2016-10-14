from os.path import realpath
from system_testing.system_test import SystemTest


class test_command_line_config_flag(SystemTest):

    @classmethod
    def setUpClass(cls):
        command_line_args = "../input/A01_1.jpg ../input/A01_2.jpg 1068,442 1191,1415"
        SystemTest._run_crystal_match(realpath(__file__), command_line_args)

    def setUp(self):


    def test_something(self):

