from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import (QPushButton, QLineEdit, QLabel, QGroupBox, QHBoxLayout)

from dls_imagematch.match import RegionMatcher, AlignedImages
from dls_imagematch.util import Translate


class RegionMatchControl(QGroupBox):
    """ Widget that allows control of the Region Matching process.
    """
    DEFAULT_X = "0"
    DEFAULT_Y = "0"

    signal_aligned = QtCore.pyqtSignal(object)

    def __init__(self, selector_a, selector_b):
        super(RegionMatchControl, self).__init__()

        self._selector_a = selector_a
        self._selector_b = selector_b

        self._img1 = None
        self._img2 = None
        self._scale_factor = 1
        self._matcher = None

        self._init_ui()
        self._set_is_matching(False)
        self.setTitle("Region Matching")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Initial position guess
        self._txt_guess_x = QLineEdit()
        self._txt_guess_x.setFixedWidth(40)
        self._txt_guess_x.setText(self.DEFAULT_X)
        self._txt_guess_y = QLineEdit()
        self._txt_guess_y.setFixedWidth(40)
        self._txt_guess_y.setText(self.DEFAULT_Y)

        # Matching function buttons
        self._btn_begin = QPushButton("Begin Match")
        self._btn_begin.clicked.connect(self._fn_begin_matching)
        self._btn_frame = QPushButton("Next Frame >>")
        self._btn_frame.clicked.connect(self._fn_next_frame)
        self._btn_end = QPushButton("Skip To End >>")
        self._btn_end.clicked.connect(self._fn_skip_to_end)

        # Create widget layout
        hbox_btns = QHBoxLayout()
        hbox_btns.addWidget(self._btn_begin)
        hbox_btns.addWidget(self._btn_frame)
        hbox_btns.addWidget(self._btn_end)
        hbox_btns.addStretch(1)

        hbox_guess = QHBoxLayout()
        hbox_guess.addWidget(QLabel("X:"))
        hbox_guess.addWidget(self._txt_guess_x)
        hbox_guess.addWidget(QLabel("Y:"))
        hbox_guess.addWidget(self._txt_guess_y)
        hbox_guess.addStretch(1)
        hbox_guess.addLayout(hbox_btns)
        hbox_guess.addStretch(3)

        self.setLayout(hbox_guess)

    def match(self):
        """ Begin the matching process. """
        self._fn_begin_matching()

    def _set_is_matching(self, is_matching):
        """ Set the current state of the matching, enabling/disabling elements as appropriate. """
        self._btn_begin.setEnabled(not is_matching)
        self._btn_frame.setEnabled(is_matching)
        self._btn_end.setEnabled(is_matching)
        self._btn_begin.setFocus()

    ''' ----------------------
    BUTTON FUNCTIONS
    ------------------------'''
    def _fn_begin_matching(self):
        """ Begin the matching procedure using the two selected images. """
        self._perform_matching()
        self._set_is_matching(True)

    def _fn_next_frame(self):
        """ Advance to the next frame of the matching procedure. """
        if self._matcher is not None:
            self._matcher.next_frame()
            self._display_results()

    def _fn_skip_to_end(self):
        """ Advance to the end of the matching procedure (dont show any frames). """
        if self._matcher is not None:
            self._matcher.skip_to_end()
            self._display_results()

    ''' ----------------------
    MATCHING FUNCTIONS
    ------------------------'''
    def _perform_matching(self):
        """ Begin the matching procedure. """
        img1, img2 = self._prepare_images()

        guess_x = float(self._txt_guess_x.text())
        guess_y = float(self._txt_guess_y.text())
        guess = Translate(guess_x*img1.size[0], guess_y*img1.size[1])

        self._matcher = RegionMatcher(img1, img2, guess)
        self._fn_next_frame()

    def _prepare_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Get the selected images
        self._img1 = self._selector_a.image()
        self._img2 = self._selector_b.image()

        # Resize the mov image so it has the same size per pixel as the ref image
        factor = self._img2.pixel_size / self._img1.pixel_size
        self._img2 = self._img2.rescale(factor)
        self._scale_factor = factor

        return self._img1.to_mono(), self._img2.to_mono()

    def _display_results(self):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        translate = self._matcher.net_transform

        if self._matcher.match_complete:
            status = "Region match"
            self._set_is_matching(False)
        else:
            status = "Region match in progress..."

        aligned = AlignedImages(self._img1, self._img2, translate, status)
        self.signal_aligned.emit(aligned)
