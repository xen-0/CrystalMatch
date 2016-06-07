from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QLineEdit, QLabel, QComboBox

from dls_imagematch.match import RegionConsensusMatcher, AlignedImages
from dls_imagematch.util import Point


class ConsensusMatchControl(QGroupBox):
    """ Widget that allows control of the Consensus Matching process.
    """
    DEFAULT_X = "0"
    DEFAULT_Y = "0"
    DEFAULT_GRID_SPACE = "0.05"

    GRID_SIZE_NAMES = ["3x3", "5x5", "7x7", "9x9"]
    GRID_SIZE_VALUES = [1, 2, 3, 4]

    signal_aligned = QtCore.pyqtSignal(object)

    def __init__(self, selector_a, selector_b):
        super(ConsensusMatchControl, self).__init__()

        self._selector_a = selector_a
        self._selector_b = selector_b
        self._matcher = None

        self._init_ui()
        self.setTitle("Consensus Region Matching")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Initial position guess
        self._txt_guess_x = QLineEdit(self.DEFAULT_X)
        self._txt_guess_x.setFixedWidth(40)
        self._txt_guess_y = QLineEdit(self.DEFAULT_Y)
        self._txt_guess_y.setFixedWidth(40)
        self._txt_grid_space = QLineEdit(self.DEFAULT_GRID_SPACE)
        self._txt_grid_space.setFixedWidth(40)

        self._cmbo_grid_size = QComboBox()
        self._cmbo_grid_size.addItems(self.GRID_SIZE_NAMES)

        # Matching function buttons
        self._btn_perform = QPushButton("Perform Match")
        self._btn_perform.clicked.connect(self._fn_begin_matching)

        # Create widget layout
        hbox_guess = QHBoxLayout()
        hbox_guess.addWidget(QLabel("X:"))
        hbox_guess.addWidget(self._txt_guess_x)
        hbox_guess.addWidget(QLabel("Y:"))
        hbox_guess.addWidget(self._txt_guess_y)
        hbox_guess.addWidget(QLabel("Grid:"))
        hbox_guess.addWidget(self._cmbo_grid_size)
        hbox_guess.addWidget(self._txt_grid_space)
        hbox_guess.addStretch(1)
        hbox_guess.addWidget(self._btn_perform)
        hbox_guess.addStretch(3)

        self.setLayout(hbox_guess)

    def match(self):
        self._fn_begin_matching()

    def _fn_begin_matching(self):
        """ Being the consensus matching process for the two selected images. """
        img1, img2 = self._prepare_images()

        # Prepare initial guess
        guess_x = float(self._txt_guess_x.text())
        guess_y = float(self._txt_guess_y.text())
        guess = Point(guess_x*img1.size[0], guess_y*img1.size[1])

        # Set grid spacing
        index = self._cmbo_grid_size.currentIndex()
        grid_size = self.GRID_SIZE_VALUES[index]
        grid = float(self._txt_grid_space.text())
        spacing = grid * img1.size[0]

        # Perform matching
        self._matcher = RegionConsensusMatcher(img1, img2)
        self._matcher.match(guess, grid_size, spacing)

        self._display_results()

    def _prepare_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Get the selected images
        self._img1 = self._selector_a.image()
        self._img2 = self._selector_b.image()

        # Resize the image B so it has the same size per pixel as image A
        factor = self._img2.pixel_size / self._img1.pixel_size
        self._img2 = self._img2.rescale(factor)

        return self._img1.to_mono(), self._img2.to_mono()

    def _display_results(self):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        translate = self._matcher.match_transform
        confidence = self._matcher.match_confidence

        method = "Consensus region match [agreement = {0:.2f}]".format(confidence)
        aligned = AlignedImages(self._img1, self._img2, translate, method)
        self.signal_aligned.emit(aligned)
