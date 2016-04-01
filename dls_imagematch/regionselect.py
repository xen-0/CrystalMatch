from __future__ import division

from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from enum import Enum

from dls_imagematch.image import Image

INPUT_DIR_ROOT = "../test-images/"


class SelectorMode(Enum):
    SINGLE_POINT = 1
    REGION = 2


class SelectorFrame(QLabel):
    """ Special type of image frame that allows the user to draw a single rectangle to highlight a
    specific area on the image. The selected region can then be passed on to the client for other
    uses.

    The frame is initialized with the filename of an image file and cannot subsequently be used to
    display a different image. The frame only allows selection of single rectangle at a time. Drawing
    another rectangle will replace the first one.
    """
    def __init__(self, max_size, filepath):
        super(SelectorFrame, self).__init__()
        self.max_size = max_size

        self.start_coords = None
        self.roi = None
        self.image_region = None

        # Set selection mode
        self.mode = SelectorMode.REGION

        # Load image from file
        self.cvimg = Image.from_file(filepath)
        self.size_image = self.cvimg.size

        # Calculate size of image frame - it is sized to maintain the aspect ratio
        #  but must be no larger than the maximum size
        w, h = self.cvimg.size
        if w > h:
            width = self.max_size
            height = int(h / w * self.max_size)
        else:
            height = self.max_size
            width = int(w / h * self.max_size)
        self.display_size = (width, height)
        self.setMaximumWidth(width)
        self.setMaximumHeight(height)

        # Display the Image
        self.size_display(self.cvimg)

    def size_display(self, cvimg):
        """ Size the image appropriately and display it in the frame. """
        width, height = self.display_size
        pixmap = cvimg.to_qt_pixmap()
        pixmap = pixmap.scaled(QSize(width, height), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Set label size
        self.setPixmap(pixmap)

    def set_roi(self, display_roi):
        """ Set the selected region of interest (display it on image and store the area
        of the image for later use by clients. """
        # Convert display coords to image coords
        scale = self.size_image[0] / self.display_size[0]
        self.roi = list((scale * p for p in display_roi))

        # Display the image with the highlighted roi
        img_copy = self.cvimg.copy()
        img_copy.draw_rectangle(self.roi)
        self.size_display(img_copy)

        # Store the selected region as a separate image
        self.image_region = self.cvimg.sub_image(self.roi).copy()

    def mousePressEvent(self, QMouseEvent):
        """ Called when the mouse is clicked. Records the coords of the start position of a
        rectangle drag. """
        self.start_coords = QMouseEvent.pos()

    def mouseReleaseEvent(self, QMouseEvent):
        """ Called when the mouse is released after having been initially clicked in the frame
        area. Completes the region selection drag and causes the rectangle to be displayed on
        the image. This still works correctly if the drag finishes outside the bounds of the
        frame. """
        end_coords = QMouseEvent.pos()

        if self.mode == SelectorMode.REGION:
            x1, y1 = self.start_coords.x(), self.start_coords.y()
            x2, y2 = end_coords.x(), end_coords.y()
        elif self.mode == SelectorMode.SINGLE_POINT:
            roi_size = 10
            x1, y1 = end_coords.x() - roi_size, end_coords.y() - roi_size
            x2, y2 = end_coords.x() + roi_size, end_coords.y() + roi_size
        else:
            raise NotImplementedError

        w, h = self.size().width(), self.size().height()

        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        x1, x2 = max(x1, 0), min(x2, w-1)
        y1, y2 = max(y1, 0), min(y2, h-1)

        # Paint the rectangle on the image
        display_roi = (x1, y1, x2, y2)
        self.set_roi(display_roi)

        self.start_coords = None


class RegionSelectDialog(QDialog):
    def __init__(self, filename):
        super(RegionSelectDialog, self).__init__()
        self.init_ui(filename)

    def init_ui(self, filename):
        self.setWindowTitle('Select Region of Interest')

        self.selector_frame = SelectorFrame(900, filename)
        self.selector_frame.mode = SelectorMode.SINGLE_POINT

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        vbox = QVBoxLayout()
        vbox.addWidget(self.selector_frame)
        vbox.addWidget(buttons)

        self.setLayout(vbox)
        self.show()

    def roi(self):
        return self.selector_frame.image_region, self.selector_frame.roi

    @staticmethod
    def get_region(parent, filename):
        dialog = RegionSelectDialog(filename)
        result = dialog.exec_()
        region_image, roi = dialog.roi()
        return region_image, roi