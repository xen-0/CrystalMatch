import sys
import os

from PyQt4 import QtGui
from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QPushButton


class ConfigDialog(QtGui.QDialog):

    def __init__(self, config):
        super(ConfigDialog, self).__init__()

        self._config = config

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
        hbox_region_size.addStretch()

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
        vbox.addLayout(hbox_input_dir)
        vbox.addLayout(hbox_output_dir)
        vbox.addLayout(hbox_samples_dir)
        vbox.addStretch()
        vbox.addLayout(hbox_ok_cancel)

        self.setLayout(vbox)

    def _update_options_display(self):
        self.txt_region_size.setText(str(self._config.region_size))
        self.txt_input_dir.setText(self._config.input_dir)
        self.txt_samples_dir.setText(self._config.samples_dir)
        self.txt_output_dir.setText(self._config.output_dir)

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

    def _dialog_apply_changes(self):
        self._config.region_size = self.txt_region_size.text()
        self._config.input_dir = self.txt_input_dir.text()
        self._config.samples_dir = self.txt_samples_dir.text()
        self._config.output_dir = self.txt_output_dir.text()

        self._config.update_config_file()
        self._update_options_display()

    def _dialog_close_ok(self):
        self._dialog_apply_changes()
        self.close()

    def _dialog_close_cancel(self):
        self.close()

    def _dialog_reset(self):
        self._config.reset_all()
        self._update_options_display()


