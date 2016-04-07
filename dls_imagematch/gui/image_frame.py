from __future__ import division

from PyQt4.QtGui import QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QWidget
from PyQt4.QtCore import Qt, QEvent


class ImageFrame(QGroupBox):

    def __init__(self):
        super(ImageFrame, self).__init__()

        self.image = None
        self.scaled_size = (0,0)
        self.offset = (0,0)

        self._init_ui()
        self.setTitle("Results")

    def _init_ui(self):
        self.frame = QLabel()
        self.frame.setMouseTracking(True)
        self.frame.installEventFilter(self)
        self.frame.setStyleSheet("border:1px solid black")
        self.frame.setAlignment(Qt.AlignCenter)
        self.frame.setFixedWidth(800)
        self.frame.setFixedHeight(800)

        # Image frame status and cursor position labels
        self.lbl_status = QLabel("Status goes here")
        self.lbl_cursor = QLabel()

        hbox = QHBoxLayout()
        hbox.addWidget(self.lbl_status)
        hbox.addStretch(1)
        hbox.addWidget(self.lbl_cursor)

        # Widget layout
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.frame)

        self.setLayout(vbox)

    def clear(self):
        self.image = None
        self.scaled_size = (0,0)
        self.offset = (0,0)
        self.frame.clear()

    def setStatusMessage(self, message):
        self.lbl_status.setText(message)

    def display_image(self, image):
        self.image = image
        frame_size = self.frame.size()

        pixmap = image.to_qt_pixmap()
        scaled = pixmap.scaled(frame_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.frame.setPixmap(scaled)

        self.scaled_size = (scaled.width(), scaled.height())

        xOff = int((frame_size.width() - self.scaled_size[0]) / 2)
        yOff = int((frame_size.height() - self.scaled_size[1]) / 2)
        self.offset = (xOff, yOff)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove and source is self.frame:
            self.mouseMoveEvent(event)
            return False

        return QWidget.eventFilter(self, source, event)

    def mouseMoveEvent(self, QMouseEvent):
        if self.image is not None:
            coords = QMouseEvent.pos()
            x = coords.x() - self.offset[0]
            y = coords.y() - self.offset[1]

            x_perc = x / self.scaled_size[0]
            y_perc = y / self.scaled_size[1]

            real_size = self.image.size

            real_x_pixels = int(real_size[0] * x_perc)
            real_y_pixels = int(real_size[1] * y_perc)
            real_x_um = real_x_pixels * self.image.pixel_size
            real_y_um = real_y_pixels * self.image.pixel_size

            if 0 <= real_x_pixels <= real_size[0] and 0 <= real_y_pixels <= real_size[1]:
                position_txt = str(real_x_pixels) + " px, " + str(real_y_pixels) + " px (" + \
                    "{0:.2f}".format(real_x_um) + " um, " + "{0:.2f}".format(real_y_um) + " um)"
            else:
                position_txt = ""

            self.lbl_cursor.setText(position_txt)