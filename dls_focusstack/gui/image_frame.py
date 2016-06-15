from __future__ import division

from PyQt4.QtGui import QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QWidget
from PyQt4.QtCore import Qt, QEvent


class ImageFrame(QGroupBox):

    def __init__(self):
        super(ImageFrame, self).__init__()

        self._image = None

        self._init_ui()
        self.setTitle("Selected Image")

    def _init_ui(self):
        """ Create all the ui elements of the widget."""
        self._frame = QLabel()
        self._frame.setMouseTracking(True)
        self._frame.installEventFilter(self)
        self._frame.setStyleSheet("border:1px solid black")
        self._frame.setAlignment(Qt.AlignCenter)
        self._frame.setFixedWidth(900)
        self._frame.setFixedHeight(600)

        # Widget layout
        vbox = QVBoxLayout()
        vbox.addWidget(self._frame)

        self.setLayout(vbox)

    def clear(self):
        """ Reset the frame, clearing the image and status text. """
        self._image = None
        self._frame.clear()

    def display_image(self, image):
        """ Display the specified Image object in the frame, scaled to fit the frame and maintain aspect ratio. """
        self._image = image
        pixmap = image.to_qt_pixmap(self._frame.size())
        self._frame.setPixmap(pixmap)
