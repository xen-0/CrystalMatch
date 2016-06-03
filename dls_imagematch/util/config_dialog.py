import sys
import os

from PyQt4 import QtGui
from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, QPushButton, QGroupBox, QWidget

from .color import Color
from .config import IntConfigItem, ColorConfigItem, DirectoryConfigItem

LABEL_WIDTH = 100


class ValueConfigControl(QWidget):
    TEXT_WIDTH = 100

    def __init__(self, config_item, txt_width=TEXT_WIDTH):
        super(ValueConfigControl, self).__init__()

        self._config_item = config_item

        self._init_ui(txt_width)

    def _init_ui(self, txt_width):
        lbl_int = QLabel(self._config_item.tag())
        lbl_int.setFixedWidth(LABEL_WIDTH)

        self.txt_value = QLineEdit()
        self.txt_value.setFixedWidth(txt_width)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(lbl_int)
        hbox.addWidget(self.txt_value)
        hbox.addWidget(QLabel(self._config_item.units()))
        hbox.addStretch()

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

    def update_from_config(self):
        self.txt_value.setText(str(self._config_item.value()))

    def save_to_config(self):
        self._config_item.set(self.txt_value.text())


class DirectoryConfigControl(QWidget):
    BUTTON_WIDTH = 80
    TEXT_WIDTH = 200

    def __init__(self, config_item):
        super(DirectoryConfigControl, self).__init__()

        self._config_item = config_item

        self._init_ui()

    def _init_ui(self):
        self.txt_dir = QLineEdit()
        self.txt_dir.setFixedWidth(self.TEXT_WIDTH)

        lbl_dir = QLabel(self._config_item.tag())
        lbl_dir.setFixedWidth(LABEL_WIDTH)

        btn_show = QPushButton('View Files')
        btn_show.setFixedWidth(self.BUTTON_WIDTH)
        btn_show.clicked.connect(self._open_directory)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(lbl_dir)
        hbox.addWidget(self.txt_dir)
        hbox.addWidget(btn_show)
        hbox.addStretch()

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

    def update_from_config(self):
        self.txt_dir.setText(self._config_item.value())

    def save_to_config(self):
        self._config_item.set(self.txt_dir.text())

    def _open_directory(self):
        path = self.txt_dir.text()
        path = os.path.abspath(path)

        if sys.platform == 'win32':
            try:
                os.startfile(path)
            except OSError:
                QMessageBox.critical(self, "File Error", "Unable to find directory: '{}".format(path))
        else:
            QMessageBox.critical(self, "File Error", "Only available on Windows")


class ColorConfigControl(QWidget):
    STYLE = "background-color: {};"

    def __init__(self, config_item):
        super(ColorConfigControl, self).__init__()

        self._config_item = config_item
        self._color = None

        self._init_ui()

    def _init_ui(self):
        lbl_color = QLabel(self._config_item.tag())
        lbl_color.setFixedWidth(LABEL_WIDTH)
        self._swatch = QPushButton("")
        self._swatch.setFixedWidth(25)
        self._swatch.clicked.connect(self._choose_color)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(lbl_color)
        hbox.addWidget(self._swatch)
        hbox.addStretch()

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

    def update_from_config(self):
        self._color = self._config_item.value()
        self.set_swatch_color(self._color)

    def save_to_config(self):
        self._config_item.set(self._color)

    def _choose_color(self):
        self._color = self._get_dialog_color(self._color)
        self.set_swatch_color(self._color)

    def set_swatch_color(self, color):
        self._swatch.setStyleSheet(self.STYLE.format(color.to_hex()))

    @staticmethod
    def _get_dialog_color(start_color):
        color = start_color

        qt_col = QtGui.QColorDialog.getColor(start_color.to_qt())
        if qt_col.isValid():
            color = Color.from_qt(qt_col)

        return color


class _ConfigGroupBox:
    def __init__(self, name):
        self._name = name
        self._controls = []

    def add_control(self, control):
        self._controls.append(control)

    def assemble(self):
        grp_box = QGroupBox(self._name)
        vbox = QVBoxLayout()
        for control in self._controls:
            vbox.addWidget(control)

        grp_box.setLayout(vbox)
        return grp_box


class ConfigDialog(QtGui.QDialog):
    def __init__(self, config):
        super(ConfigDialog, self).__init__()

        self._config = config

        self._groups = []
        self._config_controls = []

        self.setWindowTitle('Config')

    def auto_layout(self):

        for item in self._config._items:
            self.add_item(item)

        self.finalize_layout()

    def start_group(self, name):
        group = _ConfigGroupBox(name)
        self._groups.append(group)

    def add_item(self, item):
        add = self._add_control

        if isinstance(item, IntConfigItem):
            add(ValueConfigControl(item, txt_width=40))
        elif isinstance(item, ColorConfigItem):
            add(ColorConfigControl(item))
        elif isinstance(item, DirectoryConfigItem):
            add(DirectoryConfigControl(item))

    def finalize_layout(self):
        hbox_btns = self._make_buttons()

        # ----- MAIN LAYOUT -----
        vbox = QVBoxLayout()
        for group in self._groups:
            vbox.addWidget(group.assemble())
        vbox.addStretch()
        vbox.addLayout(hbox_btns)

        self.setLayout(vbox)
        self._update_options_display()

    def _make_buttons(self):
        btn_cancel = QtGui.QPushButton("Cancel")
        btn_cancel.pressed.connect(self._dialog_close_cancel)
        btn_ok = QtGui.QPushButton("OK")
        btn_ok.pressed.connect(self._dialog_close_ok)
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.pressed.connect(self._dialog_apply_changes)
        btn_reset = QtGui.QPushButton("Reset All")
        btn_reset.pressed.connect(self._dialog_reset)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn_ok)
        hbox.addWidget(btn_cancel)
        hbox.addWidget(btn_apply)
        hbox.addWidget(btn_reset)
        hbox.addStretch(1)

        return hbox

    def _add_control(self, control):
        if len(self._groups) == 0:
            self.start_group("Config Group")

        group = self._groups[-1]
        group.add_control(control)
        self._config_controls.append(control)

    def _update_options_display(self):
        for control in self._config_controls:
            control.update_from_config()

    def _dialog_apply_changes(self):
        for control in self._config_controls:
            control.save_to_config()

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
