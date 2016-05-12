from __future__ import division

import cv2
from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from enum import Enum

from dls_imagematch.util import Image


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
    ROI_SIZE = 20

    def __init__(self, max_size, aligned_images):
        super(SelectorFrame, self).__init__()
        self.max_size = max_size

        self.start_coords = None
        self.roi = None
        self.image_region = None

        # Set selection mode
        self.mode = SelectorMode.REGION

        # Load image from file
        self._selector_image = None
        self._aligned_images = aligned_images
        self._prepare_selector_image()
        self._original_size = self._selector_image.size

        # Calculate size of image frame - it is sized to maintain the aspect ratio
        #  but must be no larger than the maximum size
        w, h = self._selector_image.size
        if w > h:
            width = self.max_size
            height = int(h / w * self.max_size)
        else:
            height = self.max_size
            width = int(w / h * self.max_size)
        self._display_size = (width, height)
        self._display_scale = self._original_size[0] / self._display_size[0]

        self.setMaximumWidth(width)
        self.setMaximumHeight(height)

        # Display the Image
        self.size_display(self._selector_image)

    def _prepare_selector_image(self):
        images = self._aligned_images

        img_a = images.img_a
        overlap_img_a, _ = images.overlap_images()
        x, y = images.pixel_offset()

        # Make faded background
        blank_image = Image.blank(img_a.size[0], img_a.size[1])
        blended = cv2.addWeighted(img_a.img, 0.5, blank_image.img, 0.5, 0)
        background = Image(blended, img_a.pixel_size)
        background.paste(overlap_img_a, x, y)

        self._selector_image = background

    def size_display(self, cvimg):
        """ Size the image appropriately and display it in the frame. """
        width, height = self._display_size
        pixmap = cvimg.to_qt_pixmap()
        pixmap = pixmap.scaled(QSize(width, height), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Set label size
        self.setPixmap(pixmap)

    def set_roi(self, display_roi):
        """ Set the selected region of interest (display it on image and store the area
        of the image for later use by clients. """
        # Convert display coords to image coords
        scale = self._display_scale
        self.roi = list((scale * p for p in display_roi))

        # Display the image with the highlighted roi
        img_copy = self._selector_image.copy()
        img_copy.draw_rectangle(self.roi)
        self.size_display(img_copy)

        # Store the selected region as a separate image
        self.image_region = self._selector_image.sub_image(self.roi).copy()

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
            # convert the roi size (in um) to one in display image pixels
            roi_size = self.ROI_SIZE / (self._display_scale * self._selector_image.pixel_size)
            print(self._display_scale, self._selector_image.pixel_size, roi_size)
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
    """ Dialog that displays the Region Selector Frame and stores the result so that it may be
    retrieved by the caller.
    """
    def __init__(self, aligned_images):
        super(RegionSelectDialog, self).__init__()
        self._init_ui(aligned_images)

    def _init_ui(self, aligned_images):
        self.setWindowTitle('Select Region of Interest')

        self.selector_frame = SelectorFrame(900, aligned_images)
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

    def region_of_interest(self):
        """ The selected section of the image and the rectangle (x1, y1, x2, y2) that was drawn on
        the selector frame. """
        return self.selector_frame.image_region, self.selector_frame.roi

    @staticmethod
    def get_region(filename):
        """ Display a dialog and return the result to the caller. """
        dialog = RegionSelectDialog(filename)
        _ = dialog.exec_()
        region_image, rectangle = dialog.region_of_interest()
        return region_image, rectangle
