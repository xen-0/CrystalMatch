from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import (QPushButton, QHBoxLayout, QComboBox, QGroupBox)

from dls_imagematch.util import File, Image


class WellSelector2(QGroupBox):
    """ Widget that allows the user to select well images to use for matching. The data set for a plate has
    multiple image batches for which each well is imaged. The user can select a plate, a specific well on the
    plate, and two batches for image comparison.

    The path of an image is expected to be: plate_xxx/batch_yy/well_zz_profile_1.jpg
    """
    signal_image1_selected = QtCore.pyqtSignal(object)
    signal_image2_selected = QtCore.pyqtSignal(object)

    def __init__(self, config):
        super(WellSelector2, self).__init__()

        self._samples_dir = config.samples_dir.value()

        self._init_ui()
        self.setTitle("Select Plate")

        self._refresh_batch_lists()
        self._refresh_well_list()

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Get list of plate directories
        plate_folders = File.get_sub_dirs(self._samples_dir, startswith="plate_")

        # Row dropdown box
        self._cmbo_plate = QComboBox()
        self._cmbo_plate.activated[str].connect(self._refresh_batch_lists)
        for folder in plate_folders:
            folder = folder.split("/")[-1]
            self._cmbo_plate.addItem(folder)

        # Column dropdown box
        self._cmbo_batch1 = QComboBox()
        self._cmbo_batch1.activated[str].connect(self._refresh_well_list)
        self._cmbo_batch2 = QComboBox()
        self._cmbo_batch2.activated[str].connect(self._refresh_well_list)
        self._cmbo_well = QComboBox()
        self._cmbo_well.activated[str].connect(self._well_selected)

        # Create layout
        hbox_well_select = QHBoxLayout()
        hbox_well_select.addWidget(self._cmbo_plate)
        hbox_well_select.addWidget(self._cmbo_batch1)
        hbox_well_select.addWidget(self._cmbo_batch2)
        hbox_well_select.addWidget(self._cmbo_well)
        hbox_well_select.addStretch(1)

        self.setLayout(hbox_well_select)

    def _refresh_batch_lists(self):
        """ Called when a plate is selected in the plate dropdown; displays a list of the available batches
        in the batch dropdowns. """
        self._cmbo_batch1.clear()
        self._cmbo_batch2.clear()

        plate_dir = self._samples_dir + self._cmbo_plate.currentText()
        batch_folders = File.get_sub_dirs(str(plate_dir), startswith="batch_")

        for folder in batch_folders:
            folder = folder.split("\\")[-1]
            self._cmbo_batch1.addItem(folder)
            self._cmbo_batch2.addItem(folder)

        self._cmbo_batch1.setCurrentIndex(0)
        self._cmbo_batch2.setCurrentIndex(self._cmbo_batch2.count()-1)

        self._refresh_well_list()

    def _refresh_well_list(self):
        """ Called when a batch is selected in one of the batch dropdowns. Displays a list of the available
        wells in the well dropdown. """
        current_selection = self._cmbo_well.currentText()
        self._cmbo_well.clear()

        plate_dir = self._samples_dir + self._cmbo_plate.currentText()
        batch_dir1 = plate_dir + "/" + self._cmbo_batch1.currentText() + "/"
        batch_dir2 = plate_dir + "/" + self._cmbo_batch2.currentText() + "/"

        # Get the list of well images.
        files1 = File.get_files(str(batch_dir1))
        files1 = [f.split("/")[-1] for f in files1]
        files2 = File.get_files(str(batch_dir2))
        files2 = [f.split("/")[-1] for f in files2]

        # Find the set of images that both batches have in common
        common = list(set(files1).intersection(files2))
        common.sort()

        # Populate the well list
        for f in common:
            well = str(f[:7])
            self._cmbo_well.addItem(well)

        # Set the well selection to the same as previously selected
        index = self._cmbo_well.findText(current_selection)
        if index != -1:
            self._cmbo_well.setCurrentIndex(index)

        self._well_selected()

    def _well_selected(self):
        """ Select a well from the dataset to use for matching. Display the
        corresponding images in slot A and B. """
        plate_dir = self._samples_dir + self._cmbo_plate.currentText()
        batch_dir1 = plate_dir + "/" + self._cmbo_batch1.currentText() + "/"
        batch_dir2 = plate_dir + "/" + self._cmbo_batch2.currentText() + "/"

        filename = self._cmbo_well.currentText() + "_profile_1.jpg"
        file1 = str(batch_dir1 + filename)
        file2 = str(batch_dir2 + filename)

        image1 = Image.from_file(file1, pixel_size=1.0)
        image2 = Image.from_file(file2, pixel_size=1.0)

        self.signal_image1_selected.emit(image1)
        self.signal_image2_selected.emit(image2)

