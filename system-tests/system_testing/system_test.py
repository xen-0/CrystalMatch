from shutil import rmtree
from subprocess import call
from unittest import TestCase
from os.path import exists, isdir, join, splitext

from os import mkdir, chdir


class SystemTest(TestCase):
    """
    Parent class which provides a framework to run System Tests using the standard Python unittest libraries.
    A system test case should extend this class and include the boilerplate code below to run the
    Crystal Matching algorithm.  The command_line_args variable should be altered to create the appropriate
    test conditions.

    @classmethod
    def setUpClass(cls):
        command_line_args = "../input/A01_1.jpg ../input/A01_2.jpg 1068,442 1191,1415"
        SystemTest._run_crystal_match(realpath(__file__), command_line_args)

    When a system test is run a test directory with the same name is created (if one does not already exist for input)
    - within this creates an output directory which is ignored by git.  All output log and config files are added
    to this directory.
    """

    OUTPUT_DIR_NAME = "sys_test_output"
    CONFIG_FLAG = "--config"

    @classmethod
    def _run_crystal_match(cls, test_file_path, cmd_line_args):
        """
        Runs the Crystal Matching application in a directory with the same name as the test file generating a
        set of output files for System Testing.
        :param test_file_path:  This must be the result of os.path.realpath(__file__) run in a child of this class.  It
        is used to construct the filepath to the testing directory.
        :param cmd_line_args: A string which provides the command line arguments to use when running the program.
        """
        # Assert that the test directory exists
        test_dir, extension = splitext(test_file_path)
        err_msg = "A test directory with the same name as the test file must be present in the directory: MISSING: "
        assert exists(test_dir), err_msg + test_dir
        assert isdir(test_dir), err_msg + test_dir

        # Create output directory - delete any existing
        output_dir = join(test_dir, cls.OUTPUT_DIR_NAME)
        if exists(output_dir):
            rmtree(output_dir)
        mkdir(output_dir)

        # Set a location for the config if unspecified
        if cls.CONFIG_FLAG not in cmd_line_args:
            cmd_line_args = cls.CONFIG_FLAG + " " + output_dir + " " + cmd_line_args

        # Run Crystal Matching Algorithm with command line arguments
        chdir(output_dir)
        call("python -m dls_imagematch.main_service " + cmd_line_args, shell=True, cwd=output_dir)
