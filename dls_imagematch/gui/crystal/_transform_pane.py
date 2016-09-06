from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QComboBox

from dls_imagematch.util.shape import Point, Polygon
from dls_imagematch.util.widget import Slider
from feature import TransformCalculator


class TransformPane(QWidget):
    signal_new_transform = QtCore.pyqtSignal(object)
    signal_new_points = QtCore.pyqtSignal(object, object)
    signal_new_quads = QtCore.pyqtSignal(object, object)
    signal_updated_matches = QtCore.pyqtSignal(object)

    def __init__(self):
        super(TransformPane, self).__init__()

        self._matcher = None
        self._matches = []
        self._image1_point = None

        # UI elements
        self._cmbo_methods = None
        self._cmbo_filter = None

        self._init_ui()

    def _init_ui(self):
        pane = self._ui_create_pane()

        vbox_table = QVBoxLayout()
        vbox_table.addWidget(pane)
        vbox_table.addStretch(1)

        self.setLayout(vbox_table)

    def _ui_create_pane(self):
        label_width = 100

        self._slider_threshold = Slider("RANSAC Threshold", 5.0, 1.0, 20.0)
        self._slider_threshold.signal_value_changed.connect(self._refresh_transform)

        lbl_filter = QLabel("Filter")
        lbl_filter.setFixedWidth(label_width)
        self._cmbo_filter = QComboBox()
        self._cmbo_filter.setFixedWidth(150)
        self._cmbo_filter.currentIndexChanged.connect(self._filter_selection_changed)

        for f in TransformCalculator.FILTERS:
            self._cmbo_filter.addItem(f)
        self._cmbo_filter.setCurrentIndex(2)

        hbox_filter = QHBoxLayout()
        hbox_filter.addWidget(lbl_filter)
        hbox_filter.addWidget(self._cmbo_filter)
        hbox_filter.addStretch(1)

        lbl_method = QLabel("Method")
        lbl_method.setFixedWidth(label_width)
        self._cmbo_methods = QComboBox()
        self._cmbo_methods.setFixedWidth(150)
        self._cmbo_methods.currentIndexChanged.connect(self._method_selection_changed)

        for method in TransformCalculator.METHODS:
            self._cmbo_methods.addItem(method)

        hbox_method = QHBoxLayout()
        hbox_method.addWidget(lbl_method)
        hbox_method.addWidget(self._cmbo_methods)
        hbox_method.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_method)
        vbox.addLayout(hbox_filter)
        vbox.addWidget(self._slider_threshold)
        vbox.addStretch(1)

        box = QGroupBox("Transformation")
        box.setLayout(vbox)

        return box

    def set_crystal_match(self, crystal_match, matcher):
        self._matcher = matcher
        self._image1_point = crystal_match.image1_point()
        self._matches = crystal_match.feature_match_result().matches()
        self._refresh_transform()

    def _method_selection_changed(self):
        self._set_slider_enabled_state()
        self._refresh_transform()

    def _filter_selection_changed(self):
        self._set_slider_enabled_state()
        self._refresh_transform()

    def _set_slider_enabled_state(self):
        filter = self._get_filter_value()
        is_ransac = filter == TransformCalculator.RANSAC
        self._slider_threshold.setEnabled(is_ransac)

    def _refresh_transform(self):
        if self._matcher is None:
            return

        target_region_tl = self._matcher.make_target_region(self._image1_point).top_left()
        search_region_tl = self._matcher.make_search_region(self._image1_point).top_left()

        point1 = self._image1_point - target_region_tl
        point2 = None

        w = point1.x
        quad1 = Polygon([Point(0, 0), Point(2*w, 0), Point(2*w, 2*w), Point(0, 2*w)])
        quad2 = None

        calc = self._create_transform_calc()
        transform = calc.calculate_transform(self._matches)

        if transform is not None:
            transformed_point = transform.transform_points([self._image1_point])[0]
            point2 = transformed_point - search_region_tl

            p1 = self._image1_point

            def trans(x, y):
                return transform.transform_points([p1 + Point(x, y)])[0] - search_region_tl

            quad2 = Polygon([trans(-w, -w), trans(w, -w), trans(w, w), trans(-w, w)])

        self._emit_new_transform_signal(transform)
        self._emit_new_points_signal(point1, point2)
        self._emit_new_quads(quad1, quad2)

    def _create_transform_calc(self):
        method = self._get_method_value()
        filter = self._get_filter_value()
        threshold = self._slider_threshold.value()

        calc = TransformCalculator()
        calc.set_method(method)
        calc.set_filter(filter)
        calc.set_ransac_threshold(threshold)
        return calc

    def _get_method_value(self):
        return self._cmbo_methods.currentText()

    def _get_filter_value(self):
        return self._cmbo_filter.currentText()

    def _emit_new_transform_signal(self, transform):
        self.signal_new_transform.emit(transform)

    def _emit_new_points_signal(self, point1, point2):
        self.signal_new_points.emit(point1, point2)
        self.signal_updated_matches.emit(self._matches)

    def _emit_new_quads(self, quad1, quad2):
        self.signal_new_quads.emit(quad1, quad2)
