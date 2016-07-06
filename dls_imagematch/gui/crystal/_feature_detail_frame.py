from __future__ import division

from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox


class FeatureMatchDetailFrame(QWidget):

    def __init__(self):
        super(FeatureMatchDetailFrame, self).__init__()

        # UI elements
        self._frame = None

        self._init_ui()

    def _init_ui(self):
        frame = self._ui_create_frame()

        hbox = QHBoxLayout()
        hbox.addWidget(frame)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def _ui_create_frame(self):
        self._frame = QLabel()
        self._frame.setFixedSize(800, 800)

        vbox = QVBoxLayout()
        vbox.addWidget(self._frame)
        vbox.addStretch(1)

        box = QGroupBox("Match Image")
        box.setLayout(vbox)
        return box

    def display_image(self, image):
        pixmap = image.to_qt_pixmap(self._frame.size())
        self._frame.setPixmap(pixmap)


