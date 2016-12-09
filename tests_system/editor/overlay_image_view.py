from PyQt4.QtCore import Qt, QRectF
from PyQt4.QtGui import QGroupBox, QGraphicsView, QLabel, QVBoxLayout, QGraphicsScene, QPixmap, QGraphicsItem
from PyQt4.QtOpenGL import QGLWidget


class OverlayImageView(QGroupBox):
    def __init__(self, title):
        super(OverlayImageView, self).__init__()
        self.setTitle(title)
        self._init_ui()

    def _init_ui(self):
        self._image_view = _OverlayGraphicsView()
        self._image_view.setAlignment(Qt.AlignCenter)
        self._image_view.setViewport(QGLWidget())

        self._zoom_instructions = QLabel("Write some damn instructions, Chris")

        vbox = QVBoxLayout()
        vbox.addWidget(self._image_view)
        vbox.addWidget(self._zoom_instructions)

        self.setLayout(vbox)

    def overlay_images(self, img_1, img_2):
        self._image_view.overlay_images(img_1, img_2)

    def set_overlay_opacity(self, opacity):
        """
        Updates the opacity of the overlay image.
        :param opacity: float value between 0 and 1
        """
        self._image_view.set_opacity(opacity)

    def update_overlay_pos(self, mod_x, mod_y):
        """
        Modify the position of the overlay.
        :param mod_x: The modifier added to the x position
        :param mod_y: The modifier added to the y position
        """
        self._image_view.update_overlay_pos(mod_x, mod_y)


class _OverlayGraphicsView(QGraphicsView):

    def __init__(self):
        # TODO: add magnification
        # TODO: Add zoom reset
        # TODO: Add label to document controls
        super(_OverlayGraphicsView, self).__init__()
        self._background = None
        self._overlay = None

    def overlay_images(self, img_1, img_2):
        pixmap_1 = QPixmap(img_1)
        pixmap_2 = QPixmap(img_2)

        new_scene = QGraphicsScene()
        new_scene.addPixmap(pixmap_1)
        self._background = new_scene.items()[0]
        new_scene.addPixmap(pixmap_2)
        self._overlay = new_scene.items()[0]
        self._overlay.setFlag(QGraphicsItem.ItemIsMovable)
        self.set_opacity(0.5)

        self.setScene(new_scene)

        # Put entire image in view
        self.fitInView(QRectF(pixmap_1.rect().united(pixmap_2.rect())), Qt.KeepAspectRatio)

    def set_opacity(self, opacity):
        self._overlay.setOpacity(opacity)

    def update_overlay_pos(self, mod_x, mod_y):
        pos = self._overlay.pos()
        self._overlay.setPos(pos.x() + mod_x, pos.y() + mod_y)
