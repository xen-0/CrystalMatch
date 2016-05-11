from __future__ import division

from PyQt4.QtGui import (QPushButton, QGroupBox, QHBoxLayout)

from dls_imagematch.gui import RegionSelectDialog
from dls_imagematch.match import RegionMatcher
from dls_imagematch.util import Translate


class SecondaryMatchControl(QGroupBox):
    """ Widget that allows control of the Secondary Matching process.
    """

    def __init__(self, selector_a, selector_b, image_frame):
        super(SecondaryMatchControl, self).__init__()

        self.selector_a = selector_a
        self.selector_b = selector_b
        self.image_frame = image_frame

        self.img_a = None
        self.img_b = None
        self.scale_factor = 1
        self.matcher = None

        self._init_ui()
        self.setTitle("Secondary Matching")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Matching function buttons
        self.btn_region = QPushButton("Select Region")
        self.btn_region.clicked.connect(self._fn_select_region)
        self.btn_region.setEnabled(False)

        # Create widget layout
        hbox_btns = QHBoxLayout()
        hbox_btns.addWidget(self.btn_region)
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
        region_image, roi = RegionSelectDialog.get_region(self.img_a)

        if region_image is not None:
            pass  # self._matching_secondary(self.img_b, region_image, roi)

    ''' ----------------------
    MATCHING FUNCTIONS
    ------------------------'''
    def _matching_secondary(self, img_a, img_b, roi):
        """ Begin secondary matching procedure (matching sub-regions from image B. """
        self.img_a = img_a
        self.img_b = img_b
        img_a_gray = img_a.make_gray()
        img_b_gray = img_b.make_gray()

        primary_transform = self.matcher.net_transform
        guess_x = roi[0] - primary_transform.x
        guess_y = roi[1] - primary_transform.y
        guess = Translate(guess_x, guess_y)

        self.matcher = RegionMatcher(img_a_gray, img_b_gray, guess, scales=(1,))
        self._fn_next_frame()

    def _prepare_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Get the selected images
        self.img_a = self.selector_a.image()
        self.img_b = self.selector_b.image()

        # Resize the mov image so it has the same size per pixel as the ref image
        factor = self.img_b.pixel_size / self.img_a.pixel_size
        self.img_b = self.img_b.rescale(factor)
        self.scale_factor = factor

        return self.img_a.make_gray(), self.img_b.make_gray()
