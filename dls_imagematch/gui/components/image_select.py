from __future__ import division

import os

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLabel, QPushButton, QHBoxLayout, QVBoxLayout

from dls_util.image import Image


class ImageSelector(QtGui.QGroupBox):
    """ Widget that allows the user to select and view an image.
    """
    signal_selected = QtCore.pyqtSignal(object)

    IMAGE_SIZE = 350
    BUTTON_TEXT = "Load Image"
    NO_IMAGE_LABEL = "No Image Selected"

    def __init__(self, title, gui_config):
        super(ImageSelector, self).__init__()

        self._image = None
        self._gui_config = gui_config

        self._init_ui()
        self.setTitle(title)

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Load image button
        self._btn_load = QPushButton(self.BUTTON_TEXT)
        self._btn_load.clicked.connect(self._select_image_from_file_dialog)

        # Selection filename - displays filename of selected images (A and B)
        self._lbl_filename = QLabel(self.NO_IMAGE_LABEL)
        self._lbl_filename.setFixedWidth(250)

        # Selection Image Frames
        self._frame = QLabel(self.NO_IMAGE_LABEL)
        self._frame.setStyleSheet("color: red; font-size: 20pt; text-align: center; border:1px solid black")
        self._frame.setFixedWidth(self.IMAGE_SIZE)
        self._frame.setFixedHeight(self.IMAGE_SIZE)
        self._frame.setAlignment(Qt.AlignCenter)

        # Widget Layout
        hbox_load_btn = QHBoxLayout()
        hbox_load_btn.addWidget(self._btn_load)
        hbox_load_btn.addWidget(self._lbl_filename)
        hbox_load_btn.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_load_btn)
        vbox.addWidget(self._frame)

        self.setLayout(vbox)

    def set_button_visible(self, visible):
        self._btn_load.setVisible(visible)
        self._lbl_filename.setVisible(visible)

    def image(self):
        return self._image

    def set_image(self, image):
        self._image = image
        self._display_image(image)
        self._display_filename_label(image.file)

    def _select_image_from_file_dialog(self):
        """ Display open dialog for Image slot A, load the selected image. """
        if self._gui_config is not None:
            input_dir = self._gui_config.input_dir.value()
        else:
            input_dir = os.getcwd()

        file_path = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', input_dir))

        if file_path:
            image = Image.from_file(file_path)
            self.set_image(image)
            self.signal_selected.emit(self._image)

    def _display_image(self, image):
        """ Display the selected image in the frame. """
        if not isinstance(image, Image):
            raise TypeError("Argument must be instance of {}".format(Image.__name__))

        self._frame.clear()
        self._frame.setAlignment(Qt.AlignCenter)

        if image is None:
            self._frame.setText("No Image Selected")
        else:
            pixmap = image.to_qt_pixmap(self._frame.size())
            self._frame.setPixmap(pixmap)

    def _display_filename_label(self, file_path):
        """ Display the filename in the filename label. """
        if file_path and file_path != "":
            self._lbl_filename.setText(file_path.split('/')[-1])
        else:
            self._lbl_filename.setText("No Image Selected")
