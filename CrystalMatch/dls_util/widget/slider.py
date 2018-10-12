import logging

from PyQt4.QtCore import Qt, pyqtSignal, pyqtBoundSignal
from PyQt4.QtGui import QWidget, QLabel, QSlider, QLineEdit, QHBoxLayout


class Slider(QWidget):
    """ A PyQt widget that includes a slider and linked textbox allowing display and editing
    of the selected integer value.
    """
    signal_value_changed = pyqtSignal(int)

    def __init__(self, name, initial, min_val, max_val, sld_width=180):
        super(Slider, self).__init__()
        self._min = int(min_val)
        self._max = int(max_val)
        self._init_ui(name, int(initial), sld_width)

    def _init_ui(self, name, initial, sld_width):
        self._lbl_name = QLabel(name)
        self._lbl_name.setFixedWidth(100)

        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setRange(self._min, self._max)
        self._slider.setFocusPolicy(Qt.NoFocus)
        self._slider.setValue(initial)
        self._slider.valueChanged[int].connect(self._value_changed)
        self._slider.setFixedWidth(sld_width)

        self._txt_value = QLineEdit(str(initial))
        assert (isinstance(self._txt_value.textChanged, pyqtBoundSignal))
        self._txt_value.textChanged.connect(self._value_changed)
        self._txt_value.setFixedWidth(50)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self._lbl_name)
        hbox.addWidget(self._slider)
        hbox.addWidget(self._txt_value)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def set_value(self, value):
        self._slider.setValue(value)

    def value(self):
        return self._slider.value()

    def _value_changed(self, value):
        try:
            if self._slider.value() != int(value):
                self._slider.setValue(int(value))
            if self._txt_value.text() != str(value):
                self._txt_value.setText(str(value))

            self.signal_value_changed.emit(int(value))

        except ValueError:
            logging.error("Value is not an integer: " + str(value))

        self._update_color()

    def _update_color(self):
        text = self._txt_value.text()
        valid = True

        try:
            val = int(text)
            if not (self._min <= val <= self._max):
                valid = False
        except ValueError:
            valid = False

        color = "white" if valid else "red"
        self._txt_value.setStyleSheet("background-color: {};".format(color))
