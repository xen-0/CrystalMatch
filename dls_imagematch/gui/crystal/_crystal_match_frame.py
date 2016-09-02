from __future__ import division

from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox

from feature.draw import MatchPainter


class CrystalMatchFrame(QWidget):

    def __init__(self):
        super(CrystalMatchFrame, self).__init__()

        self._frame = None

        self._painter = None
        self._matches = []
        self._highlighted_matches = []
        self._img1_point = None
        self._img2_point = None
        self._quad1 = None
        self._quad2 = None

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

    def clear(self):
        self._painter = None
        self._matches = []
        self._highlighted_matches = []
        self._img1_point = None
        self._img2_point = None
        self._quad1 = None
        self._quad2 = None

    def set_new_images(self, img1, img2):
        self.clear()

        self._painter = MatchPainter(img1, img2)
        background_image = self._painter.background_image()
        self._display_image(background_image)

    def display_points(self, img1_point, img2_point):
        self._img1_point = img1_point
        self._img2_point = img2_point
        self._update_image()

    def display_transformed_square(self, quad1, quad2):
        self._quad1 = quad1
        self._quad2 = quad2
        self._update_image()

    def display_matches(self, matches):
        self._matches = matches
        self._update_image()

    def display_highlights(self, highlights):
        self._highlighted_matches = highlights
        self._update_image()

    def _update_image(self):
        if self._painter is None:
            return

        image = self._painter.background_image()

        image = self._painter.draw_transform_shapes(self._quad1, self._quad2, image)
        image = self._painter.draw_matches(self._matches, self._highlighted_matches, image)
        image = self._painter.draw_transform_points(self._img1_point, self._img2_point, image)

        self._display_image(image)

    def _display_image(self, image):
        pixmap = image.to_qt_pixmap(self._frame.size())
        self._frame.setPixmap(pixmap)


