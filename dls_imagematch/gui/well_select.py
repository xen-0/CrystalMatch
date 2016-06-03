from __future__ import division

from PyQt4.QtGui import (QPushButton, QHBoxLayout, QComboBox, QGroupBox)


class WellSelector(QGroupBox):
    """ Widget that allows the user to select a particular well from a
    sample test plate.
    """
    SET_FACTOR = 6.55

    def __init__(self, selector_a, selector_b, config):
        super(WellSelector, self).__init__()

        self.selector_a = selector_a
        self.selector_b = selector_b

        self._samples_dir = config.samples_dir.value()

        self._init_ui()
        self.setTitle("Select Well (441350000072)")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Row dropdown box
        self._cmbo_row = QComboBox()
        for c in range(ord('A'), ord('H')+1):
            self._cmbo_row.addItem(chr(c))

        # Column dropdown box
        self._cmbo_col = QComboBox()
        for col in range(1,13):
            self._cmbo_col.addItem(str(col))

        # Select button
        btn_select = QPushButton("Select")
        btn_select.clicked.connect(self._select_well)

        # Create layout
        hbox_well_select = QHBoxLayout()
        hbox_well_select.addWidget(self._cmbo_row)
        hbox_well_select.addWidget(self._cmbo_col)
        hbox_well_select.addWidget(btn_select)
        hbox_well_select.addStretch(1)

        self.setLayout(hbox_well_select)

    def _select_well(self):
        """ Select a well from the 441350000072 dataset to use for matching. Display the
        corresponding images in slot A and B. """
        row = self._cmbo_row.currentText()
        col = self._cmbo_col.currentText()

        file_a, file_b = self._get_441350000072_files(row, col, self._samples_dir)
        self.selector_a.setFile(file_a)
        self.selector_b.setFile(file_b)

        # Set pixel sizes
        pixel_size_a = 1.0
        pixel_size_b = pixel_size_a / WellSelector.SET_FACTOR
        self.selector_a.setPixelSize(pixel_size_a)
        self.selector_b.setPixelSize(pixel_size_b)

    @staticmethod
    def _get_441350000072_files(row, col, dir):
        """ Get the full paths of the files for the specified well of the 441350000072 data set. """
        mov_filepath = dir + "441350000072_OAVS/_1_" + str(row) + str(col) + ".png"
        col = int(col)
        if col < 10:
            col = '0' + str(col)

        ref_filepath = dir + "441350000072/" + str(row) + str(col) + "_13.jpg"

        return ref_filepath, mov_filepath
