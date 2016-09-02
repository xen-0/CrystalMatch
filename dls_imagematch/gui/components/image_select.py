from __future__ import division

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit

from dls_imagematch.util import Image, Color


class ImageSelector(QtGui.QGroupBox):
    """ Widget that allows the user to select and view an image and to specify a
    corresponding real pixel size in micrometers (um).
    """
    signal_selected = QtCore.pyqtSignal(object)

    IMAGE_SIZE = 350
    BUTTON_TEXT = "Load Image"
    NO_IMAGE_LABEL = "No Image Selected"

    PIXEL_SIZE_OK_COLOR = Color.White()
    PIXEL_SIZE_BAD_COLOR = Color(255, 128, 128)

    def __init__(self, title, gui_config):
        super(ImageSelector, self).__init__()

        self._image = None
        self._pixel_size = 1.0
        self._gui_config = gui_config

        self._init_ui()
        self.setTitle(title)

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Load image button
        btn_load = QPushButton(self.BUTTON_TEXT)
        btn_load.clicked.connect(self._select_image_from_file_dialog)

        # Selection filename - displays filename of selected images (A and B)
        self._lbl_filename = QLabel(self.NO_IMAGE_LABEL)
        self._lbl_filename.setFixedWidth(250)

        # Selection Image Frames
        self._frame = QLabel(self.NO_IMAGE_LABEL)
        self._frame.setStyleSheet("color: red; font-size: 20pt; text-align: center; border:1px solid black")
        self._frame.setFixedWidth(self.IMAGE_SIZE)
        self._frame.setFixedHeight(self.IMAGE_SIZE)
        self._frame.setAlignment(Qt.AlignCenter)

        # Selection pixel size
        self._txt_px_size = QLineEdit()
        self._txt_px_size.setFixedWidth(60)
        self._txt_px_size.textChanged.connect(self._pixel_size_text_changed)

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

    def image(self):
        return self._image

    def set_image(self, image):
        self._image = image
        self._pixel_size = image.pixel_size

        self._display_image(image)
        self._display_filename_label(image.file)
        self._display_pixel_size(image.pixel_size)

    def _set_image_pixel_size(self, pixel_size):
        raw_img = self._image.img
        filename = self._image.file

        self._image = Image(raw_img, pixel_size)
        self._image.file = filename
        self._pixel_size = pixel_size

    def _pixel_size_text_changed(self):
        pixel_txt = self._txt_px_size.text()
        color = self.PIXEL_SIZE_OK_COLOR

        try:
            pixel_float = float(pixel_txt)
            self._set_image_pixel_size(pixel_float)
        except ValueError:
            color = self.PIXEL_SIZE_BAD_COLOR

        self._txt_px_size.setStyleSheet("background-color:{}".format(color.to_hex()))

    def _select_image_from_file_dialog(self):
        """ Display open dialog for Image slot A, load the selected image. """
        input_dir = self._gui_config.input_dir.value()
        filepath = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', input_dir))

        if filepath:
            image = Image.from_file(filepath, self._pixel_size)
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

    def _display_filename_label(self, filepath):
        """ Display the filename in the filename label. """
        if filepath and filepath != "":
            self._lbl_filename.setText(filepath.split('/')[-1])
        else:
            self._lbl_filename.setText("No Image Selected")

    def _display_pixel_size(self, size):
        """ Set the per pixel size for the image in micrometers. """
        self._txt_px_size.setText("{0:.5f}".format(size))

