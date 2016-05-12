from __future__ import division

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QLabel

from dls_imagematch.gui import RegionSelectDialog
from dls_imagematch.match import RegionMatcher, Overlayer
from dls_imagematch.util import Translate, Image


class SecondaryMatchControl(QGroupBox):
    """ Widget that allows control of the Secondary Matching process.
    """

    def __init__(self, selector_a, selector_b, image_frame):
        super(SecondaryMatchControl, self).__init__()

        self._selector_a = selector_a
        self._selector_b = selector_b
        self._image_frame = image_frame

        self._img_a = None
        self._img_b = None
        self._scale_factor = 1
        self._matcher = None

        self._init_ui()
        self.setTitle("Secondary Matching")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Matching function buttons
        self._btn_region = QPushButton("Select Region")
        self._btn_region.clicked.connect(self._fn_select_region)

        # Selection Image Frames
        self._frame = QLabel()
        self._frame.setStyleSheet("color: red; font-size: 20pt; text-align: center; border:1px solid black")
        self._frame.setFixedWidth(150)
        self._frame.setFixedHeight(150)
        self._frame.setAlignment(Qt.AlignCenter)

        # Create widget layout
        hbox_btns = QHBoxLayout()
        hbox_btns.addWidget(self._btn_region)
        hbox_btns.addWidget(self._frame)
        hbox_btns.addStretch(1)

        self.setLayout(hbox_btns)

    def match(self):
        """ Begin the matching process. """
        self._fn_begin_matching()

    ''' ----------------------
    BUTTON FUNCTIONS
    ------------------------'''
    def _fn_select_region(self):
        """ For a completed primary matching procedure, select a sub-region (feature) to track. """
        img_a = self._image_frame.last_img_a
        img_b = self._image_frame.last_img_b
        transform = self._image_frame.last_transform
        offset = (int(transform.x), int(transform.y))

        img, _ = Overlayer.get_overlap_regions(img_a, img_b, offset)
        img = Image(img, img_a.pixel_size)

        region_image, roi = RegionSelectDialog.get_region(img)

        if region_image is not None:
            self.display_image(region_image)
            pass  # self._matching_secondary(self.img_b, region_image, roi)

    ''' ----------------------
    MATCHING FUNCTIONS
    ------------------------'''
    def _matching_secondary(self, img_a, img_b, roi):
        """ Begin secondary matching procedure (matching sub-regions from image B. """
        self._img_a = img_a
        self._img_b = img_b
        img_a_gray = img_a.make_gray()
        img_b_gray = img_b.make_gray()

        primary_transform = self._matcher.net_transform
        guess_x = roi[0] - primary_transform.x
        guess_y = roi[1] - primary_transform.y
        guess = Translate(guess_x, guess_y)

        self._matcher = RegionMatcher(img_a_gray, img_b_gray, guess, scales=(1,))
        self._fn_next_frame()

    def _prepare_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Get the selected images
        self._img_a = self._selector_a.image()
        self._img_b = self._selector_b.image()

        # Resize the mov image so it has the same size per pixel as the ref image
        factor = self._img_b.pixel_size / self._img_a.pixel_size
        self._img_b = self._img_b.rescale(factor)
        self._scale_factor = factor

        return self._img_a.make_gray(), self._img_b.make_gray()

    def display_image(self, image):
        """ Display the specified Image object in the frame, scaled to fit the frame and maintain aspect ratio. """
        frame_size = self._frame.size()

        # Convert to a QT pixmap and display
        pixmap = image.to_qt_pixmap()
        scaled = pixmap.scaled(frame_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._frame.setPixmap(scaled)