from __future__ import division

from PyQt4.QtGui import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QLineEdit

from _feature_detail_pane import FeatureMatchDetailPane
from _point_select_dialog import PointSelectDialog


class SingleCrystalDialog(QDialog):

    def __init__(self, aligned_images, feature_match, config):
        super(SingleCrystalDialog, self).__init__()

        self._config = config

        self._aligned_images = aligned_images
        self._match_result = feature_match

        # UI elements
        self._details_pane = None
        self._txt_region_size = None
        self.hbox_search_w = None
        self.hbox_search_h = None

        self._init_ui(feature_match)

    def _init_ui(self, feature_match):
        self.setWindowTitle('Feature Match Result')

        select_controls = self._ui_controls()
        self._details_pane = FeatureMatchDetailPane(feature_match)

        hbox = QHBoxLayout()
        hbox.addWidget(select_controls)
        hbox.addWidget(self._details_pane)
        hbox.addStretch()

        self.setLayout(hbox)

    def _ui_controls(self):
        LABEL_WIDTH = 100

        grp_box = QGroupBox("Select Crystal")

        btn_select_point = QPushButton("Select Crystal")
        btn_select_point.clicked.connect(self._fn_select_points)

        lbl_region = QLabel("Region Size")
        lbl_region.setFixedWidth(LABEL_WIDTH)
        region_size = self._config.region_size.value()
        self._txt_region_size = QLineEdit(str(region_size))
        hbox_region = QHBoxLayout()
        hbox_region.addWidget(lbl_region)
        hbox_region.addWidget(self._txt_region_size)
        hbox_region.addStretch()

        lbl_width = QLabel("Search Width")
        lbl_width.setFixedWidth(LABEL_WIDTH)
        search_width = self._config.search_width.value()
        self._txt_search_width = QLineEdit(str(search_width))
        hbox_search_w = QHBoxLayout()
        hbox_search_w.addWidget(lbl_width)
        hbox_search_w.addWidget(self._txt_search_width)
        hbox_search_w.addStretch()

        lbl_height = QLabel("Search Height")
        lbl_height.setFixedWidth(LABEL_WIDTH)
        search_height = self._config.search_height.value()
        self._txt_search_height = QLineEdit(str(search_height))
        hbox_search_h = QHBoxLayout()
        hbox_search_h.addWidget(lbl_height)
        hbox_search_h.addWidget(self._txt_search_height)
        hbox_search_h.addStretch()

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_region)
        vbox.addLayout(hbox_search_w)
        vbox.addLayout(hbox_search_h)
        vbox.addWidget(btn_select_point)
        vbox.addStretch()

        grp_box.setLayout(vbox)
        return grp_box

    def _fn_select_points(self):
        max_points = 1

        region_size = self._get_region_size()
        color = self._config.color_xtal_img1.value()
        dialog = PointSelectDialog(self, self._aligned_images, max_points, region_size, color)
        result_ok = dialog.exec_()

        if result_ok:
            points = dialog.selected_points()
            if len(points) == 1:
                self._set_selected_point(points[0])

    def _set_selected_point(self, point):
        self._point = point

    def _get_region_size(self):
        size_txt = self._txt_region_size.text()
        try:
            size = int(size_txt)
        except ValueError:
            size = self._config.region_size.value()

        return size
