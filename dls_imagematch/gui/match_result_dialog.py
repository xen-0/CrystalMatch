
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QTableWidget, QCheckBox


class FeatureMatchResultDialog(QDialog):
    """ Dialog that displays the Region Selector Frame and stores the result so that it may be
    retrieved by the caller.
    """
    def __init__(self, match_result):
        super(FeatureMatchResultDialog, self).__init__()

        self._match_result = match_result

        self._init_ui()

        self._display_image(match_result.matches_image())
        self._populate_table(match_result)

    def _init_ui(self):
        self.setWindowTitle('Feature Match Result')

        self._frame = QLabel()
        self._frame.setFixedSize(800, 800)

        self._table = self._ui_create_table()

        filters_layout = self._ui_create_filters()

        vbox_table = QVBoxLayout()
        vbox_table.addWidget(self._table)
        vbox_table.addLayout(filters_layout)
        vbox_table.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox_table)
        hbox.addWidget(self._frame)
        hbox.addStretch()

        self.setLayout(hbox)

    def _ui_create_table(self):
        table = QTableWidget()
        table.setFixedWidth(300)
        table.setFixedHeight(600)
        table.setColumnCount(3)
        table.setRowCount(10)
        table.setHorizontalHeaderLabels(['Method', 'Distance', 'Included'])
        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 80)
        table.setColumnWidth(2, 80)
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        return table

    def _ui_create_filters(self):
        self._chk_include_all = QCheckBox("Include all matches")
        self._chk_include_all.setTristate(False)
        self._chk_include_all.setCheckState(False)
        self._chk_include_all.stateChanged.connect(self._apply_filters)

        vbox = QVBoxLayout()
        vbox.addWidget(self._chk_include_all)

        return vbox

    def _display_image(self, image):
        """ Display the specified Image object in the frame, scaled to fit the frame and maintain aspect ratio. """
        pixmap = image.to_qt_pixmap(self._frame.size())
        self._frame.setPixmap(pixmap)

    def _populate_table(self, match_result):
        """ Called when a new row is selected on the record table. Displays all of the
        barcodes from the selected record in the barcode table. By default, valid barcodes are
        highlighted green, invalid barcodes are highlighted red, and empty slots are grey.
        """
        matches = match_result.matches
        num_results = len(matches)
        self._table.clearContents()
        self._table.setRowCount(num_results)

        for n, match in enumerate(matches):
            self._populate_row(match, n)

    def _populate_row(self, match, row):
        distance = '{:.3f}'.format(match.distance())
        included = 'X' if match.is_in_transformation() else ''
        items = [match.method(), distance, included]
        for col, item in enumerate(items):
            table_item = QtGui.QTableWidgetItem(str(item))
            table_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self._table.setItem(row, col, table_item)

    def _apply_filters(self):

        include_all = self._chk_include_all.checkState() != 0

        matches = self._match_result.matches
        if not include_all:
            matches = [m for m in matches if m.is_in_transformation()]

        image = self._match_result.matches_image(matches)
        self._display_image(image)
