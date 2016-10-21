import sys

from os.path import dirname
from sys import path

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
    app = QApplication(sys.argv)
    VMXiCrystalMatchMainWindow(CONFIG_DIR)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
