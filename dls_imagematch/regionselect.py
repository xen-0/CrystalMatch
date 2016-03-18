import sys

from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel
from PyQt4.QtCore import Qt, QSize

from dls_imagematch.match.image import Image

INPUT_DIR_ROOT = "../test-images/"


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
        self.roi_image = None

        # Load image from file
        self.cvimg = Image.from_file(filepath, 100)
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
        """ Size the image appropriately and display it in the frame.
        """
        width, height = self.display_size
        pixmap = cvimg.to_qt_pixmap()
        pixmap = pixmap.scaled(QSize(width, height), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Set label size
        self.setPixmap(pixmap)

    def set_roi(self, display_roi):
        """ Set the selected region of interest (display it on image and store the area
        of the image for later use by clients.
        """
        # Convert display coords to image coords
        scale = self.size_image[0] / self.display_size[0]
        self.roi_image = list((scale*p for p in display_roi))

        # Display the image with the highlighted roi
        img_copy = self.cvimg.copy()
        img_copy.draw_rectangle(self.roi_image)
        self.size_display(img_copy)

    def mousePressEvent(self, QMouseEvent):
        """ Called when the mouse is clicked. Records the coords of the start position of a
        rectangle drag.
        """
        self.start_coords = QMouseEvent.pos()

    def mouseReleaseEvent(self, QMouseEvent):
        """ Called when the mouse is released after having been initially clicked in the frame
        area. Completes the region selection drag and causes the rectangle to be displayed on
        the image. This still works correctly if the drag finishes outside the bounds of the frame.
        """
        end_coords = QMouseEvent.pos()
        x1, y1 = self.start_coords.x(), self.start_coords.y()
        x2, y2 = end_coords.x(), end_coords.y()
        w, h = self.size().width(), self.size().height()
        self.start_coords = None

        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        x1, x2 = max(x1, 0), min(x2, w-1)
        y1, y2 = max(y1, 0), min(y2, h-1)

        # Paint the rectangle on the image
        display_roi = (x1, y1, x2, y2)
        self.set_roi(display_roi)


class RegionSelectGui(QMainWindow):
    def __init__(self):
        super(RegionSelectGui, self).__init__()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Select Region of Interest')

        # Image frame - displays the image currently selected in the file tree
        filepath = INPUT_DIR_ROOT + "441350000072/A01_13.jpg"
        self._image_frame = SelectorFrame(1000, filepath)

        hbox = QHBoxLayout()
        hbox.addWidget(self._image_frame)

        main_widget = QWidget()
        main_widget.setLayout(hbox)
        self.setCentralWidget(main_widget)
        self.show()



def main():
    app = QApplication(sys.argv)
    ex = RegionSelectGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()