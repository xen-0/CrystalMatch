from __future__ import division
from enum import Enum

from PyQt4.QtGui import (QPushButton, QLineEdit, QLabel, QGroupBox, QHBoxLayout)

from dls_imagematch.gui import RegionSelectDialog
from dls_imagematch.match import Overlayer, RegionMatcher
from dls_imagematch.util import Translate


class MatchStates(Enum):
    READY = 1
    MATCHING = 2
    MATCHING_COMPLETE = 3
    MATCHING_2ND = 4
    MATCHING_2ND_COMPLETE = 5


class RegionMatchControl(QGroupBox):
    """ Widget that allows control of the Region Matching process.
    """
    DEFAULT_X = "0.1"
    DEFAULT_Y = "0.4"

    def __init__(self, selector_a, selector_b, image_frame):
        super(RegionMatchControl, self).__init__()

        self.selector_a = selector_a
        self.selector_b = selector_b
        self.image_frame = image_frame

        self.img_a = None
        self.img_b = None
        self.scale_factor = 1
        self.matcher = None

        self._init_ui()
        self.setTitle("Region Matching")

        self.reset()

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Initial position guess
        self.txt_guess_x = QLineEdit()
        self.txt_guess_x.setFixedWidth(40)
        self.txt_guess_y = QLineEdit()
        self.txt_guess_y.setFixedWidth(40)

        # Matching function buttons
        self.btn_begin = QPushButton("Begin Match")
        self.btn_begin.clicked.connect(self._fn_begin_matching)
        self.btn_frame = QPushButton("Next Frame >>")
        self.btn_frame.clicked.connect(self._fn_next_frame)
        self.btn_scale = QPushButton("Next Scale >>")
        self.btn_scale.clicked.connect(self._fn_next_scale)
        self.btn_end = QPushButton("Skip To End >>")
        self.btn_end.clicked.connect(self._fn_skip_to_end)
        self.btn_region = QPushButton("Select Region")
        self.btn_region.clicked.connect(self._fn_select_region)
        self.btn_region.setEnabled(False)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self._fn_reset)

        # Create widget layout
        hbox_btns = QHBoxLayout()
        hbox_btns.addWidget(self.btn_reset)
        hbox_btns.addWidget(self.btn_begin)
        hbox_btns.addWidget(self.btn_frame)
        hbox_btns.addWidget(self.btn_scale)
        hbox_btns.addWidget(self.btn_end)
        hbox_btns.addWidget(self.btn_region)
        hbox_btns.addStretch(1)

        hbox_guess = QHBoxLayout()
        hbox_guess.addWidget(QLabel("X:"))
        hbox_guess.addWidget(self.txt_guess_x)
        hbox_guess.addWidget(QLabel("Y:"))
        hbox_guess.addWidget(self.txt_guess_y)
        hbox_guess.addStretch(1)
        hbox_guess.addLayout(hbox_btns)
        hbox_guess.addStretch(3)

        self.setLayout(hbox_guess)

    def match(self):
        """ Begin the matching process. """
        self._fn_begin_matching()

    def reset(self):
        """ Reset, clearing the current matching process. """
        self._fn_reset()

    def _set_state(self, state):
        """ Set the current state of the matching, enabling/disabling elements as appropriate. """
        self.gui_state = state

        self.btn_begin.setEnabled(False)
        self.btn_frame.setEnabled(False)
        self.btn_scale.setEnabled(False)
        self.btn_end.setEnabled(False)
        self.btn_region.setEnabled(False)

        if state == MatchStates.READY:
            self.btn_begin.setEnabled(True)
        elif state == MatchStates.MATCHING:
            self.btn_frame.setEnabled(True)
            self.btn_scale.setEnabled(True)
            self.btn_end.setEnabled(True)
        elif state == MatchStates.MATCHING_COMPLETE:
            self.btn_region.setEnabled(True)
        elif state == MatchStates.MATCHING_2ND:
            self.btn_frame.setEnabled(True)
            self.btn_end.setEnabled(True)
        elif state == MatchStates.MATCHING_2ND_COMPLETE:
            self.btn_begin.setEnabled(True)
        else:
            raise NotImplementedError

    ''' ----------------------
    BUTTON FUNCTIONS
    ------------------------'''
    def _fn_reset(self):
        """ Reset, clearing the current matching process. """
        self._set_state(MatchStates.READY)
        self.matcher = None
        self.img_a = None
        self.img_b = None

        self.txt_guess_x.setText(self.DEFAULT_X)
        self.txt_guess_y.setText(self.DEFAULT_Y)

        self.image_frame.clear()

    def _fn_begin_matching(self):
        """ Begin the matching procedure using the two selected images. """
        self._matching_primary()
        self._set_state(MatchStates.MATCHING)

    def _fn_next_frame(self):
        """ Advance to the next frame of the matching procedure. """
        if self.matcher is not None:
            self.matcher.next_frame()
            self._display_results()

    def _fn_next_scale(self):
        """ Advance to the next scale factor of the matching procedure. """
        if self.matcher is not None:
            self.matcher.skip_to_next_scale()
            self._display_results()

    def _fn_skip_to_end(self):
        """ Advance to the end of the matching procedure (dont show any frames). """
        if self.matcher is not None:
            self.matcher.skip_to_end()
            self._display_results()

    def _fn_select_region(self):
        """ For a completed primary matching procedure, select a sub-region (feature) to track. """
        region_image, roi = RegionSelectDialog.get_region(self, self.img_a)

        if region_image is not None:
            self._matching_secondary(self.img_b, region_image, roi)
            self._set_state(MatchStates.MATCHING_2ND)

    ''' ----------------------
    MATCHING FUNCTIONS
    ------------------------'''
    def _matching_primary(self):
        """ Vebing the primary matching procedure. """
        img_a, img_b = self._prepare_images()

        guess_x = float(self.txt_guess_x.text())
        guess_y = float(self.txt_guess_y.text())
        guess = Translate(guess_x*img_a.size[0], guess_y*img_a.size[1])

        self.matcher = RegionMatcher(img_a, img_b, guess)
        self._fn_next_frame()

    def _matching_secondary(self, imgA, imgB, roi):
        """ Begin secondary matching procedure (matching sub-regions from image B. """
        self.img_a = imgA
        self.img_b = imgB
        imgA_gray = imgA.make_gray()
        imgB_gray = imgB.make_gray()

        primary_transform = self.matcher.net_transform
        guessX = roi[0] - primary_transform.x
        guessY = roi[1] - primary_transform.y
        guess = Translate(guessX, guessY)

        self.matcher = RegionMatcher(imgA_gray, imgB_gray, guess, scales=(1,))
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

    def _display_results(self):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        transform = self.matcher.net_transform

        # Create image of B overlaid on A
        img = Overlayer.create_overlay_image(self.img_a, self.img_b, transform)
        self.image_frame.display_image(img)

        # Determine current transformation in real units (um)
        x, y = int(transform.x), int(transform.y)
        pixel_size = self.img_a.pixel_size
        x_um, y_um = int(x * pixel_size), int(y * pixel_size)
        offset_msg = "x={} um, y={} um ({} px, {} px)".format(x_um,y_um,x,y)

        if self.matcher.match_complete:
            # Print results
            status = "Region match complete: " + offset_msg
            self.image_frame.setStatusMessage(status)

            if self.gui_state == MatchStates.MATCHING:
                self._set_state(MatchStates.MATCHING_COMPLETE)
            elif self.gui_state == MatchStates.MATCHING_2ND:
                self._set_state(MatchStates.MATCHING_2ND_COMPLETE)
        else:
            status = "Region match in progress: " + offset_msg
            self.image_frame.setStatusMessage(status)