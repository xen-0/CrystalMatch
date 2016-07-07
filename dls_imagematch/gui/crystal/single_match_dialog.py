from __future__ import division

from PyQt4.QtGui import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QLineEdit, QCheckBox

from _feature_detail_pane import FeatureMatchDetailPane
from _feature_detail_frame import FeatureMatchDetailFrame
from _point_select_dialog import PointSelectDialog

from dls_imagematch.match import CrystalMatcher


class SingleCrystalDialog(QDialog):
    LABEL_WIDTH = 100

    def __init__(self, aligned_images, feature_match, config):
        super(SingleCrystalDialog, self).__init__()

        self._config = config

        self._aligned_images = aligned_images

        # UI elements
        self._details_pane = None
        self._frame = None
        self._txt_region_size = None
        self.hbox_search_w = None
        self.hbox_search_h = None

        self._init_ui()
        self._set_feature_match_result(feature_match)

    def _init_ui(self):
        self.setWindowTitle('Single Crystal Matching')

        select_controls = self._ui_create_search()
        match_controls = self._ui_create_match()
        self._details_pane = FeatureMatchDetailPane()
        self._frame = FeatureMatchDetailFrame()

        self._details_pane.signal_matches_filtered.connect(self._frame.display_matches)
        self._details_pane.signal_matches_selected.connect(self._frame.display_highlights)

        vbox = QVBoxLayout()
        vbox.addWidget(select_controls)
        vbox.addWidget(match_controls)
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(self._details_pane)
        hbox.addWidget(self._frame)
        hbox.addStretch()

        self.setLayout(hbox)

    def _ui_create_search(self):
        grp_box = QGroupBox("Select Crystal")

        btn_select_point = QPushButton("Select Crystal")
        btn_select_point.clicked.connect(self._fn_select_crystal_point)
        btn_select_point.setFixedWidth(80)

        region_size = str(self._config.region_size.value())
        self._txt_region_size, hbox_region = self._ui_txt_box("Region Size", region_size)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_region)
        vbox.addWidget(btn_select_point)
        vbox.addStretch()

        grp_box.setLayout(vbox)
        return grp_box

    def _ui_create_match(self):
        grp_box = QGroupBox("Perform Crystal Match")

        search_width = str(self._config.search_width.value())
        self._txt_search_width, hbox_search_w = self._ui_txt_box("Search Width", search_width)

        search_height = str(self._config.search_height.value())
        self._txt_search_height, hbox_search_h = self._ui_txt_box("Search Height", search_height)

        trans_only = str(self._config.match_translation_only.value())
        self._chk_translation, hbox_trans = self._ui_check_box("Translation Only", trans_only)

        btn_perform_match = QPushButton("Perform Match")
        btn_perform_match.clicked.connect(self._fn_select_crystal_point)
        btn_perform_match.setFixedWidth(80)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_search_w)
        vbox.addLayout(hbox_search_h)
        vbox.addLayout(hbox_trans)
        vbox.addWidget(btn_perform_match)
        vbox.addStretch()

        grp_box.setLayout(vbox)
        return grp_box

    def _ui_txt_box(self, label, initial_value):
        lbl = QLabel(label)
        lbl.setFixedWidth(self.LABEL_WIDTH)
        txt = QLineEdit(initial_value)

        hbox = QHBoxLayout()
        hbox.addWidget(lbl)
        hbox.addWidget(txt)
        hbox.addStretch()

        return txt, hbox

    def _ui_check_box(self, label, initial_value):
        lbl = QLabel(label)
        lbl.setFixedWidth(self.LABEL_WIDTH)

        if initial_value == True:
            state = 2
        else:
            state = 0

        chkbox = QCheckBox()
        chkbox.setCheckState(state)
        chkbox.setTristate(False)

        hbox = QHBoxLayout()
        hbox.addWidget(lbl)
        hbox.addWidget(chkbox)
        hbox.addStretch()

        return chkbox, hbox

    def _fn_select_crystal_point(self):
        max_points = 1

        region_size = self._region_size()
        color = self._config.color_xtal_img1.value()
        dialog = PointSelectDialog(self, self._aligned_images, max_points, region_size, color)
        result_ok = dialog.exec_()

        if result_ok:
            points = dialog.selected_points()
            if len(points) == 1:
                self._set_crystal_point(points[0])

    def _set_crystal_point(self, point):
        self._point = point

        matcher = self._create_crystal_matcher()
        results = matcher.match([point])
        feature_match = results.get_match(0).feature_matches()
        self._set_feature_match_result(feature_match)

    def _create_crystal_matcher(self):
        region_size = self._region_size()
        search_width = self._search_width()
        search_height = self._search_height()
        translation_only = self._translation_only()

        matcher = CrystalMatcher(self._aligned_images)
        matcher.set_real_region_size(region_size)
        matcher.set_real_search_size(search_width, search_height)
        matcher.set_translation_only(translation_only)
        return matcher

    def _set_feature_match_result(self, feature_match):
        self._frame.set_new_images(feature_match.img1, feature_match.img2)
        self._details_pane.set_feature_match(feature_match)

    # -----
    def _region_size(self):
        text = self._txt_region_size.text()
        try:
            return int(text)
        except ValueError:
            return self._config.region_size.value()

    def _search_width(self):
        text = self._txt_search_width.text()
        try:
            return int(text)
        except ValueError:
            return self._config.search_width.value()

    def _search_height(self):
        text = self._txt_search_height.text()
        try:
            return int(text)
        except ValueError:
            return self._config.search_height.value()

    def _translation_only(self):
        return self._chk_translation.checkState() > 0
