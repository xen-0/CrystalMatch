import sys
import os
from PyQt4 import QtGui, QtCore

from PyQt4.QtGui import (QFileSystemModel, QTreeView)
from PyQt4.QtCore import QDir, Qt


INPUT_DIR_ROOT = "../test-images/old/"


class ImageMatcher(QtGui.QMainWindow):
    def __init__(self):
        super(ImageMatcher, self).__init__()

        self._fileTreeView = None
        self.model = None

        self._init_ui()

    def _init_ui(self):
        self.setGeometry(100, 100, 1020, 650)
        self.setWindowTitle('Diamond VMXi Image Matching')
        self.setWindowIcon(QtGui.QIcon('web.png'))

        self.model = QFileSystemModel()
        # You can setRootPath to any path.
        self.model.setRootPath(INPUT_DIR_ROOT)
        # List of views.
        self._fileTreeView = QTreeView()
        self._fileTreeView.setModel(self.model)
        self._fileTreeView.setRootIndex(self.model.index(INPUT_DIR_ROOT))
        self._fileTreeView.setFixedWidth(300)
        self._fileTreeView.setFixedHeight(600)

        self._fileTreeView.setColumnWidth(0, 175)
        self._fileTreeView.setColumnWidth(1, 25)
        self._fileTreeView.hideColumn(3)
        self._fileTreeView.hideColumn(2)

        self._fileTreeView.connect(self._fileTreeView.selectionModel(),
                                   QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
                                   self.new_file_selected)

        # Image frame - displays image of the currently selected image
        self._imageFrame = QtGui.QLabel()
        self._imageFrame.setStyleSheet("background-color: black; color: red; font-size: 30pt; text-align: center")
        self._imageFrame.setFixedWidth(600)
        self._imageFrame.setFixedHeight(600)

        # Create layout
        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.addWidget(self._fileTreeView)
        hbox.addWidget(self._imageFrame)
        hbox.addStretch(1)

        main_widget = QtGui.QWidget()
        main_widget.setLayout(hbox)
        self.setCentralWidget(main_widget)
        self.show()

    def new_file_selected(self, selected, deselected):
        indexes = selected.indexes()
        index = indexes[0]
        filepath = self.model.filePath(index)
        print(filepath)

        self._display_image(filepath)

    def _display_image(self, filename):
        self._imageFrame.clear()
        self._imageFrame.setAlignment(QtCore.Qt.AlignCenter)

        if filename is None:
            self._imageFrame.setText("No Scan Selected")
        elif os.path.isfile(filename):
            pixmap = QtGui.QPixmap(filename)
            self._imageFrame.setPixmap(pixmap.scaled(self._imageFrame.size(),
                                                     QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self._imageFrame.setText("Image Not Found")


def main():
    app = QtGui.QApplication(sys.argv)
    ex = ImageMatcher()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
