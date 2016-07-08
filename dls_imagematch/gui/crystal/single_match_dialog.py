from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QLineEdit, QCheckBox, QSlider

from _match_pane import CrystalMatchPane
from _filter_pane import FeatureMatchDetailPane
from _matches_table import FeatureMatchTable
from _crystal_match_frame import CrystalMatchFrame


class SingleCrystalDialog(QDialog):
    LABEL_WIDTH = 100

    def __init__(self, aligned_images, selected_point, config):
        super(SingleCrystalDialog, self).__init__()

        self._config = config

        self._aligned_images = aligned_images

        # UI elements
        self._match_pane = None
        self._filter_pane = None
        self._table = None
        self._frame = None
        self._slider_region_size = None

        self._init_ui(selected_point)

    def _init_ui(self, selected_point):
        self.setWindowTitle('Single Crystal Matching')

        self._match_pane = CrystalMatchPane(self._aligned_images, selected_point, self._config)

        self._filter_pane = FeatureMatchDetailPane()
        self._filter_pane.setEnabled(False)

        self._table = FeatureMatchTable()
        self._table.setEnabled(False)

        self._frame = CrystalMatchFrame()

        self._match_pane.signal_match_performed.connect(self._filter_pane.set_feature_match)
        self._match_pane.signal_new_images.connect(self._frame.set_new_images)
        self._match_pane.signal_new_points.connect(self._frame.display_points)

        self._filter_pane.signal_matches_filtered.connect(self._frame.display_matches)
        self._filter_pane.signal_matches_filtered.connect(self._table.display_matches)
        self._filter_pane.signal_matches_filtered.connect(self._match_pane.set_transform_points_from_filtered_matches)

        self._table.signal_matches_selected.connect(self._frame.display_highlights)

        vbox = QVBoxLayout()
        vbox.addWidget(self._match_pane)
        vbox.addStretch(1)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self._filter_pane)
        vbox2.addWidget(self._table)
        vbox2.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addLayout(vbox2)
        hbox.addWidget(self._frame)
        hbox.addStretch()

        self.setLayout(hbox)
