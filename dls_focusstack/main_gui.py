import sys
from PyQt4.QtGui import QApplication

from gui.main_focus import FocusStackerMain


def main():
    app = QApplication(sys.argv)
    # noinspection PyUnusedLocal
    ex = FocusStackerMain()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
