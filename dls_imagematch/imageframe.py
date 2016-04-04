from __future__ import division
from PyQt4.QtGui import QLabel
from PyQt4.QtCore import Qt
from PyQt4 import QtCore


class ImageFrame(QLabel):
    coord_change = QtCore.pyqtSignal()

    def __init__(self):
        super(ImageFrame, self).__init__()
        self.image = None
        self.scaled_size = (0,0)
        self.offset = (0,0)

        self.setMouseTracking(True)

    def display_image(self, image):
        self.image = image
        frame_size = self.size()

        pixmap = image.to_qt_pixmap()
        scaled = pixmap.scaled(frame_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled)

        self.scaled_size = (scaled.width(), scaled.height())

        xOff = int((frame_size.width() - self.scaled_size[0]) / 2)
        yOff = int((frame_size.height() - self.scaled_size[1]) / 2)
        self.offset = (xOff, yOff)

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
                self.position_txt = str(real_x_pixels) + " px, " + str(real_y_pixels) + " px (" + \
                    "{0:.2f}".format(real_x_um) + " um, " + "{0:.2f}".format(real_y_um) + " um)"
            else:
                self.position_txt = ""

            self.coord_change.emit()