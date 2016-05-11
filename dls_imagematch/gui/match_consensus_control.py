from __future__ import division

from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QLineEdit, QLabel, QComboBox

from dls_imagematch.match import RegionConsensusMatcher, Overlayer, OverlapMetric
from dls_imagematch.util import Translate


class ConsensusMatchControl(QGroupBox):
    """ Widget that allows control of the Consensus Matching process.
    """

    DEFAULT_X = "0"
    DEFAULT_Y = "0"
    DEFAULT_GRID_SPACE = "0.05"

    GRID_SIZE_NAMES = ["3x3", "5x5", "7x7", "9x9"]
    GRID_SIZE_VALUES = [1, 2, 3, 4]

    def __init__(self, selector_a, selector_b, image_frame):
        super(ConsensusMatchControl, self).__init__()

        self._selector_a = selector_a
        self._selector_b = selector_b
        self._image_frame = image_frame
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
        img_a, img_b = self._prepare_images()

        # Prepare initial guess
        guess_x = float(self._txt_guess_x.text())
        guess_y = float(self._txt_guess_y.text())
        guess = Translate(guess_x*img_a.size[0], guess_y*img_a.size[1])

        # Set grid spacing
        index = self._cmbo_grid_size.currentIndex()
        grid_size = self.GRID_SIZE_VALUES[index]
        grid = float(self._txt_grid_space.text())
        spacing = grid * img_a.size[0]

        # Clear existing image from frame
        self._image_frame.clear()
        self._image_frame.set_status_message("Performing consensus match...")

        # Perform matching
        self._matcher = RegionConsensusMatcher(img_a, img_b)
        self._matcher.match(guess, grid_size, spacing)

        self._display_results()

    def _prepare_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Get the selected images
        self._img_a = self._selector_a.image()
        self._img_b = self._selector_b.image()

        # Resize the image B so it has the same size per pixel as image A
        factor = self._img_b.pixel_size / self._img_a.pixel_size
        self._img_b = self._img_b.rescale(factor)

        return self._img_a.make_gray(), self._img_b.make_gray()

    def _display_results(self):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        transform = self._matcher.match_transform
        confidence = self._matcher.match_confidence

        status = "Consensus region match complete (agreement = {0:.2f})".format(confidence)
        self._image_frame.display_match_results(self._img_a, self._img_b, transform, status)
