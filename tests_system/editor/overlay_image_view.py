from PyQt4.QtCore import QRectF, Qt
from PyQt4.QtGui import QGroupBox, QGraphicsView, QLabel, QVBoxLayout, QGraphicsScene, QPixmap, QGraphicsItem
from PyQt4.QtOpenGL import QGLWidget


class OverlayImageView(QGroupBox):
    """
    Takes two images, sets the first image as an overlay and the second as the background.  The user can adjust
    the image alignment using the mouse and the offset can be returned.
    """
    def __init__(self, title):
        super(OverlayImageView, self).__init__()
        self.setTitle(title)
        self._init_ui()

    def _init_ui(self):
        self._image_view = _OverlayGraphicsView()
        self._image_view.setAlignment(Qt.AlignCenter)
        self._image_view.setViewport(QGLWidget())

        self._zoom_instructions = QLabel("Zoom on area: Right-click + drag\nReset Zoom: Right-click")

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

    def set_overlay_pos(self, x, y):
        print x
        print y
        self._image_view.set_overlay_pos(x, y)

    def update_overlay_pos(self, mod_x, mod_y):
        """
        Modify the position of the overlay.
        :param mod_x: The modifier added to the x position
        :param mod_y: The modifier added to the y position
        """
        self._image_view.update_overlay_pos(mod_x, mod_y)

    def get_overlay_pos(self):
        return self._image_view.get_overlay_pos()


class _OverlayGraphicsView(QGraphicsView):
    """
    Takes two images, sets the first image as an overlay and the second as the background.  The user can adjust
    the image alignment using the mouse and the offset can be returned.
    """
    DRAG_ZOOM_MIN_SIZE = 10  # Sets the threshold for turning a click into drag-zoom - relative to viewer-size

    def __init__(self):
        super(_OverlayGraphicsView, self).__init__()
        self._background = None
        self._overlay = None
        self._mouse_down_pos = None

    def overlay_images(self, img_1, img_2):
        pixmap_1 = QPixmap(img_1)
        pixmap_2 = QPixmap(img_2)

        new_scene = QGraphicsScene()
        new_scene.addPixmap(pixmap_2)
        self._background = new_scene.items()[0]
        new_scene.addPixmap(pixmap_1)
        self._overlay = new_scene.items()[0]
        self._overlay.setFlag(QGraphicsItem.ItemIsMovable)
        self.set_opacity(0.5)

        self.setScene(new_scene)

        # Put entire image in view
        self._reset_zoom()

    def get_overlay_pos(self):
        return self._overlay.pos().x(), self._overlay.pos().y()

    def set_opacity(self, opacity):
        self._overlay.setOpacity(opacity)

    def set_overlay_pos(self, x, y):
        self._overlay.setPos(x, y)

    def update_overlay_pos(self, mod_x, mod_y):
        pos = self._overlay.pos()
        self._overlay.setPos(pos.x() + mod_x, pos.y() + mod_y)

    def mousePressEvent(self, event):
        QGraphicsView.mousePressEvent(self, event)
        if event.button() == Qt.RightButton:
            self._mouse_down_pos = event.pos()

    def mouseReleaseEvent(self, event):
        QGraphicsView.mouseReleaseEvent(self, event)
        # Check for drag zoom on the right mouse button
        if self._mouse_down_pos is not None and event.button() == Qt.RightButton:
            if self._is_drag_zoom_operation(self._mouse_down_pos, event.pos()):
                self._zoom_to_area(self._mouse_down_pos, event.pos())
            else:
                self._reset_zoom()
            self._mouse_down_pos = None

    def _reset_zoom(self):
        zoom_rect = QRectF(self._overlay.sceneBoundingRect().united(self._background.sceneBoundingRect()))
        self.fitInView(zoom_rect, Qt.KeepAspectRatio)

    def _is_drag_zoom_operation(self, pos_1, pos_2):
        if pos_1 is None or pos_2 is None:
            return False
        drag_vector = pos_1 - pos_2
        return drag_vector.manhattanLength() > self.DRAG_ZOOM_MIN_SIZE

    def _zoom_to_area(self, pos_1, pos_2):
        zoom_area = self._get_q_rect(self.mapToScene(pos_1), self.mapToScene(pos_2))
        self.fitInView(zoom_area, Qt.KeepAspectRatio)

    @staticmethod
    def _get_q_rect(pos_1, pos_2):
        x = min(pos_1.x(), pos_2.x())
        y = min(pos_1.y(), pos_2.y())
        w = max(pos_1.x(), pos_2.x()) - min(pos_1.x(), pos_2.x())
        h = max(pos_1.y(), pos_2.y()) - min(pos_1.y(), pos_2.y())
        return QRectF(x, y, w, h)
