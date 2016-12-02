from PyQt4.QtCore import Qt, QSize, QRect, QPoint
from PyQt4.QtGui import QGroupBox, QGraphicsView, QVBoxLayout, QGraphicsScene, QPixmap
from PyQt4.QtOpenGL import QGLWidget


class MagnifyingImageView(QGroupBox):
    VIEWER_SIZE = 600

    def __init__(self, title):
        super(MagnifyingImageView, self).__init__()
        self.setTitle(title)
        self._init_ui()

    def _init_ui(self):
        self._image_view = MagnifyingGraphicsView(self.VIEWER_SIZE)
        self._image_view.setFixedWidth(self.VIEWER_SIZE)
        self._image_view.setFixedHeight(self.VIEWER_SIZE)
        self._image_view.setAlignment(Qt.AlignCenter)
        self._image_view.setViewport(QGLWidget())

        vbox = QVBoxLayout()
        vbox.addWidget(self._image_view)

        self.setLayout(vbox)

    def set_image(self, img, scale_factor=1):
        self._image_view.set_image(img, scale_factor)


class MagnifyingGraphicsView(QGraphicsView):
    MIN_DRAG_LENGTH = 10
    MAX_SCALE_FACTOR = 7.5  # DEV NOTE: past 7.5 scale the image view goes entirely black - out of memory?

    def __init__(self, viewer_size, parent=None):
        super(MagnifyingGraphicsView, self).__init__(parent)
        self._mouse_drag_event = False
        self._mouse_down_location = None
        self._original_pixmap = None
        self._viewer_size = viewer_size
        self._scale_factor = 1

    def mouseMoveEvent(self, event):
        QGraphicsView.mouseMoveEvent(self, event)
        self._mouse_drag_event = True

    def mousePressEvent(self, event):
        QGraphicsView.mousePressEvent(self, event)
        self._mouse_drag_event = False
        self._mouse_down_location = event.pos()

    def mouseReleaseEvent(self, event):
        QGraphicsView.mouseReleaseEvent(self, event)
        if self._original_pixmap is None:
            return
        rect = self._get_q_rect(event.pos(), self._mouse_down_location)
        drag_length = rect.height() + rect.width()
        QGraphicsView.mouseReleaseEvent(self, event)
        if self._mouse_drag_event and drag_length > self.MIN_DRAG_LENGTH:
            self._toggle_zoom_on_rect(rect)
        else:
            print "Click"

    def _toggle_zoom_on_rect(self, q_rect):
        if self._scale_factor != 1.0:
            self._scale_factor = 1.0
            self._rescale_pixmap()
            return
        w = q_rect.width() if q_rect.width() != 0 else 1
        h = q_rect.height() if q_rect.height() != 0 else 1
        w_scale = float(self._viewer_size) / float(w)
        h_scale = float(self._viewer_size) / float(h)
        self._scale_factor = min(w_scale, h_scale)

        # Calculate Relative centre
        offset_w = float(self._viewer_size - self.items()[0].pixmap().width()) / 2.0
        offset_h = float(self._viewer_size - self.items()[0].pixmap().height()) / 2.0
        x = ((float(q_rect.center().x()) - offset_w) / float(self._viewer_size))
        y = ((float(q_rect.center().y()) - offset_h) / float(self._viewer_size))
        relative_centre_point = (x, y)

        self._rescale_pixmap(relative_centre=relative_centre_point)

    def set_image(self, img, scale_factor=1):
        self._scale_factor = scale_factor
        self._original_pixmap = QPixmap(img)
        self._rescale_pixmap()

    def _rescale_pixmap(self, relative_centre=None):
        if self._scale_factor > self.MAX_SCALE_FACTOR:
            print "Warning: Max scale factor is " + str(self.MAX_SCALE_FACTOR)
            self._scale_factor = self.MAX_SCALE_FACTOR

        scale = QSize(self._scale_factor * self._viewer_size, self._scale_factor * self._viewer_size)
        pixmap = self._original_pixmap.scaled(scale, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        new_scene = QGraphicsScene()
        new_scene.addPixmap(pixmap)
        self.setScene(new_scene)

        if relative_centre is not None:
            calc_centre = QPoint(scale.width() * relative_centre[0], scale.height() * relative_centre[1])

            self.centerOn(calc_centre)

    @staticmethod
    def _get_q_rect(pos_1, pos_2):
        x = min(pos_1.x(), pos_2.x())
        y = min(pos_1.y(), pos_2.y())
        w = max(pos_1.x(), pos_2.x()) - min(pos_1.x(), pos_2.x())
        h = max(pos_1.y(), pos_2.y()) - min(pos_1.y(), pos_2.y())
        return QRect(x, y, w, h)
