import logging
import sys

from os.path import dirname
from sys import path, stdout

from PyQt4.QtGui import QApplication

from gui import VMXiCrystalMatchMainWindow
path.append(dirname(path[0]))

# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
if IS_BUNDLED:
    CONFIG_DIR = "./config/"
else:
    CONFIG_DIR = "../config/"


def main():

    # Set logging level
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(stdout)
    ch.setLevel(logging.DEBUG)
    root.addHandler(ch)

    # Run GUI
    app = QApplication(sys.argv)
    VMXiCrystalMatchMainWindow(CONFIG_DIR)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
