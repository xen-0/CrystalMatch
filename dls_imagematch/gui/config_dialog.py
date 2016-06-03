import sys
import os

from PyQt4 import QtGui
from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QPushButton, QGroupBox

from dls_imagematch.util import Color


class ConfigDialog(QtGui.QDialog):

    def __init__(self, config):
        super(ConfigDialog, self).__init__()

        self._config = config

        self._color_align = None
        self._color_search = None
        self._color_xtal_img1 = None
        self._color_xtal_img2 = None

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

        # ----- ALIGNMENT -------
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

        # Group Box
        grp_align = QGroupBox("Image Alignment")
        vbox_grp_align = QVBoxLayout()
        vbox_grp_align.addLayout(hbox_color_align)
        grp_align.setLayout(vbox_grp_align)

        # ----- XTAL SEARCH -------
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

        # Img1 Xtal Selection Color
        lbl_color_xtal_img1 = QLabel("Img1 Xtal Color:")
        lbl_color_xtal_img1.setFixedWidth(LABEL_WIDTH)
        self.btn_color_xtal_img1 = QPushButton("")
        self.btn_color_xtal_img1.setFixedWidth(25)
        self.btn_color_xtal_img1.clicked.connect(self._set_color_xtal_img1)
        self.btn_color_xtal_img1.setStyleSheet("background-color: black;")

        hbox_color_xtal_img1 = QHBoxLayout()
        hbox_color_xtal_img1.addWidget(lbl_color_xtal_img1)
        hbox_color_xtal_img1.addWidget(self.btn_color_xtal_img1)
        hbox_color_xtal_img1.addStretch()

        # Img2 Xtal Selection Color
        lbl_color_xtal_img2 = QLabel("Img2 Xtal Color:")
        lbl_color_xtal_img2.setFixedWidth(LABEL_WIDTH)
        self.btn_color_xtal_img2 = QPushButton("")
        self.btn_color_xtal_img2.setFixedWidth(25)
        self.btn_color_xtal_img2.clicked.connect(self._set_color_xtal_img2)
        self.btn_color_xtal_img2.setStyleSheet("background-color: black;")

        hbox_color_xtal_img2 = QHBoxLayout()
        hbox_color_xtal_img2.addWidget(lbl_color_xtal_img2)
        hbox_color_xtal_img2.addWidget(self.btn_color_xtal_img2)
        hbox_color_xtal_img2.addStretch()

        # Search Width
        self.txt_search_width = QLineEdit()
        self.txt_search_width.setFixedWidth(40)
        lbl_search_width = QLabel("Search Width:")
        lbl_search_width.setFixedWidth(LABEL_WIDTH)

        hbox_search_width = QHBoxLayout()
        hbox_search_width.addWidget(lbl_search_width)
        hbox_search_width.addWidget(self.txt_search_width)
        hbox_search_width.addWidget(QLabel('px'))
        hbox_search_width.addStretch()

        # Search Height
        self.txt_search_height = QLineEdit()
        self.txt_search_height.setFixedWidth(40)
        lbl_search_height = QLabel("Search Height:")
        lbl_search_height.setFixedWidth(LABEL_WIDTH)

        hbox_search_height = QHBoxLayout()
        hbox_search_height.addWidget(lbl_search_height)
        hbox_search_height.addWidget(self.txt_search_height)
        hbox_search_height.addWidget(QLabel('px'))
        hbox_search_height.addStretch()

        # Search Region Color
        lbl_color_search = QLabel("Search Box Color:")
        lbl_color_search.setFixedWidth(LABEL_WIDTH)
        self.btn_color_search = QPushButton("")
        self.btn_color_search.setFixedWidth(25)
        self.btn_color_search.clicked.connect(self._set_color_search)
        self.btn_color_search.setStyleSheet("background-color: black;")

        hbox_color_search = QHBoxLayout()
        hbox_color_search.addWidget(lbl_color_search)
        hbox_color_search.addWidget(self.btn_color_search)
        hbox_color_search.addStretch()

        # Group Box
        grp_search = QGroupBox("Xtal Search")
        vbox_grp_search = QVBoxLayout()
        vbox_grp_search.addLayout(hbox_region_size)
        vbox_grp_search.addLayout(hbox_search_width)
        vbox_grp_search.addLayout(hbox_search_height)
        vbox_grp_search.addLayout(hbox_color_xtal_img1)
        vbox_grp_search.addLayout(hbox_color_xtal_img2)
        vbox_grp_search.addLayout(hbox_color_search)
        grp_search.setLayout(vbox_grp_search)

        # ----- DIRECTORIES -------
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

        # Group Box
        grp_dirs = QGroupBox("Directories")
        vbox_grp_dirs = QVBoxLayout()
        vbox_grp_dirs.addLayout(hbox_input_dir)
        vbox_grp_dirs.addLayout(hbox_output_dir)
        vbox_grp_dirs.addLayout(hbox_samples_dir)
        grp_dirs.setLayout(vbox_grp_dirs)

        # ----- OK /CANCEL BUTTONS -------
        btn_cancel = QtGui.QPushButton("Cancel")
        btn_cancel.pressed.connect(self._dialog_close_cancel)
        btn_ok = QtGui.QPushButton("OK")
        btn_ok.pressed.connect(self._dialog_close_ok)
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.pressed.connect(self._dialog_apply_changes)
        btn_reset = QtGui.QPushButton("Reset All")
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
        vbox.addWidget(grp_align)
        vbox.addWidget(grp_search)
        vbox.addWidget(grp_dirs)
        vbox.addStretch()
        vbox.addLayout(hbox_ok_cancel)

        self.setLayout(vbox)

    def _update_options_display(self):
        self.txt_region_size.setText(str(self._config.region_size.value()))
        self.txt_search_width.setText(str(self._config.search_width.value()))
        self.txt_search_height.setText(str(self._config.search_height.value()))
        self.txt_input_dir.setText(self._config.input_dir.value())
        self.txt_samples_dir.setText(self._config.samples_dir.value())
        self.txt_output_dir.setText(self._config.output_dir.value())

        self._color_align = self._config.color_align.value()
        self._color_search = self._config.color_search.value()
        self._color_xtal_img1 = self._config.color_xtal_img1.value()
        self._color_xtal_img2 = self._config.color_xtal_img2.value()

        style = "background-color: {};"
        self.btn_color_align.setStyleSheet(style.format(self._color_align.to_hex()))
        self.btn_color_search.setStyleSheet(style.format(self._color_search.to_hex()))
        self.btn_color_xtal_img1.setStyleSheet(style.format(self._color_xtal_img1.to_hex()))
        self.btn_color_xtal_img2.setStyleSheet(style.format(self._color_xtal_img2.to_hex()))

    def _open_input_dir(self):
        path = self._config.input_dir.value()
        path = os.path.abspath(path)
        self._open_directory(path)

    def _open_samples_dir(self):
        path = self._config.samples_dir.value()
        path = os.path.abspath(path)
        self._open_directory(path)

    def _open_output_dir(self):
        path = self._config.output_dir.value()
        path = os.path.abspath(path)
        self._open_directory(path)

    def _open_directory(self, abspath):
        if sys.platform == 'win32':
            try:
                os.startfile(abspath)
            except OSError:
                QMessageBox.critical(self, "File Error", "Unable to find directory: '{}".format(abspath))
        else:
            QMessageBox.critical(self, "File Error", "Only available on Windows")

    def _set_color_align(self):
        color = self._get_dialog_color(self._color_align)
        self._color_align = color
        self.btn_color_align.setStyleSheet("background-color: {};".format(color.to_hex()))

    def _set_color_search(self):
        color = self._get_dialog_color(self._color_search)
        self._color_search = color
        self.btn_color_search.setStyleSheet("background-color: {};".format(color.to_hex()))

    def _set_color_xtal_img1(self):
        color = self._get_dialog_color(self._color_xtal_img1)
        self._color_xtal_img1 = color
        self.btn_color_xtal_img1.setStyleSheet("background-color: {};".format(color.to_hex()))

    def _set_color_xtal_img2(self):
        color = self._get_dialog_color(self._color_xtal_img2)
        self._color_xtal_img2 = color
        self.btn_color_xtal_img2.setStyleSheet("background-color: {};".format(color.to_hex()))

    @staticmethod
    def _get_dialog_color(start_color):
        color = start_color

        qt_col = QtGui.QColorDialog.getColor(start_color.to_qt())
        if qt_col.isValid():
            color = Color.from_qt(qt_col)

        return color

    def _dialog_apply_changes(self):
        cfg = self._config

        cfg.region_size.set(self.txt_region_size.text())
        cfg.search_width.set(self.txt_search_width.text())
        cfg.search_height.set(self.txt_search_height.text())
        cfg.input_dir.set(self.txt_input_dir.text())
        cfg.samples_dir.set(self.txt_samples_dir.text())
        cfg.output_dir.set(self.txt_output_dir.text())
        cfg.color_align.set(self._color_align)
        cfg.color_search.set(self._color_search)
        cfg.color_xtal_img1.set(self._color_xtal_img1)
        cfg.color_xtal_img2.set(self._color_xtal_img2)

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
