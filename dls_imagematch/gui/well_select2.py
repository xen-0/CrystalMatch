from __future__ import division

from PyQt4.QtGui import (QPushButton, QHBoxLayout, QComboBox, QGroupBox)

from dls_imagematch.gui import SAMPLES_DIR
from dls_imagematch.util import File


class WellSelector2(QGroupBox):
    """ Widget that allows the user to select a particular well from a
    sample test plate.
    """
    def __init__(self, selector_a, selector_b):
        super(WellSelector2, self).__init__()

        self.selector_a = selector_a
        self.selector_b = selector_b

        self._init_ui()
        self.setTitle("Select Plate")

        self._plate_selected()
        self._batch_selected()

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Get list of plate directories
        plate_dirs = File.get_sub_dirs(SAMPLES_DIR, startswith="plate_")

        # Row dropdown box
        self._cmbo_plate = QComboBox()
        self._cmbo_plate.activated[str].connect(self._plate_selected)
        for dir in plate_dirs:
            dir = dir.split("/")[-1]
            self._cmbo_plate.addItem(dir)

        # Column dropdown box
        self._cmbo_batch1 = QComboBox()
        self._cmbo_batch1.activated[str].connect(self._batch_selected)
        self._cmbo_batch2 = QComboBox()
        self._cmbo_batch2.activated[str].connect(self._batch_selected)
        self._cmbo_well = QComboBox()

        # Select button
        btn_select = QPushButton("Select")
        btn_select.clicked.connect(self._select_well)

        # Create layout
        hbox_well_select = QHBoxLayout()
        hbox_well_select.addWidget(self._cmbo_plate)
        hbox_well_select.addWidget(self._cmbo_batch1)
        hbox_well_select.addWidget(self._cmbo_batch2)
        hbox_well_select.addWidget(self._cmbo_well)
        hbox_well_select.addWidget(btn_select)
        hbox_well_select.addStretch(1)

        self.setLayout(hbox_well_select)

    def _plate_selected(self):
        self._cmbo_batch1.clear()
        self._cmbo_batch2.clear()

        plate_dir = SAMPLES_DIR + self._cmbo_plate.currentText()
        batch_dirs = File.get_sub_dirs(str(plate_dir), startswith="batch_")

        for dir in batch_dirs:
            dir = dir.split("\\")[-1]
            self._cmbo_batch1.addItem(dir)
            self._cmbo_batch2.addItem(dir)

        self._cmbo_batch1.setCurrentIndex(0)
        self._cmbo_batch2.setCurrentIndex(self._cmbo_batch2.count()-1)

    def _batch_selected(self):
        self._cmbo_well.clear()

        plate_dir = SAMPLES_DIR + self._cmbo_plate.currentText()
        batch_dir1 = plate_dir + "/" + self._cmbo_batch1.currentText() + "/"

        files = File.get_files(str(batch_dir1))
        for f in files:
            f = f.split("/")[-1]
            num = f[:7]

            self._cmbo_well.addItem(num)

    def _select_well(self):
        """ Select a well from the dataset to use for matching. Display the
        corresponding images in slot A and B. """
        plate_dir = SAMPLES_DIR + self._cmbo_plate.currentText()
        batch_dir1 = plate_dir + "/" + self._cmbo_batch1.currentText() + "/"
        batch_dir2 = plate_dir + "/" + self._cmbo_batch2.currentText() + "/"

        filename = self._cmbo_well.currentText() + "_profile_1.jpg"
        file_a = str(batch_dir1 + filename)
        file_b = str(batch_dir2 + filename)

        self.selector_a.setFile(file_a)
        self.selector_b.setFile(file_b)

        # Set pixel sizes
        self.selector_a.setPixelSize(1.0)
        self.selector_b.setPixelSize(1.0)
