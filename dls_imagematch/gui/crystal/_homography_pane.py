from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QComboBox

from dls_imagematch.match.feature import HomographyCalculator
from dls_imagematch.util import Point
from ._slider import Slider


class HomographyPane(QWidget):
    signal_new_points = QtCore.pyqtSignal(object, object)
    signal_new_quads = QtCore.pyqtSignal(object, object)
    signal_updated_matches = QtCore.pyqtSignal(object)

    def __init__(self):
        super(HomographyPane, self).__init__()

        self._matcher = None
        self._matches = []
        self._img1_point = None

        # UI elements
        self._cmbo_methods = None

        self._init_ui()

    def _init_ui(self):
        pane = self._ui_create_pane()

        vbox_table = QVBoxLayout()
        vbox_table.addWidget(pane)
        vbox_table.addStretch(1)

        self.setLayout(vbox_table)

    def _ui_create_pane(self):
        label_width = 100

        lbl_method = QLabel("Method")
        lbl_method.setFixedWidth(label_width)
        self._cmbo_methods = QComboBox()
        self._cmbo_methods.setFixedWidth(120)
        self._cmbo_methods.currentIndexChanged.connect(self._refresh_transform)

        names = HomographyCalculator.METHOD_NAMES
        values = HomographyCalculator.METHOD_VALUES
        for name, value in zip(names, values):
            self._cmbo_methods.addItem(name, value)

        self._slider_threshold = Slider("RANSAC Threshold", 5.0, 1.0, 20.0)
        self._slider_threshold.signal_value_changed.connect(self._refresh_transform)

        hbox = QHBoxLayout()
        hbox.addWidget(lbl_method)
        hbox.addWidget(self._cmbo_methods)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self._slider_threshold)
        vbox.addStretch(1)

        box = QGroupBox("Homography")
        box.setLayout(vbox)

        return box

    def set_crystal_match(self, crystal_match, matcher):
        self._matcher = matcher
        self._img1_point = crystal_match.img1_point()
        self._matches = crystal_match.feature_matches().matches
        self._refresh_transform()

    def _refresh_transform(self):
        if self._matcher is None:
            return

        target_region_tl = self._matcher.make_target_region(self._img1_point).top_left()
        search_region_tl = self._matcher.make_search_region(self._img1_point).top_left()

        point1 = self._img1_point - target_region_tl
        point2 = None
        quad1 = []
        quad2 = []

        if len(self._matches) > 0:
            homo = self._create_homography_calc()
            transform = homo.calculate_transform(self._matches)
            transformed_point = transform.transform_points([self._img1_point])[0]
            point2 = transformed_point - search_region_tl

            p1 = self._img1_point

            def trans(x, y):
                return transform.transform_points([p1 + Point(x, y)])[0] - search_region_tl

            w = point1.x
            quad1 = [Point(0, 0), Point(2*w, 0), Point(2*w, 2*w), Point(0, 2*w)]
            quad2 = [trans(-w, -w), trans(w, -w), trans(w, w), trans(-w, w)]

        self._emit_new_points_signal(point1, point2)
        self._emit_new_quads(quad1, quad2)

    def _create_homography_calc(self):
        method_index = self._cmbo_methods.currentIndex()
        method = HomographyCalculator.METHOD_VALUES[method_index]

        threshold = self._slider_threshold.value()

        homo = HomographyCalculator()
        homo.set_homography_method(method)
        homo.set_ransac_threshold(threshold)
        return homo

    def _emit_new_points_signal(self, point1, point2):
        self.signal_new_points.emit(point1, point2)
        self.signal_updated_matches.emit(self._matches)

    def _emit_new_quads(self, quad1, quad2):
        self.signal_new_quads.emit(quad1, quad2)
