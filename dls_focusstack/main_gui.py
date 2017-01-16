import sys
from PyQt4.QtGui import QApplication

from gui.main_focus import FocusStackerMain

CONFIG_FILE = "../config/focus_stack.ini"


def main():
    app = QApplication(sys.argv)
    # noinspection PyUnusedLocal
    ex = FocusStackerMain(CONFIG_FILE)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
