from os import makedirs, listdir
from os.path import exists, join, splitext, isdir
from re import match
from shutil import rmtree
from subprocess import call
from unittest import TestCase


class SystemTest(TestCase):
    """
    Parent class which provides a framework to run System Tests using the standard Python unittest libraries.
    A system test case should extend this class and include the boilerplate code below to run the
    Crystal Matching algorithm.

    def setUp(self):
        self._set_directory_paths(realpath(__file__))

    def test_something(self):
        # Command line arguments below can be modified for each test.
        self._run_crystal_matching_test("test_something",
                                        "../../input/A01_1.jpg ../../input/A01_2.jpg 1068,442 1191,1415")
        ...

    A Test suite directory is created for each TestCase object based on the file name; this is a convenient place to
    store input files.  Within this directory a global output directory is created which is ignored by git - in turn
    this will contain an output directory for each named test.
    """

    OUTPUT_DIR_NAME = "sys_test_output"
    CONFIG_FLAG = "--config"

    def _get_output_dir(self):
        """
        Assert-safe method of retrieving the output directory.
        :return: Output directory for the current test suite
        """
        assert hasattr(self, "_output_dir"), "Output directory not set"
        assert self._output_dir is not None, "Output directory not set correctly!"
        return self._output_dir

    def _get_test_suite_dir(self):
        """
        Assert-safe method of retrieving the test suite directory.
        :return:
        """
        assert hasattr(self, "_test_suite_dir"), "Test directory not set"
        assert self._test_suite_dir is not None, "Test directory not set correctly!"
        return self._test_suite_dir

    def _get_test_output_dir(self, test_name):
        return join(self._get_output_dir(), test_name)

    def _set_directory_paths(self, test_file_path):
        """
        Must be included in the setUp() method of the child TestCase.
        :param test_file_path: Must be the result of os.path.realpath(__file__) from the child file.
        """
        # Set test directory
        self._test_suite_dir, extension = splitext(test_file_path)

        # Set output directory
        self._output_dir = join(self._get_test_suite_dir(), self.OUTPUT_DIR_NAME)

    def _run_crystal_matching_test(self, test_name, cmd_line_args):
        """
        Run the Crystal Matching algorithm in a sub-process relative to a directory named
        test_name in the test suite output directory. If the directory already exists it will be overwritten.
        If the --config flag is not included in the command line args it will be set to the output directory.
        :param test_name: Directory name used to store output in the test suite output dir.
        :param cmd_line_args: Command line arguments to be used for the sub-process call.
        :return: The path of the output directory.
        """

        test_output_dir = self._get_test_output_dir(test_name)
        if exists(test_output_dir):
            rmtree(test_output_dir)
        makedirs(test_output_dir)

        # Set a location for the config if unspecified
        if self.CONFIG_FLAG not in cmd_line_args:
            cmd_line_args = self.CONFIG_FLAG + " " + test_output_dir + " " + cmd_line_args

        # Run Crystal Matching Algorithm with command line arguments
        command = "python -m dls_imagematch.main_service " + cmd_line_args
        # TODO: Improve logging to associate this with the unit test
        print ("COMMAND: " + command)
        call(command, shell=True, cwd=test_output_dir)
        return test_output_dir

    # Testing Tools

    def failUnlessDirExists(self, directory_path):
        self.failUnless(exists(directory_path), "Directory does not exist: " + directory_path)
        self.failUnless(isdir(directory_path), "Not a directory: " + directory_path)

    def failUnlessDirContainsFileRegex(self, directory_path, regex_filename):
        for file_name in listdir(directory_path):
            if match(regex_filename, file_name):
                return
            self.fail("Could not find regex \"" + regex_filename + "\" in directory: " + directory_path)

    def failUnlessDirContainsFile(self, directory_path, file_name):
        self.failUnless(file_name in listdir(directory_path), "Could not find file \"" + file_name +
                        "\" in directory: " + directory_path)

    def failUnlessDirContainsFiles(self, directory_path, files):
        for file_name in files:
            self.failUnlessDirContainsFile(directory_path, file_name)
