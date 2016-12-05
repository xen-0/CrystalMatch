from PyQt4.QtCore import Qt, QRectF
from PyQt4.QtGui import QGroupBox, QGraphicsView, QVBoxLayout, QGraphicsScene, QPixmap, QPen, QColor, QApplication
from PyQt4.QtOpenGL import QGLWidget

from dls_util.shape.point import Point


class MagnifyingImageView(QGroupBox):
    VIEWER_SIZE = 800

    def __init__(self, title):
        super(MagnifyingImageView, self).__init__()
        self.setTitle(title)
        self._init_ui()

    def _init_ui(self):
        self._image_view = MagnifyingGraphicsView()
        self._image_view.setFixedWidth(self.VIEWER_SIZE)
        self._image_view.setFixedHeight(self.VIEWER_SIZE)
        self._image_view.setAlignment(Qt.AlignCenter)
        self._image_view.setViewport(QGLWidget())

        vbox = QVBoxLayout()
        vbox.addWidget(self._image_view)

        self.setLayout(vbox)

    def set_image(self, img):
        self._image_view.set_image(img)

    def update_points_data(self, points_data):
        self._image_view.update_points_data(points_data)

    def select_point(self, point):
        self._image_view.select_point(point.x, point.y)

    def get_selected_point(self):
        s_point = self._image_view.selected_point
        return None if s_point is None else Point(s_point[0], s_point[1])


class MagnifyingGraphicsView(QGraphicsView):
    POI_MARKER_SIZE_RELATIVE = 0.005  # Sets the POI markers based on the width of the pixmap
    SCALE_STEP_SIZE = 1.5

    def __init__(self, parent=None):
        super(MagnifyingGraphicsView, self).__init__(parent)
        self._pixmap = None
        self._points_data = None
        self._scene = None
        self.selected_point = None

    def _reset_zoom(self):
        self.fitInView(QRectF(self._pixmap.rect()))

    def mouseReleaseEvent(self, event):
        QGraphicsView.mouseReleaseEvent(self, event)
        if self._pixmap is None:
            return

        # noinspection PyArgumentList
        modifiers = QApplication.keyboardModifiers()
        scene_pos = self.mapToScene(event.pos())
        if event.button() == Qt.RightButton:
            if modifiers == Qt.ShiftModifier:
                self._zoom_out()
            elif modifiers == Qt.ControlModifier:
                self._reset_zoom()
            else:
                self._zoom_in(centre_point=scene_pos)
        elif event.button() == Qt.LeftButton:
            self.select_point(scene_pos.x(), scene_pos.y())

    def select_point(self, x, y):
        self.selected_point = (x, y)
        self._redraw()
        self._draw_point(x, y, colour=QColor("#00FF00"))

    def _redraw(self):
        self._new_scene_from_pixmap(self._pixmap)
        self._draw_points_data()

    def update_points_data(self, points_data):
        self._points_data = points_data
        self._redraw()

    def _draw_points_data(self):
        if self._points_data is not None:
            for p in self._points_data:
                if p is not None:
                    self._draw_point(p.x, p.y)

    # noinspection PyArgumentList
    def _draw_point(self, x, y, colour=QColor("red")):
        pen = QPen(colour)
        offset = self.POI_MARKER_SIZE_RELATIVE * self._pixmap.width()
        self._scene.addLine(x - offset, y - offset, x + offset, y + offset, pen=pen)
        self._scene.addLine(x + offset, y - offset, x - offset, y + offset, pen=pen)

    def set_image(self, img):
        self._points_data = None
        self._pixmap = QPixmap(img)
        self._new_scene_from_pixmap(self._pixmap, reset_zoom=True)

    def _new_scene_from_pixmap(self, pixmap, reset_zoom=False):
        self._scene = QGraphicsScene()
        self._scene.addPixmap(pixmap)
        self.setScene(self._scene)
        if reset_zoom:
            self._reset_zoom()

    def _zoom_in(self, scale_factor=None, centre_point=None):
        self._zoom(True, centre_point, scale_factor)

    def _zoom_out(self, scale_factor=None, centre_point=None):
        self._zoom(False, centre_point, scale_factor)

    def _zoom(self, zoom_in, centre_point, scale_factor):
        if scale_factor is None:
            scale_factor = self.SCALE_STEP_SIZE
        if zoom_in:
            self.setTransform(self.transform().scale(scale_factor, scale_factor))
        else:
            self.setTransform(self.transform().scale(1/float(scale_factor), 1/float(scale_factor)))

        if centre_point is not None:
            self.centerOn(centre_point)
