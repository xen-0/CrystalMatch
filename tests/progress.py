from __future__ import division

import sys
import time

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QWidget, QMainWindow, QIcon, QHBoxLayout, QVBoxLayout, QApplication, QAction, QPushButton


class ProgressTest(QMainWindow):
    def __init__(self):
        super(ProgressTest, self).__init__()


        self.init_ui()

    def init_ui(self):
        """ Create all elements of the user interface. """
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Test')

        btn = QPushButton("Push Me")
        btn.clicked.connect(self.onStart)

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(btn)
        hbox.addStretch()

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)

        main_widget = QWidget()
        main_widget.setLayout(vbox)
        self.setCentralWidget(main_widget)
        self.show()

    def onStart(self):
        my_dialog = ProgressDialog()
        long_task = TaskThread()
        long_task.taskFinished.connect(my_dialog.onFinished)
        long_task.start()
        my_dialog.exec_()


class ProgressDialog(QtGui.QDialog):

    def __init__(self):
        super(ProgressDialog, self).__init__()

        self._init_ui()

    def _init_ui(self):
        """ Create the basic elements of the user interface.
        """
        self.setGeometry(100, 100, 450, 400)
        self.setWindowTitle('Progress')
        self.setWindowIcon(QtGui.QIcon('web.png'))

        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setRange(0, 0)

        vbox = QVBoxLayout()
        vbox.addWidget(self.progressBar)

        self.setLayout(vbox)

    def onFinished(self):
        # Stop the pulsation
        self.progressBar.setRange(0, 1)
        self.close()


class TaskThread(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal()
    def run(self):
        time.sleep(3)
        self.taskFinished.emit()


def main():
    app = QApplication(sys.argv)
    ex = ProgressTest()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
