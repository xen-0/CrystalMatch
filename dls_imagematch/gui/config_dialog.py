import sys
import os

from PyQt4 import QtGui
from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QPushButton

from dls_imagematch.util import Color


class ConfigDialog(QtGui.QDialog):

    def __init__(self, config):
        super(ConfigDialog, self).__init__()

        self._config = config

        self._color_align = None
        self._color_search = None

        self._init_ui()
        self._update_options_display()

    def _init_ui(self):
        """ Create the basic elements of the user interface.
        """
        self.setGeometry(100, 100, 450, 400)
        self.setWindowTitle('Options')
        self.setWindowIcon(QtGui.QIcon('web.png'))

        LABEL_WIDTH = 100
        BUTTON_WIDTH = 120

        # Region Size
        self.txt_region_size = QLineEdit()
        self.txt_region_size.setFixedWidth(40)
        lbl_region_size = QLabel("Region Size:")
        lbl_region_size.setFixedWidth(LABEL_WIDTH)

        hbox_region_size = QHBoxLayout()
        hbox_region_size.addWidget(lbl_region_size)
        hbox_region_size.addWidget(self.txt_region_size)
        hbox_region_size.addWidget(QLabel('px'))
        hbox_region_size.addStretch()

        # Search Width
        self.txt_search_width = QLineEdit()
        self.txt_search_width.setFixedWidth(40)
        lbl_search_width = QLabel("Xtal Search Width:")
        lbl_search_width.setFixedWidth(LABEL_WIDTH)

        hbox_search_width = QHBoxLayout()
        hbox_search_width.addWidget(lbl_search_width)
        hbox_search_width.addWidget(self.txt_search_width)
        hbox_search_width.addWidget(QLabel('px'))
        hbox_search_width.addStretch()

        # Search Height
        self.txt_search_height = QLineEdit()
        self.txt_search_height.setFixedWidth(40)
        lbl_search_height = QLabel("Xtal Search Height:")
        lbl_search_height.setFixedWidth(LABEL_WIDTH)

        hbox_search_height = QHBoxLayout()
        hbox_search_height.addWidget(lbl_search_height)
        hbox_search_height.addWidget(self.txt_search_height)
        hbox_search_height.addWidget(QLabel('px'))
        hbox_search_height.addStretch()

        # Input Directory
        self.txt_input_dir = QLineEdit()
        lbl_input_dir = QLabel("Input Directory:")
        lbl_input_dir.setFixedWidth(LABEL_WIDTH)

        btn_show_input_dir = QPushButton('View Input Files')
        btn_show_input_dir.setFixedWidth(BUTTON_WIDTH)
        btn_show_input_dir.clicked.connect(self._open_input_dir)

        hbox_input_dir = QHBoxLayout()
        hbox_input_dir.addWidget(lbl_input_dir)
        hbox_input_dir.addWidget(self.txt_input_dir)
        hbox_input_dir.addWidget(btn_show_input_dir)

        # Output Directory
        self.txt_output_dir = QLineEdit()
        lbl_output_dir = QLabel("Output Directory:")
        lbl_output_dir.setFixedWidth(LABEL_WIDTH)

        btn_show_output_dir = QPushButton('View Output Files')
        btn_show_output_dir.setFixedWidth(BUTTON_WIDTH)
        btn_show_output_dir.clicked.connect(self._open_output_dir)

        hbox_output_dir = QHBoxLayout()
        hbox_output_dir.addWidget(lbl_output_dir)
        hbox_output_dir.addWidget(self.txt_output_dir)
        hbox_output_dir.addWidget(btn_show_output_dir)

        # Samples Directory
        self.txt_samples_dir = QLineEdit()
        lbl_samples_dir = QLabel("Samples Directory:")
        lbl_samples_dir.setFixedWidth(LABEL_WIDTH)

        btn_show_samples_dir = QPushButton('View Samples Files')
        btn_show_samples_dir.setFixedWidth(BUTTON_WIDTH)
        btn_show_samples_dir.clicked.connect(self._open_samples_dir)

        hbox_samples_dir = QHBoxLayout()
        hbox_samples_dir.addWidget(lbl_samples_dir)
        hbox_samples_dir.addWidget(self.txt_samples_dir)
        hbox_samples_dir.addWidget(btn_show_samples_dir)

        # Align Color
        lbl_color_align = QLabel("Align Color:")
        lbl_color_align.setFixedWidth(LABEL_WIDTH)
        self.btn_color_align = QPushButton("")
        self.btn_color_align.setFixedWidth(25)
        self.btn_color_align.clicked.connect(self._set_color_align)
        self.btn_color_align.setStyleSheet("background-color: black;")

        hbox_color_align = QHBoxLayout()
        hbox_color_align.addWidget(lbl_color_align)
        hbox_color_align.addWidget(self.btn_color_align)
        hbox_color_align.addStretch()

        # Search Color
        lbl_color_search = QLabel("Xtal Search Color:")
        lbl_color_search.setFixedWidth(LABEL_WIDTH)
        self.btn_color_search = QPushButton("")
        self.btn_color_search.setFixedWidth(25)
        self.btn_color_search.clicked.connect(self._set_color_search)
        self.btn_color_search.setStyleSheet("background-color: black;")

        hbox_color_search = QHBoxLayout()
        hbox_color_search.addWidget(lbl_color_search)
        hbox_color_search.addWidget(self.btn_color_search)
        hbox_color_search.addStretch()

        # ----- OK /CANCEL BUTTONS -------
        btn_cancel = QtGui.QPushButton("Cancel")
        btn_cancel.pressed.connect(self._dialog_close_cancel)
        btn_ok = QtGui.QPushButton("OK")
        btn_ok.pressed.connect(self._dialog_close_ok)
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.pressed.connect(self._dialog_apply_changes)
        btn_reset = QtGui.QPushButton("Reset")
        btn_reset.pressed.connect(self._dialog_reset)

        hbox_ok_cancel = QtGui.QHBoxLayout()
        hbox_ok_cancel.addStretch(1)
        hbox_ok_cancel.addWidget(btn_ok)
        hbox_ok_cancel.addWidget(btn_cancel)
        hbox_ok_cancel.addWidget(btn_apply)
        hbox_ok_cancel.addWidget(btn_reset)
        hbox_ok_cancel.addStretch(1)

        # ----- MAIN LAYOUT -----
        vbox = QVBoxLayout()
        vbox.addLayout(hbox_region_size)
        vbox.addLayout(hbox_search_width)
        vbox.addLayout(hbox_search_height)
        vbox.addLayout(hbox_input_dir)
        vbox.addLayout(hbox_output_dir)
        vbox.addLayout(hbox_samples_dir)
        vbox.addLayout(hbox_color_align)
        vbox.addLayout(hbox_color_search)
        vbox.addStretch()
        vbox.addLayout(hbox_ok_cancel)

        self.setLayout(vbox)

    def _update_options_display(self):
        self.txt_region_size.setText(str(self._config.region_size))
        self.txt_search_width.setText(str(self._config.search_width))
        self.txt_search_height.setText(str(self._config.search_height))
        self.txt_input_dir.setText(self._config.input_dir)
        self.txt_samples_dir.setText(self._config.samples_dir)
        self.txt_output_dir.setText(self._config.output_dir)

        self._color_align = self._config.color_align
        self._color_search = self._config.color_search

        style = "background-color: {};"
        self.btn_color_align.setStyleSheet(style.format(self._color_align.to_hex()))
        self.btn_color_search.setStyleSheet(style.format(self._color_search.to_hex()))

    def _open_input_dir(self):
        path = self._config.input_dir
        path = os.path.abspath(path)
        self._open_directory(path)

    def _open_samples_dir(self):
        path = self._config.samples_dir
        path = os.path.abspath(path)
        self._open_directory(path)

    def _open_output_dir(self):
        path = self._config.output_dir
        path = os.path.abspath(path)
        self._open_directory(path)

    def _open_directory(self, abspath):
        if sys.platform == 'win32':
            try:
                os.startfile(abspath)
            except FileNotFoundError:
                QMessageBox.critical(self, "File Error", "Unable to find directory: '{}".format(abspath))
        else:
            QMessageBox.critical(self, "File Error", "Only available on Windows")

    def _set_color_align(self):
        color = self._get_dialog_color()
        self._color_align = color
        self.btn_color_align.setStyleSheet("background-color: {};".format(color.to_hex()))

    def _set_color_search(self):
        color = self._get_dialog_color()
        self._color_search = color
        self.btn_color_search.setStyleSheet("background-color: {};".format(color.to_hex()))

    @staticmethod
    def _get_dialog_color():
        qt_col = QtGui.QColorDialog.getColor()
        if qt_col.isValid():
            color = Color.from_qt(qt_col)
            print(color.to_hex())
            return color
        else:
            return Color.Black()

    def _dialog_apply_changes(self):
        cfg = self._config

        cfg.region_size = self.txt_region_size.text()
        cfg.search_width = self.txt_search_width.text()
        cfg.search_height = self.txt_search_height.text()
        cfg.input_dir = self.txt_input_dir.text()
        cfg.samples_dir = self.txt_samples_dir.text()
        cfg.output_dir = self.txt_output_dir.text()
        cfg.color_align = self._color_align
        cfg.color_search = self._color_search

        cfg.update_config_file()
        self._update_options_display()

    def _dialog_close_ok(self):
        self._dialog_apply_changes()
        self.close()

    def _dialog_close_cancel(self):
        self.close()

    def _dialog_reset(self):
        self._config.reset_all()
        self._update_options_display()


