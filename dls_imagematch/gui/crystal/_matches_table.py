from __future__ import division

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QVBoxLayout, QTableWidget, QGroupBox


class FeatureMatchTable(QWidget):
    signal_matches_selected = QtCore.pyqtSignal(object)

    def __init__(self):
        super(FeatureMatchTable, self).__init__()

        self._feature_match = None
        self._matches = []
        self._selected_matches = []

        # UI elements
        self._table = None

        self._init_ui()

    def _init_ui(self):
        table = self._ui_create_table()

        vbox_table = QVBoxLayout()
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

    def clear_all(self):
        self._matches = []
        self._selected_matches = []

        self._clear_selection()
        self._update_method_dropdown([])
        self._changed_filters()

    def display_matches(self, matches):
        self.setEnabled(True)
        self._matches = matches
        self._update_table()

    def _clear_selection(self):
        self._table.selectionModel().clearSelection()

    def _changed_selection(self):
        self._update_selected_matches()
        self.signal_matches_selected.emit(self._selected_matches)

    def _update_table(self):
        matches = self._matches
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

    def _update_selected_matches(self):
        rows = self._table.selectionModel().selectedRows()
        rows = [r.row() for r in rows]
        selected = [self._matches[r] for r in rows]

        self._selected_matches = selected
