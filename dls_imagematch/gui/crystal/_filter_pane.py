from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QComboBox


class FilterPane(QWidget):
    ALL = "All"
    ALL_MATCHES = "All Matches"
    GOOD_MATCHES = "Good Matches"
    BAD_MATCHES = "Bad Matches"
    NO_MATCHES = "No Matches"

    signal_matches_filtered = QtCore.pyqtSignal(object)

    def __init__(self):
        super(FilterPane, self).__init__()

        self._matches = []
        self._filtered_matches = []
        self._match_methods = []

        # UI elements
        self._cmbo_include = None
        self._cmbo_methods = None

        self._init_ui()

    def _init_ui(self):
        filters = self._ui_create_filters()

        vbox_table = QVBoxLayout()
        vbox_table.addWidget(filters)
        vbox_table.addStretch(1)

        self.setLayout(vbox_table)

    def _ui_create_filters(self):
        label_width = 100

        lbl_include = QLabel("Include")
        lbl_include.setFixedWidth(label_width)
        self._cmbo_include = QComboBox()
        self._cmbo_include.setFixedWidth(150)
        self._cmbo_include.addItems([self.ALL_MATCHES, self.GOOD_MATCHES, self.BAD_MATCHES, self.NO_MATCHES])
        self._cmbo_include.currentIndexChanged.connect(self._include_selection_changed)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(lbl_include)
        hbox2.addWidget(self._cmbo_include)
        hbox2.addStretch(1)

        lbl_method = QLabel("Detector")
        lbl_method.setFixedWidth(label_width)
        self._cmbo_methods = QComboBox()
        self._cmbo_methods.setFixedWidth(150)
        self._cmbo_methods.addItem(self.ALL, self.ALL)
        self._cmbo_methods.currentIndexChanged.connect(self._method_selection_changed)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(lbl_method)
        hbox3.addWidget(self._cmbo_methods)
        hbox3.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addStretch(1)

        box = QGroupBox("Display")
        box.setLayout(vbox)

        return box

    def set_matches(self, matches):
        self.setEnabled(True)
        self._matches = matches
        self._filtered_matches = self._matches
        self._match_methods = self._get_match_methods(matches)

        self._update_include_dropdown()
        self._update_method_dropdown()
        self._changed_filters()

    def clear_all(self):
        self._matches = []
        self._filtered_matches = []

        self._clear_selection()
        self._update_method_dropdown([])
        self._changed_filters()

    def _changed_filters(self):
        self._update_filtered_matches()
        self.signal_matches_filtered.emit(self._filtered_matches)

    def _update_include_dropdown(self):
        index = self._cmbo_include.currentIndex()

        all_count = len(self._matches)
        good_count = len([m for m in self._matches if m.is_in_transformation()])
        bad_count = all_count - good_count

        self._cmbo_include.clear()
        self._cmbo_include.addItem("{} ({})".format(self.ALL_MATCHES, all_count), self.ALL_MATCHES)
        self._cmbo_include.addItem("{} ({})".format(self.GOOD_MATCHES, good_count), self.GOOD_MATCHES)
        self._cmbo_include.addItem("{} ({})".format(self.BAD_MATCHES, bad_count), self.BAD_MATCHES)
        self._cmbo_include.addItem(self.NO_MATCHES, self.NO_MATCHES)

        self._cmbo_include.setCurrentIndex(index)

    def _update_method_dropdown(self):
        index = self._cmbo_methods.currentIndex()

        matches = self._filter_matches_by_include(self._matches)
        methods = {method: 0 for method in self._match_methods}

        for match in matches:
            key = match.method()
            methods[key] += 1

        self._cmbo_methods.clear()
        self._cmbo_methods.addItem("{} ({})".format(self.ALL, len(matches)), self.ALL)
        for method in self._match_methods:
            count = methods[method]
            self._cmbo_methods.addItem("{} ({})".format(method, count), method)

        self._cmbo_methods.setCurrentIndex(index)

    def _get_match_methods(self, matches):
        methods = []
        for match in matches:
            method = match.method()
            if method not in methods:
                methods.append(method)
        return methods

    def _include_selection_changed(self):
        self._update_method_dropdown()
        self._changed_filters()

    def _method_selection_changed(self):
        self._changed_filters()

    def _update_filtered_matches(self):
        matches = self._matches
        matches = self._filter_matches_by_include(matches)
        matches = self._filter_matches_by_method(matches)
        self._filtered_matches = matches

    def _filter_matches_by_include(self, matches):
        if self._cmbo_include is None:
            return []

        index = self._cmbo_include.currentIndex()
        include = self._cmbo_include.itemData(index).toString()

        if include == self.ALL_MATCHES:
            matches = matches
        elif include == self.GOOD_MATCHES:
            matches = [m for m in matches if m.is_in_transformation()]
        elif include == self.BAD_MATCHES:
            matches = [m for m in matches if not m.is_in_transformation()]
        else:
            matches = []

        return matches

    def _filter_matches_by_method(self, matches):
        if self._cmbo_methods is None:
            return []

        method_ind = self._cmbo_methods.currentIndex()
        method = self._cmbo_methods.itemData(method_ind).toString()

        if method != self.ALL:
            matches = [m for m in matches if m.method() == method]
        return matches
