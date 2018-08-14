from __future__ import division

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QGroupBox, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QIcon, QPushButton

from dls_util.imaging import Image


class ImageList(QGroupBox):
    """ Widget that allows control of the Secondary Matching process.
    """
    signal_selected = QtCore.pyqtSignal(object)

    NUM_FRAMES = 10
    FRAME_SIZE = 75

    FRAME_STYLE = "color: {0}; font-size: 16pt; text-align: center; border:1px solid {0};"

    def __init__(self):
        super(ImageList, self).__init__()

        self._init_ui()
        self.setTitle("Images")
        self._image_files = None

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        self._list = QListWidget()

        self._list.itemSelectionChanged.connect(self._new_selection_made)

        btn_check_all = QPushButton("Check All")
        btn_check_all.clicked.connect(self._fn_check_all)
        btn_check_none = QPushButton("Check None")
        btn_check_none.clicked.connect(self._fn_check_none)

        hbox_btns = QHBoxLayout()
        hbox_btns.addWidget(btn_check_all)
        hbox_btns.addWidget(btn_check_none)
        hbox_btns.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(self._list)
        vbox.addLayout(hbox_btns)

        self.setLayout(vbox)

    def set_images(self, image_files):
        self._list.clear()
        self._image_files = []
        for file_path in image_files:
            self._image_files.append(file(file_path))
            item = ImageItem(file_path)
            self._list.addItem(item)

    def _new_selection_made(self):
        items = self._list.selectedItems()
        if len(items) > 0:
            self.signal_selected.emit(items[0].image)

    def _fn_check_all(self):
        for i in range(self._list.count()):
            item = self._list.item(i)
            item.setCheckState(2)

    def _fn_check_none(self):
        for i in range(self._list.count()):
            item = self._list.item(i)
            item.setCheckState(0)

    def get_checked_images(self):
        checked = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.checkState() == 2:
                checked.append(self._image_files[i])

        return checked


class ImageItem(QListWidgetItem):
    def __init__(self, filepath):
        super(ImageItem, self).__init__()
        self._filepath = filepath
        self.image = Image.from_file(filepath)

        filename = filepath.split("\\")[-1]
        self.setText(filename)
        self.setCheckState(True)
        self.setCheckState(2)

        icon = QIcon()
        icon.addPixmap(self.image.to_qt_pixmap(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setIcon(icon)
