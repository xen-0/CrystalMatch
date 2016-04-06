from __future__ import division

import os

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QPixmap, QLineEdit)

from dls_imagematch.gui import INPUT_DIR_ROOT
from dls_imagematch.util import Image


class ImageSelector(QtGui.QGroupBox):
    """ Widget that allows the user to select and view an image and to specify a
    corresponding real pixel size in micrometers (um).
    """
    def __init__(self, title):
        super(ImageSelector, self).__init__()

        self._file = None

        self._init_ui()
        self.setTitle(title)

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Load image button
        btn_load = QPushButton("Load Image")
        btn_load.clicked.connect(self._open_file_dialog)

        # Selection filename - displays filename of selected images (A and B)
        self._lbl_filename = QLabel("No Image Selected")
        self._lbl_filename.setFixedWidth(250)

        # Selection Image Frames
        self._frame = QLabel("No Image Selected")
        self._frame.setStyleSheet("color: red; font-size: 20pt; text-align: center; border:1px solid black")
        self._frame.setFixedWidth(350)
        self._frame.setFixedHeight(350)
        self._frame.setAlignment(Qt.AlignCenter)

        # Selection pixel size
        self._txt_px_size = QLineEdit()
        self._txt_px_size.setFixedWidth(60)

        # Widget Layout
        hbox_load_btn = QHBoxLayout()
        hbox_load_btn.addWidget(btn_load)
        hbox_load_btn.addWidget(self._lbl_filename)

        hbox_px_size = QHBoxLayout()
        hbox_px_size.addWidget(QLabel("Size per pixel:"))
        hbox_px_size.addWidget(self._txt_px_size)
        hbox_px_size.addWidget(QLabel("um"))
        hbox_px_size.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_load_btn)
        vbox.addWidget(self._frame)
        vbox.addLayout(hbox_px_size)

        self.setLayout(vbox)

    def setFile(self, filepath):
        """ Set the image file to display. """
        if filepath:
            self._file = filepath
            self._display_image(filepath)
            self._set_filename_label(filepath)

    def setPixelSize(self, size):
        """ Set the per pixel size for the image in micormeters. """
        self._txt_px_size.setText("{0:.5f}".format(size))

    def image(self):
        """ Get the wrapped image with appropriate pixel size. """
        return Image.from_file(self.file(), self.pixelSize())

    def file(self):
        """ Get the path of the selected file. """
        return self._file

    def pixelSize(self):
        """ Get the current real pixel size"""
        return float(self._txt_px_size.text())

    def _open_file_dialog(self):
        """ Display open dialog for Image slot A, load the selected image. """
        filepath = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', INPUT_DIR_ROOT))
        if filepath:
            self.setFile(filepath)

    def _display_image(self, filename):
        """ Display the selected image in the specified frame. """
        self._frame.clear()
        self._frame.setAlignment(Qt.AlignCenter)

        if filename is None:
            self._frame.setText("No Image Selected")
        elif os.path.isfile(filename):
            pixmap = QPixmap(filename)
            self._frame.setPixmap(pixmap.scaled(self._frame.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self._frame.setText("Image Not Found")

    def _set_filename_label(self, filepath):
        """ Display the filename in the specified label. """
        if filepath and filepath != "":
            self._lbl_filename.setText(filepath.split('/')[-1])
        else:
            self._lbl_filename.setText("No Image Selected")