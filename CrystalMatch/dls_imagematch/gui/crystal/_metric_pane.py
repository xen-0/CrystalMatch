from __future__ import division

from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox


class MetricPane(QWidget):
    def __init__(self):
        super(MetricPane, self).__init__()

        self._crystal_match_result = None
        self._transform = None

        self._init_ui()

    def _init_ui(self):
        pane = self._ui_create_pane()

        vbox = QVBoxLayout()
        vbox.addWidget(pane)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def _ui_create_pane(self):
        grp_box = QGroupBox("Results Summary")

        hbox_matches, self._lbl_matches = self._ui_create_label("Matches:", "0")
        hbox_good_matches, self._lbl_good_matches = self._ui_create_label("Good Matches:", "0")
        hbox_avg_error, self._lbl_avg_error = self._ui_create_label("Avg Trans. Error:", "0")

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_matches)
        vbox.addLayout(hbox_good_matches)
        vbox.addLayout(hbox_avg_error)
        vbox.addStretch(1)

        grp_box.setLayout(vbox)
        return grp_box

    @staticmethod
    def _ui_create_label(tag, value):
        tag_width = 120

        tag_label = QLabel(tag)
        tag_label.setStyleSheet("font-weight:bold;")
        tag_label.setFixedWidth(tag_width)

        label = QLabel(value)

        hbox = QHBoxLayout()
        hbox.addWidget(tag_label)
        hbox.addWidget(label)
        hbox.addStretch(1)
        return hbox, label

    def set_crystal_match_result(self, crystal_match_result):
        self._crystal_match_result = crystal_match_result
        result = crystal_match_result.feature_match_result()

        num_matches = result.num_matches()
        self._lbl_matches.setText(str(num_matches))

        num_good_matches = result.num_good_matches()
        percent = 0 if num_matches == 0 else num_good_matches / num_matches * 100
        msg = "{}   ({:.1f}%)".format(num_good_matches, percent)
        self._lbl_good_matches.setText(msg)

        average_transform_error = result.mean_transform_error()
        self._lbl_avg_error.setText("{:.2f}".format(average_transform_error))

    def set_transform(self, transform):
        self._transform = transform
        if self._crystal_match_result is not None:
            self.set_crystal_match_result(self._crystal_match_result)
