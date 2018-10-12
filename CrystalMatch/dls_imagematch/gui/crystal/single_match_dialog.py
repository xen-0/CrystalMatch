from __future__ import division

from PyQt4.QtGui import QDialog, QHBoxLayout, QVBoxLayout

from ._match_pane import CrystalMatchPane
from ._filter_pane import FilterPane
from ._metric_pane import MetricPane
from ._matches_table import FeatureMatchTable
from ._crystal_match_frame import CrystalMatchFrame
from ._transform_pane import TransformPane


class SingleCrystalDialog(QDialog):
    LABEL_WIDTH = 100

    def __init__(self, aligned_images, selected_point, gui_config, crystal_config):
        super(SingleCrystalDialog, self).__init__()

        self._gui_config = gui_config
        self._crystal_config = crystal_config

        self._aligned_images = aligned_images

        # UI elements
        self._match_pane = None
        self._transform_pane = None
        self._filter_pane = None
        self._metric_pane = None
        self._table = None
        self._frame = None

        self._init_ui()
        self._connect_components()

        self._match_pane.set_starting_point(selected_point)

    def _init_ui(self):
        self.setWindowTitle('Single Crystal Matching')

        self._match_pane = CrystalMatchPane(self._aligned_images, self._gui_config, self._crystal_config)

        self._transform_pane = TransformPane()

        self._filter_pane = FilterPane()
        self._filter_pane.setEnabled(False)

        self._metric_pane = MetricPane()

        self._table = FeatureMatchTable()
        self._table.setEnabled(False)

        self._frame = CrystalMatchFrame()

        vbox = QVBoxLayout()
        vbox.addWidget(self._match_pane)
        vbox.addWidget(self._transform_pane)
        vbox.addWidget(self._filter_pane)
        vbox.addWidget(self._metric_pane)
        vbox.addStretch(1)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self._table)
        vbox2.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addLayout(vbox2)
        hbox.addWidget(self._frame)
        hbox.addStretch()

        self.setLayout(hbox)

    def _connect_components(self):
        self._match_pane.signal_new_crystal_match.connect(self._transform_pane.set_crystal_match)
        self._match_pane.signal_new_crystal_match.connect(self._metric_pane.set_crystal_match_result)
        self._match_pane.signal_new_images.connect(self._frame.set_new_images)

        self._transform_pane.signal_new_transform.connect(self._metric_pane.set_transform)
        self._transform_pane.signal_updated_matches.connect(self._filter_pane.set_matches)
        self._transform_pane.signal_new_points.connect(self._frame.display_points)
        self._transform_pane.signal_new_quads.connect(self._frame.display_transformed_square)

        self._filter_pane.signal_matches_filtered.connect(self._frame.display_matches)
        self._filter_pane.signal_matches_filtered.connect(self._table.display_matches)

        self._table.signal_matches_selected.connect(self._frame.display_highlights)
