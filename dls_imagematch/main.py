import sys

from os.path import dirname
from sys import path
path.append(dirname(path[0]))


from PyQt4 import QtGui
from gui import VMXiCrystalMatchMainWindow

# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
if IS_BUNDLED:
    CONFIG_FILE = "./config-xtal.ini"
else:
    CONFIG_FILE = "../config-xtal.ini"


def main():
    app = QtGui.QApplication(sys.argv)
    ex = VMXiCrystalMatchMainWindow(CONFIG_FILE)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
