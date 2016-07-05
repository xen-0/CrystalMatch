from __future__ import division

from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDialogButtonBox, QPushButton

from dls_imagematch.util import Rectangle, Point


class SelectorFrame(QLabel):
    """ Special type of image frame that allows the user to draw a single rectangle to highlight a
    specific area on the image. The selected region can then be passed on to the client for other
    uses.

    The frame is initialized with the filename of an image file and cannot subsequently be used to
    display a different image. The frame only allows selection of single rectangle at a time. Drawing
    another rectangle will replace the first one.
    """
    def __init__(self, max_size, aligned_images, max_points, config):
        super(SelectorFrame, self).__init__()

        self._max_points = max_points

        self._selected_points = []
        self._rect_size = config.region_size.value()
        self._rect_color = config.color_xtal_img1.value()

        # Load image from file
        self._aligned_images = aligned_images
        self._selector_image = aligned_images.img1.to_color()
        self._original_size = self._selector_image.size

        # Calculate size of image frame - it is sized to maintain the aspect ratio
        #  but must be no larger than the maximum size
        self._display_size = self._calculate_display_size(max_size)
        self._display_scale = self._original_size[0] / self._display_size[0]

        self.setMaximumWidth(self._display_size[0])
        self.setMaximumHeight(self._display_size[1])

        # Display the Image
        self._display_image(self._selector_image)

    def _calculate_display_size(self, max_size):
        w, h = self._selector_image.size
        if w > h:
            width = max_size
            height = int(h / w * max_size)
        else:
            height = max_size
            width = int(w / h * max_size)

        return width, height

    def get_points(self):
        return self._selected_points

    def clear_points(self):
        self._selected_points = []
        self._display_image(self._selector_image)

    def _display_image(self, cvimg):
        """ Size the image appropriately and display it in the frame. """
        width, height = self._display_size
        pixmap = cvimg.to_qt_pixmap()
        pixmap = pixmap.scaled(QSize(width, height), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Set label size
        self.setPixmap(pixmap)

    def _add_point(self, point):
        self._selected_points.append(point)
        if len(self._selected_points) > self._max_points:
            self._selected_points = self._selected_points[-self._max_points:]
        self._refresh_image()

    def _refresh_image(self):
        img_copy = self._selector_image.copy()
        for point in self._selected_points:
            self._draw_point_rectangle(img_copy, point)

        self._display_image(img_copy)

    def _draw_point_rectangle(self, img, point):
        rect = Rectangle.from_center(point, self._rect_size, self._rect_size)
        img.draw_rectangle(rect, self._rect_color, thickness=1)
        img.draw_cross(point, self._rect_color, thickness=1, size=int(self._rect_size / 2))

    def mousePressEvent(self, QMouseEvent):
        """ Called when the mouse is clicked. Records the coords of the start position of a
        rectangle drag. """
        display_point = QMouseEvent.pos()
        display_point = Point(display_point.x(), display_point.y())
        image_point = display_point * self._display_scale
        self._add_point(image_point)


class PointSelectDialog(QDialog):
    """ Dialog that displays the Region Selector Frame and stores the result so that it may be
    retrieved by the caller.
    """
    def __init__(self, aligned_images, max_points, config):
        super(PointSelectDialog, self).__init__()
        self._init_ui(aligned_images, max_points, config)

    def _init_ui(self, aligned_images, max_points, config):
        self.setWindowTitle('Select Region of Interest from Image A')

        self._frame = SelectorFrame(1100, aligned_images, max_points, config)

        dialog_btns = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        dialog_btns.accepted.connect(self.accept)
        dialog_btns.rejected.connect(self.reject)

        btn_clear = QPushButton("Clear All")
        btn_clear.clicked.connect(self._frame.clear_points)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_clear)
        hbox.addWidget(dialog_btns)

        vbox = QVBoxLayout()
        vbox.addWidget(self._frame)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.show()

    def selected_points(self):
        return self._frame.get_points()
