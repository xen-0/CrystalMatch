import sys
from PyQt4.QtGui import QApplication

from gui.main_focus import FocusStackerMain

CONFIG_DIR = "../config"
DEFAULT_INPUT_DIR = "../test-images/Focus Stacking/VMXI-AA005-G07-1-R0DRP1"
OUTPUT_DIR = "../test-output/focus_stacking/"


def main():
    app = QApplication(sys.argv)
    # noinspection PyUnusedLocal
    ex = FocusStackerMain(CONFIG_DIR, OUTPUT_DIR, DEFAULT_INPUT_DIR)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
