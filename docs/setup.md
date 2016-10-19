Recommended IDE
===============
This application has been developed using the JetBrains PyCharm IDE. While the source code can be used separately using the information below, Pycharm is a highly recommended development tool.

A free community edition of Pycharm is available from <https://www.jetbrains.com/pycharm/>; the professional edition has additional features which are useful but not essential to this project.

The configuration files for Pycharm are located in `.idea` directories in the repository. The root level directory also contains example run configurations and should be detected automatically when opening the project with Pycharm for the first time.

Using the Source Code - Windows
===============================
This application is written in Python (v2.7) and was developed under Windows but should be portable to other platforms.

The following steps will help you prepare an appropriate Python environment to run this program. These instructions assume that you will use the 32-bit version on Python 2.7.11. The program should also run correctly under other versions of Python (e.g. 3.4, 3.5, 64bit), however due to an error in later versions of OpenCV (v3) on Windows, seem features may not work correctly.

* Install the appropriate version of Python by downloading the Windows binary installer from <https://www.python.org/downloads/release/python-2711/>
    * You want the one labelled 'Windows x86 MSI installer'
    * During installation, make sure you check ‘Add python.exe to system path’.
    
* The following packages are required:
    * enum
    * numpy
    * OpenCV
    * PyQt4
    * mock (standard in Python v3.3+ but required for unit tests to run under v2.7)
    
* Some of these packages can be installed using `pip`. To do this:
    * Open cmd.exe (being sure to ‘Run as Administrator’)
    * Upgrade pip by typing `pip install –-upgrade pip`
    * Install enum by typing `pip install enum`
    
* The easiest way to install the other packages is to download the precompiled binaries from <http://www.lfd.uci.edu/~gohlke/pythonlibs/>. To install each one, open cmd.exe and type `pip install filename`. Download the most recent version of each for your version of Python (2.7, 32bit). For OpenCV you should get version 2 rather than 3 if available, as some features may not work under version 3:
    * numpy-1.11.0+mkl-cp27-cp27m-win32.whl
    * opencv_python-2.4.12-cp27-none-win32.whl
    * PyQt4-4.11.4-cp27-none-win32.whl


Running from the Command Line
=============================

To run the service from the command line the root directory of project (ie: the root of the git repository) must be added to the `PYTHONPATH` environment variable.

The service can be run without this step but the `PYTHONPATH` variable must be defined in the command as follows:

```
PYTHONPATH="[path-to-source-directory]" python [./path/to/script]main_service.py [marked-image] [target-image] [x,y ...]
```

NOTE: A `config` directory will be added to the current working directory unless an alternate path is specified using the flag `--config ./path/to/dir`.


Unit Testing
============

Unit tests have been in-lined with the module structure - unit tests for a class will be located in a file named `test_[file name]`.

In order to run unit tests in Pycharm right-click on a python module and select "Run unittests" - this will run all unit tests in the module and any sub-modules. If you are not using Pycharm the `nose` library can be used to similar effect.

The professional (paid licence) edition of Pycharm incorporates the `coverage` Python library which provides a rough indication of how much of the code is covered by unit tests.  The `coverage` tool can be run outside of Pycharm but has not been tested.

**NOTE:** Avoid running unit tests for the entire repository as system tests also use the python `unittest` framework and take considerably longer to run.

System Tests
============

At the time of writing system testing does not cover the application exhaustively - tests were added late in the development process and have been written to cover features as they are added or updated.

System tests are located in the `system-tests` directory of the repository. A custom System Testing Framework has been constructed which runs the algorithm and outputs the results to output directories named `sys_test_output` which are ignored by the git repository.  The framework should be self-documenting and will not be described here in detail.

The System Test Framework is based on the standard python `unittest` library (note that this will need to be installed during setup for Python 2.7). System Tests can be run in the same manner as unit tests but may require the `PYTHONPATH` variable to be added if you are not using Pycharm.

The base `SystemTest` class extends `unittest.TestCase` - each `test_` method in a unit test class should cause the application to run once using the method `run_crystal_matching_test(test_name, cmd_line_args)`.  This will generate an output directory which contains the stdout and stderr in file form as well as the config directory and any file system output from the application itself.  The parent class `SystemTest` provides a series of helper methods which are primarily aimed at rapid testing of content in the output directory (including stdout).

