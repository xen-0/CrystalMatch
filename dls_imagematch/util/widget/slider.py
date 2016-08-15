from PyQt4 import QtGui, QtCore


class Slider(QtGui.QWidget):
    signal_value_changed = QtCore.pyqtSignal(int)

    def __init__(self, name, initial, min_val, max_val):
        super(Slider, self).__init__()
        self._min = int(min_val)
        self._max = int(max_val)
        self._init_ui(name, int(initial))

    def _init_ui(self, name, initial):
        self._lbl_name = QtGui.QLabel(name)
        self._lbl_name.setFixedWidth(100)

        self._slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self._slider.setRange(self._min, self._max)
        self._slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self._slider.setValue(initial)
        self._slider.valueChanged[int].connect(self._value_changed)
        self._slider.setFixedWidth(180)

        self._txt_value = QtGui.QLineEdit(str(initial))
        self._txt_value.textChanged.connect(self._value_changed)
        self._txt_value.setFixedWidth(50)

        hbox = QtGui.QHBoxLayout()
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

        except ValueError as e:
            print("Value is not an integer: " + str(value))

