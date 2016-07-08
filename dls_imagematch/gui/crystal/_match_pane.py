from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QLineEdit

from _point_select_dialog import PointSelectDialog
from _slider import Slider


from dls_imagematch.match import CrystalMatcher
from dls_imagematch.match.feature import MatchHomographyCalculator


class CrystalMatchPane(QWidget):
    signal_match_performed = QtCore.pyqtSignal(object)
    signal_new_images = QtCore.pyqtSignal(object, object)
    signal_new_points = QtCore.pyqtSignal(object, object)

    LABEL_WIDTH = 100

    def __init__(self, aligned_images, selected_point, config):
        super(CrystalMatchPane, self).__init__()

        self._config = config

        self._aligned_images = aligned_images

        # UI elements
        self._filter_pane = None
        self._table = None
        self._frame = None
        self._slider_region_size = None

        self._init_ui()

        if selected_point is not None:
            self._set_point_value(selected_point)
            self._fn_perform_match()

    def _init_ui(self):
        pane = self._ui_create_pane()

        vbox_table = QVBoxLayout()
        vbox_table.addWidget(pane)
        vbox_table.addStretch(1)

        self.setLayout(vbox_table)

    def _ui_create_pane(self):
        grp_box = QGroupBox("Crystal Matching")

        lbl_select_point = QLabel("Selected Point")
        lbl_select_point.setFixedWidth(self.LABEL_WIDTH)

        self._txt_point = QLineEdit()
        self._txt_point.setFixedWidth(200)
        self._txt_point.setEnabled(False)

        btn_select_point = QPushButton("Select")
        btn_select_point.clicked.connect(self._fn_select_crystal_point)
        btn_select_point.setFixedWidth(50)

        hbox_select = QHBoxLayout()
        hbox_select.addWidget(lbl_select_point)
        hbox_select.addWidget(self._txt_point)
        hbox_select.addWidget(btn_select_point)
        hbox_select.addStretch(1)

        region_size = self._config.region_size.value()
        self._slider_region_size = Slider("Region Size", region_size, 20, 150)

        search_width = self._config.search_width.value()
        self._slider_search_width = Slider("Search Width", search_width, 100, 500)

        search_height = self._config.search_height.value()
        self._slider_search_height = Slider("Search Height", search_height, 100, 800)

        btn_perform_match = QPushButton("Perform Match")
        btn_perform_match.clicked.connect(self._fn_perform_match)
        btn_perform_match.setFixedWidth(80)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_select)
        vbox.addWidget(self._slider_region_size)
        vbox.addWidget(self._slider_search_width)
        vbox.addWidget(self._slider_search_height)
        vbox.addWidget(btn_perform_match)
        vbox.addStretch()

        grp_box.setLayout(vbox)
        return grp_box

    def _fn_select_crystal_point(self):
        max_points = 1

        region_size = self._slider_region_size.value()
        color = self._config.color_xtal_img1.value()
        dialog = PointSelectDialog(self, self._aligned_images, max_points, region_size, color)
        result_ok = dialog.exec_()

        if result_ok:
            points = dialog.selected_points()
            if len(points) == 1:
                self._set_point_value(points[0])

    def _fn_perform_match(self):
        self._matcher = self._create_crystal_matcher()
        results = self._matcher.match([self._point])
        crystal_match = results.get_match(0)
        feature_match = crystal_match.feature_matches()

        self._emit_new_match_signal(feature_match)

        self._set_transform_points_from_match(crystal_match)

    def _create_crystal_matcher(self):
        region_size = self._slider_region_size.value()
        search_width = self._slider_search_width.value()
        search_height = self._slider_search_height.value()

        matcher = CrystalMatcher(self._aligned_images)
        matcher.set_real_region_size(region_size)
        matcher.set_real_search_size(search_width, search_height)
        return matcher

    def _emit_new_match_signal(self, feature_match):
        self.signal_new_images.emit(feature_match.img1, feature_match.img2)
        self.signal_match_performed.emit(feature_match)

    def _emit_new_points_signal(self, point1, point2):
        self.signal_new_points.emit(point1, point2)

    def _set_transform_points_from_match(self, crystal_match):
        point1 = crystal_match.img1_point() - self._matcher.make_target_region(self._point).top_left()
        point2 = crystal_match.img2_point() - self._matcher.make_search_region(self._point).top_left()
        self._emit_new_points_signal(point1, point2)

    def set_transform_points_from_filtered_matches(self, matches):
        point1 = self._point - self._matcher.make_target_region(self._point).top_left()
        point2 = None

        good_matches = [mat for mat in matches if mat.is_in_transformation()]
        if len(good_matches) > 0:
            homo = MatchHomographyCalculator()
            homo.set_mark_unused(False)
            transform = homo.calculate_transform(good_matches)
            transformed_point = transform.transform_points([self._point])[0]
            point2 = transformed_point - self._matcher.make_search_region(self._point).top_left()

        self._emit_new_points_signal(point1, point2)

    def _set_point_value(self, point):
        self._point = point
        self._txt_point.setText("x={}, y={}".format(int(point.x), int(point.y)))

