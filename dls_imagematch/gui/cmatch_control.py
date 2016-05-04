from __future__ import division

from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QLineEdit, QLabel, QComboBox

from dls_imagematch.match import RegionConsensusMatcher, Overlayer
from dls_imagematch.util import Translate


class ConsensusMatchControl(QGroupBox):
    """ Widget that allows control of the Consensus Matching process.
    """

    DEFAULT_X = "0.1"
    DEFAULT_Y = "0.4"
    DEFAULT_GRID_SPACE = "0.05"

    GRID_SIZE_NAMES = ["3x3", "5x5", "7x7", "9x9"]
    GRID_SIZE_VALUES = [1, 2, 3, 4]

    def __init__(self, selector_a, selector_b, image_frame):
        super(ConsensusMatchControl, self).__init__()

        self.selector_a = selector_a
        self.selector_b = selector_b
        self.image_frame = image_frame

        self._init_ui()

        self.matcher = None

        self.setTitle("Consensus Matching")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Initial position guess
        self.txt_guess_x = QLineEdit(self.DEFAULT_X)
        self.txt_guess_x.setFixedWidth(40)
        self.txt_guess_y = QLineEdit(self.DEFAULT_Y)
        self.txt_guess_y.setFixedWidth(40)
        self.txt_grid_space = QLineEdit(self.DEFAULT_GRID_SPACE)
        self.txt_grid_space.setFixedWidth(40)

        self._cmbo_grid_size = QComboBox()
        self._cmbo_grid_size.addItems(self.GRID_SIZE_NAMES)

        # Matching function buttons
        self.btn_perform = QPushButton("Perform Match")
        self.btn_perform.clicked.connect(self._fn_begin_matching)

        # Create widget layout
        hbox_guess = QHBoxLayout()
        hbox_guess.addWidget(QLabel("X:"))
        hbox_guess.addWidget(self.txt_guess_x)
        hbox_guess.addWidget(QLabel("Y:"))
        hbox_guess.addWidget(self.txt_guess_y)
        hbox_guess.addWidget(QLabel("Grid:"))
        hbox_guess.addWidget(self._cmbo_grid_size)
        hbox_guess.addWidget(self.txt_grid_space)
        hbox_guess.addStretch(1)
        hbox_guess.addWidget(self.btn_perform)
        hbox_guess.addStretch(3)

        self.setLayout(hbox_guess)

    def match(self):
        self._fn_begin_matching()

    def _fn_begin_matching(self):
        """ Being the consensus matching process for the two selected images. """
        img_a, img_b = self._prepare_images()

        # Prepare initial guess
        guess_x = float(self.txt_guess_x.text())
        guess_y = float(self.txt_guess_y.text())
        guess = Translate(guess_x*img_a.size[0], guess_y*img_a.size[1])

        # Set grid spacing
        index = self._cmbo_grid_size.currentIndex()
        grid_size = self.GRID_SIZE_VALUES[index]
        grid = float(self.txt_grid_space.text())
        spacing = grid * img_a.size[0]

        # Perform matching
        self.matcher = RegionConsensusMatcher(img_a, img_b)
        self.matcher.match(guess, grid_size, spacing)

        self._display_results()

    def _prepare_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Get the selected images
        self.img_a = self.selector_a.image()
        self.img_b = self.selector_b.image()

        # Resize the image B so it has the same size per pixel as image A
        factor = self.img_b.pixel_size / self.img_a.pixel_size
        self.img_b = self.img_b.rescale(factor)

        return self.img_a.make_gray(), self.img_b.make_gray()

    def _display_results(self):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        transform = self.matcher.match_transform

        # Create image of B overlaid on A
        img = Overlayer.create_overlay_image(self.img_a, self.img_b, transform)
        self.image_frame.display_image(img)

        # Determine current transformation in real units (um)
        x, y = int(transform.x), int(transform.y)
        pixel_size = self.img_a.pixel_size
        x_um, y_um = int(x * pixel_size), int(y * pixel_size)
        offset_msg = "x={} um, y={} um ({} px, {} px)".format(x_um, y_um, x, y)

        status = "Consensus match complete"
        self.image_frame.set_status_message(status, offset_msg)
