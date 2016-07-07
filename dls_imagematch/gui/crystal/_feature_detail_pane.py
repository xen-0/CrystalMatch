from __future__ import division

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QTableWidget, QCheckBox, QGroupBox, QComboBox


class FeatureMatchDetailPane(QWidget):
    ALL = "All"
    GOOD_MATCHES = "Good Matches"
    BAD_MATCHES = "Bad Matches"

    signal_matches_selected = QtCore.pyqtSignal(object)
    signal_matches_filtered = QtCore.pyqtSignal(object)

    def __init__(self):
        super(FeatureMatchDetailPane, self).__init__()

        self._feature_match = None
        self._matches = []
        self._filtered_matches = []
        self._selected_matches = []

        # UI elements
        self._table = None
        self._cmbo_include = None
        self._cmbo_methods = None
        self._chk_highlight_selected = None

        self._init_ui()

    def _init_ui(self):
        table = self._ui_create_table()
        filters = self._ui_create_filters()

        vbox_table = QVBoxLayout()
        vbox_table.addWidget(filters)
        vbox_table.addWidget(table)
        vbox_table.addStretch(1)

        self.setLayout(vbox_table)

    def _ui_create_table(self):
        table = QTableWidget()
        table.setFixedWidth(300)
        table.setFixedHeight(700)
        table.setColumnCount(4)
        table.setRowCount(10)
        table.setHorizontalHeaderLabels(['Index', 'Method', 'Distance', 'Included'])
        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 80)
        table.setColumnWidth(2, 80)
        table.setColumnWidth(3, 80)
        table.setColumnHidden(0, True)
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table.currentItemChanged.connect(self._changed_selection)
        table.cellPressed.connect(self._changed_selection)
        self._table = table

        vbox = QVBoxLayout()
        vbox.addWidget(table)
        vbox.addStretch(1)

        box = QGroupBox("Matches")
        box.setLayout(vbox)

        return box

    def _ui_create_filters(self):
        label_width = 90

        lbl_highlight = QLabel("Highlight Selected")
        lbl_highlight.setFixedWidth(label_width)
        self._chk_highlight_selected = QCheckBox()
        self._chk_highlight_selected.setTristate(False)
        self._chk_highlight_selected.setCheckState(2)
        self._chk_highlight_selected.stateChanged.connect(self._changed_filters)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(lbl_highlight)
        hbox1.addWidget(self._chk_highlight_selected)
        hbox1.addStretch(1)

        lbl_include = QLabel("Include")
        lbl_include.setFixedWidth(label_width)
        self._cmbo_include = QComboBox()
        self._cmbo_include.setFixedWidth(100)
        self._cmbo_include.addItems([self.ALL, self.GOOD_MATCHES, self.BAD_MATCHES, "None"])
        self._cmbo_include.currentIndexChanged.connect(self._changed_filters)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(lbl_include)
        hbox2.addWidget(self._cmbo_include)
        hbox2.addStretch(1)

        lbl_method = QLabel("Method")
        lbl_method.setFixedWidth(label_width)
        self._cmbo_methods = QComboBox()
        self._cmbo_methods.setFixedWidth(100)
        self._cmbo_methods.currentIndexChanged.connect(self._changed_filters)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(lbl_method)
        hbox3.addWidget(self._cmbo_methods)
        hbox3.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addStretch(1)

        box = QGroupBox("Filter")
        box.setLayout(vbox)

        return box

    def set_feature_match(self, feature_match):
        self._feature_match = feature_match
        self._matches = feature_match.matches
        self._filtered_matches = self._matches
        self._selected_matches = []

        self._update_method_dropdown(self._matches)
        self._changed_filters()

    def clear_all(self):
        self._feature_match = None
        self._matches = []
        self._filtered_matches = []
        self._selected_matches = []

        self._clear_selection()
        self._update_method_dropdown([])
        self._changed_filters()

    def _clear_selection(self):
        self._table.selectionModel().clearSelection()

    def set_enabled(self, enabled):
        self._cmbo_include.setEnabled(enabled)
        self._cmbo_methods.setEnabled(enabled)
        self._chk_highlight_selected.setEnabled(enabled)
        self._table.setEnabled(enabled)

    def _changed_filters(self):
        self._update_selected_matches()
        self._update_filtered_matches()
        self._clear_selection()

        self._update_table()
        self.signal_matches_filtered.emit(self._filtered_matches)

    def _changed_selection(self):
        print("--Changed Selection")
        self._update_selected_matches()
        self.signal_matches_selected.emit(self._selected_matches)

    def _update_method_dropdown(self, matches):
        methods = {}

        for match in matches:
            key = match.method()
            if key in methods:
                methods[key] += 1
            else:
                methods[key] = 1

        self._cmbo_methods.clear()
        self._cmbo_methods.addItem("{} ({})".format(self.ALL, len(matches)), self.ALL)
        for key, value in methods.iteritems():
            self._cmbo_methods.addItem("{} ({})".format(key, value), key)

    def _update_table(self):
        matches = self._filtered_matches
        selected = self._selected_matches

        num_results = len(matches)
        self._table.clearContents()
        self._table.setRowCount(num_results)

        for row, match in enumerate(matches):
            index = self._matches.index(match)
            self._populate_row(match, row, index, selected)

        self._update_selected_matches()

    def _populate_row(self, match, row, index, selected):
        distance = '{:.3f}'.format(match.distance())
        included = 'X' if match.is_in_transformation() else ''
        items = [index, match.method(), distance, included]

        for col, item in enumerate(items):
            table_item = QtGui.QTableWidgetItem(str(item))
            table_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self._table.setItem(row, col, table_item)
            if match in selected:
                self._table.setItemSelected(table_item, True)

    def _update_filtered_matches(self):
        matches = self._matches
        matches = self._filter_matches_by_include(matches)
        matches = self._filter_matches_by_method(matches)
        self._filtered_matches = matches

    def _update_selected_matches(self):
        rows = self._table.selectionModel().selectedRows()
        rows = [r.row() for r in rows]
        selected = [self._filtered_matches[r] for r in rows]

        self._selected_matches = selected

    def _filter_matches_by_include(self, matches):
        if self._cmbo_include is None:
            return []

        include = self._cmbo_include.currentText()
        if include == self.ALL:
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

    def _get_highlighted_matches(self):
        use_highlights = self._chk_highlight_selected.checkState() != 0
        if use_highlights:
            return self._selected_matches
        else:
            return []
