import os

from pkg_resources import require
require("numpy==1.11.1")
import sys
from PyQt4.QtGui import QApplication

from gui.main_focus import FocusStackerMain

CONFIG_DIR = os.path.join('..', 'config')
DEFAULT_INPUT_DIR = os.path.join('..','test-images', 'Focus', 'VMXI-AA0019-H01-1-R0DRP1', 'levels')
OUTPUT_DIR = os.path.join('..', 'test-output', 'focus_stacking')


def main():
    app = QApplication(sys.argv)
    # noinspection PyUnusedLocal
    ex = FocusStackerMain(CONFIG_DIR, OUTPUT_DIR, DEFAULT_INPUT_DIR)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
