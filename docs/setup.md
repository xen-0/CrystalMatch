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
    
* Some of these packages can be installed using `pip`. To do this:
    * Open cmd.exe (being sure to ‘Run as Administrator’)
    * Upgrade pip by typing `pip install –-upgrade pip`
    * Install enum by typing `pip install enum`
    
* The easiest way to install the other packages is to download the precompiled binaries from <http://www.lfd.uci.edu/~gohlke/pythonlibs/>. To install each one, open cmd.exe and type `pip install filename`. Download the most recent version of each for your version of Python (2.7, 32bit), except for OpenCV (you should get version 2 if available):
    * numpy-1.11.0+mkl-cp27-cp27m-win32.whl
    * opencv_python-2.4.12-cp27-none-win32.whl
    * PyQt4-4.11.4-cp27-none-win32.whl








