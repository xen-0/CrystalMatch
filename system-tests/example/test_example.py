import unittest
from os.path import realpath

from system_test import SystemTest


class ExampleSystemTest(SystemTest):
    def setUp(self):
        self._set_directory_paths(realpath(__file__))

    @unittest.SkipTest
    def test_something(self):
        """
        This will create a test output directory called test_something in the parent directory which can be tested.
        """
        self._run_crystal_matching_test("test_something",
                                        "../../input/A01_1.jpg ../../input/A01_2.jpg 1068,442 1191,1415")
