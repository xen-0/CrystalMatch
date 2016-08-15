from __future__ import division

import os

from PyQt4 import QtCore
from PyQt4.QtGui import QHBoxLayout, QComboBox, QGroupBox

from dls_imagematch.util import Image


class WellSelectorFormulatrix(QGroupBox):
    """ Widget that allows the user to select well images to use for matching. The data set for a plate has
    multiple image batches for which each well is imaged. The user can select a plate, a specific well on the
    plate, and two batches for image comparison.

    The path of an image is expected to be: plate_xxx/batch_yy/well_zz_profile_1.jpg
    """
    signal_image1_selected = QtCore.pyqtSignal(object)
    signal_image2_selected = QtCore.pyqtSignal(object)

    def __init__(self, config):
        super(WellSelectorFormulatrix, self).__init__()

        self._init_ui()
        self.setTitle("Select Plate")

        self._samples_dir = None

        self._set_samples_directory("../test-images/Formulatrix/")
        self._refresh_batch_lists()
        self._refresh_well_list()

    def _init_ui(self):
        """ Create all the display elements of the widget. """

        # Row dropdown box
        self._cmbo_plate = QComboBox()
        self._cmbo_plate.activated[str].connect(self._refresh_batch_lists)

        # Column dropdown box
        self._cmbo_batch1 = QComboBox()
        self._cmbo_batch1.activated[str].connect(self._refresh_well_list)
        self._cmbo_batch2 = QComboBox()
        self._cmbo_batch2.activated[str].connect(self._refresh_well_list)
        self._cmbo_well = QComboBox()
        self._cmbo_well.activated[str].connect(self._emit_well_selected_signal)

        # Create layout
        hbox_well_select = QHBoxLayout()
        hbox_well_select.addWidget(self._cmbo_plate)
        hbox_well_select.addWidget(self._cmbo_batch1)
        hbox_well_select.addWidget(self._cmbo_batch2)
        hbox_well_select.addWidget(self._cmbo_well)
        hbox_well_select.addStretch(1)

        self.setLayout(hbox_well_select)

    def _set_samples_directory(self, directory):
        self._samples_dir = directory

        if not self.is_sample_dir_valid():
            return

        # Get list of plate directories
        plate_folders = self.get_sub_dirs(directory)

        for folder in plate_folders:
            folder = folder.split("/")[-1]
            self._cmbo_plate.addItem(folder)

    def is_sample_dir_valid(self):
        return self._samples_dir is not None and os.path.exists(self._samples_dir)

    def _refresh_batch_lists(self):
        """ Called when a plate is selected in the plate dropdown; displays a list of the available batches
        in the batch dropdowns. """
        if not self.is_sample_dir_valid():
            return

        self._cmbo_batch1.clear()
        self._cmbo_batch2.clear()

        plate_dir = self._samples_dir + self._cmbo_plate.currentText()
        batch_folders = self.get_sub_dirs(str(plate_dir))

        self._populate_batch_lists(batch_folders)
        self._cmbo_batch1.setCurrentIndex(0)
        self._cmbo_batch2.setCurrentIndex(self._cmbo_batch2.count()-1)

        self._refresh_well_list()

    def _populate_batch_lists(self, folders):
        for folder in folders:
            folder = folder.split("\\")[-1]
            self._cmbo_batch1.addItem(folder)
            self._cmbo_batch2.addItem(folder)

    def _refresh_well_list(self):
        """ Called when a batch is selected in one of the batch dropdowns. Displays a list of the available
        wells in the well dropdown. """
        if not self.is_sample_dir_valid():
            return

        current_selection = self._cmbo_well.currentText()
        self._cmbo_well.clear()

        files = self._get_well_files_list()
        self._populate_well_list(files)
        self._set_selected_well(current_selection)
        self._emit_well_selected_signal()

    def _populate_well_list(self, files):
        for f in files:
            well = str(f[:7])
            self._cmbo_well.addItem(well)

    def _set_selected_well(self, text):
        index = self._cmbo_well.findText(text)
        if index != -1:
            self._cmbo_well.setCurrentIndex(index)

    def _get_well_files_list(self):
        plate_dir = self._samples_dir + self._cmbo_plate.currentText()
        batch_dir1 = plate_dir + "/" + self._cmbo_batch1.currentText() + "/"
        batch_dir2 = plate_dir + "/" + self._cmbo_batch2.currentText() + "/"

        files1 = self.get_files(str(batch_dir1))
        files1 = [f.split("/")[-1][:-4] for f in files1]
        files2 = self.get_files(str(batch_dir2))
        files2 = [f.split("/")[-1][:-4] for f in files2]

        print(batch_dir1, files1)
        print(batch_dir2, files2)

        # Find the set of images that both batches have in common
        common = list(set(files1).intersection(files2))
        common.sort()
        return common

    def _emit_well_selected_signal(self):
        """ Select a well from the dataset to use for matching. Display the
        corresponding images in slot A and B. """
        plate_dir = self._samples_dir + self._cmbo_plate.currentText()
        batch_dir1 = plate_dir + "/" + self._cmbo_batch1.currentText() + "/"
        batch_dir2 = plate_dir + "/" + self._cmbo_batch2.currentText() + "/"

        filename = self._cmbo_well.currentText() + ".jpg"
        file1 = str(batch_dir1 + filename)
        file2 = str(batch_dir2 + filename)

        image1 = Image.from_file(file1, pixel_size=1.0)
        image2 = Image.from_file(file2, pixel_size=1.0)

        self.signal_image1_selected.emit(image1)
        self.signal_image2_selected.emit(image2)

    @staticmethod
    def get_sub_dirs(dir, startswith="", endswith=""):
        """ Return the full path of all immediate subdirectories in the
        specified directory. """
        dirs = os.listdir(dir)

        if startswith != "":
            dirs = [d for d in dirs if d.startswith(startswith)]

        if endswith != "":
            dirs = [d for d in dirs if d.endswith(endswith)]

        paths = [os.path.join(dir, d) for d in dirs]
        sub_dirs = [p for p in paths if os.path.isdir(p)]
        return sub_dirs

    @staticmethod
    def get_files(dir):
        """ Return a list of all files (full path) in the directory. """
        paths = [os.path.join(dir,o) for o in os.listdir(dir)]
        files = [p for p in paths if os.path.isfile(p)]

        return files
