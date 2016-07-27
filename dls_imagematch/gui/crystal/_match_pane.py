from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QLineEdit

from ._point_select_dialog import PointSelectDialog
from ._slider import Slider
from dls_imagematch.util import Point
from dls_imagematch.match import CrystalMatcher


class CrystalMatchPane(QWidget):
    signal_new_crystal_match = QtCore.pyqtSignal(object, object)
    signal_new_images = QtCore.pyqtSignal(object, object)

    LABEL_WIDTH = 100

    def __init__(self, aligned_images, config):
        super(CrystalMatchPane, self).__init__()

        self._config = config

        self._aligned_images = aligned_images

        # UI elements
        self._filter_pane = None
        self._table = None
        self._frame = None
        self._slider_region_size = None

        self._init_ui()
        self._set_point_value(aligned_images.img1.bounds().center())

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

        self._txt_point_x = QLineEdit("0")
        self._txt_point_x.setFixedWidth(66)
        self._txt_point_x.textChanged.connect(self._point_x_text_changed)
        self._txt_point_y = QLineEdit("0")
        self._txt_point_y.setFixedWidth(67)
        self._txt_point_y.textChanged.connect(self._point_y_text_changed)

        btn_select_point = QPushButton("Select")
        btn_select_point.clicked.connect(self._fn_select_crystal_point)
        btn_select_point.setFixedWidth(52)

        hbox_select = QHBoxLayout()
        hbox_select.addWidget(lbl_select_point)
        hbox_select.addWidget(QLabel("X="))
        hbox_select.addWidget(self._txt_point_x)
        hbox_select.addWidget(QLabel("Y="))
        hbox_select.addWidget(self._txt_point_y)
        hbox_select.addWidget(btn_select_point)
        hbox_select.addStretch(1)

        region_size = self._config.region_size.value()
        self._slider_region_size = Slider("Region Size", region_size, 20, 150)

        search_width = self._config.search_width.value()
        self._slider_search_width = Slider("Search Width", search_width, 100, 500)

        search_height = self._config.search_height.value()
        self._slider_search_height = Slider("Search Height", search_height, 100, 800)

        self._btn_perform_match = QPushButton("Refresh")
        self._btn_perform_match.clicked.connect(self._fn_perform_match)
        self._btn_perform_match.setFixedWidth(80)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_select)
        vbox.addWidget(self._slider_region_size)
        vbox.addWidget(self._slider_search_width)
        vbox.addWidget(self._slider_search_height)
        vbox.addWidget(self._btn_perform_match)
        vbox.addStretch()

        grp_box.setLayout(vbox)
        return grp_box

    def set_starting_point(self, point):
        if point is not None:
            self._set_point_value(point)
            self._fn_perform_match()

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
                self._fn_perform_match()

    def _fn_perform_match(self):
        matcher = self._create_crystal_matcher()
        print(self._point)
        results = matcher.match([self._point])
        crystal_match = results.get_match(0)
        self._emit_new_match_signal(crystal_match, matcher)

    def _create_crystal_matcher(self):
        region_size = self._slider_region_size.value()
        search_width = self._slider_search_width.value()
        search_height = self._slider_search_height.value()

        matcher = CrystalMatcher(self._aligned_images)
        matcher.set_real_region_size(region_size)
        matcher.set_real_search_size(search_width, search_height)
        return matcher

    def _emit_new_match_signal(self, crystal_match, matcher):
        feature_match = crystal_match.feature_matches()

        self.signal_new_images.emit(feature_match.img1, feature_match.img2)
        self.signal_new_crystal_match.emit(crystal_match, matcher)

    def _set_point_value(self, point):
        self._point = point.intify()

        if self._txt_point_x.text() != str(self._point.x):
            self._txt_point_x.setText(str(self._point.x))

        if self._txt_point_y.text() != str(self._point.y):
            self._txt_point_y.setText(str(self._point.y))

    def _point_x_text_changed(self):
        x = self._txt_point_x.text()
        try:
            x = int(x)
            if x != self._point.x:
                self._set_point_value(Point(x, self._point.y))
        except ValueError:
            pass

    def _point_y_text_changed(self):
        y = self._txt_point_y.text()
        try:
            y = int(y)
            if y != self._point.y:
                self._set_point_value(Point(self._point.x, y))
        except ValueError:
            pass
