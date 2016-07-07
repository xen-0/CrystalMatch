from __future__ import division

from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox

from dls_imagematch.match.feature import FeaturePainter


class FeatureMatchDetailFrame(QWidget):

    def __init__(self):
        super(FeatureMatchDetailFrame, self).__init__()

        self._frame = None

        self._painter = None
        self._matches = []
        self._highlighted_matches = []

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

    def set_new_images(self, img1, img2):
        self._matches = []
        self._highlighted_matches = []

        self._painter = FeaturePainter(img1, img2)
        background_image = self._painter.background_image()
        self._display_image(background_image)

    def display_matches(self, matches):
        self._matches = matches
        self._update_image()

    def display_highlights(self, highlights):
        self._highlighted_matches = highlights
        self._update_image()

    def _update_image(self):
        image = self._painter.draw_matches(self._matches, self._highlighted_matches)
        self._display_image(image)

    def _display_image(self, image):
        pixmap = image.to_qt_pixmap(self._frame.size())
        self._frame.setPixmap(pixmap)


