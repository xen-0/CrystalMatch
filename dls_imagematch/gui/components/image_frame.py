from __future__ import division

from PyQt4.QtGui import QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QWidget
from PyQt4.QtCore import Qt, QEvent

from dls_imagematch.crystal import AlignedImages


class ImageFrame(QGroupBox):
    """ Widget that displays an image as well as an editable status message and a readout of
    the current mouse position on the image.
    """
    def __init__(self, gui_config):
        super(ImageFrame, self).__init__()

        self._gui_config = gui_config

        self._image = None
        self._scaled_size = (0, 0)
        self._mouse_display_offset = (0, 0)

        self.last_images = None

        self._init_ui()
        self.setTitle("Results")

    def _init_ui(self):
        """ Create all the ui elements of the widget."""
        self._frame = self._ui_make_image_frame()

        # Image frame status and cursor position labels
        self._lbl_status1 = QLabel("")
        self._lbl_status2 = QLabel("")
        self._lbl_cursor = QLabel()

        # Widget layout
        hbox = QHBoxLayout()
        hbox.addWidget(self._lbl_status2)
        hbox.addStretch(1)
        hbox.addWidget(self._lbl_cursor)

        vbox = QVBoxLayout()
        vbox.addWidget(self._lbl_status1)
        vbox.addLayout(hbox)
        vbox.addWidget(self._frame)

        self.setLayout(vbox)

    def _ui_make_image_frame(self):
        frame = QLabel()
        frame.setMouseTracking(True)
        frame.installEventFilter(self)
        frame.setStyleSheet("border:1px solid black")
        frame.setAlignment(Qt.AlignCenter)
        frame.setFixedWidth(900)
        frame.setFixedHeight(600)
        return frame

    def clear(self):
        """ Reset the frame, clearing the image and status text. """
        self._image = None
        self._scaled_size = (0, 0)
        self._mouse_display_offset = (0, 0)
        self.set_status_message("")
        self._lbl_cursor.setText("")
        self._frame.clear()

    def set_status_message(self, line1, line2=""):
        """ Set the text to be displayed in the status message area (2 lines). """
        self._lbl_status1.setText(line1)
        self._lbl_status2.setText(line2)

    def display_image(self, image):
        """ Display the specified Image object in the frame, scaled to fit the frame and maintain aspect ratio. """
        self._image = image
        pixmap = image.to_qt_pixmap(self._frame.size())
        self._frame.setPixmap(pixmap)

        self._scaled_size = (pixmap.width(), pixmap.height())
        self._set_mouse_display_offset()

    def display_align_results(self, aligned_images):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        if not isinstance(aligned_images, AlignedImages):
            raise TypeError("Argument must be instance of {}".format(AlignedImages.__name__))

        self.last_images = aligned_images

        # Display image of B overlaid on A
        rect_color = self._gui_config.color_align.value()
        self.display_image(aligned_images.overlay(rect_color))
        self._set_align_status_message(aligned_images)

    def _set_align_status_message(self, aligned_images):
        metric = aligned_images.overlap_metric()

        # Determine transformation in real units (um)
        pixel = aligned_images.pixel_offset()
        real = aligned_images.real_offset()
        offset_msg = "x={0:.2f} um, y={1:.2f} um ({2} px, {3} px)".format(real.x, real.y, pixel.x, pixel.y)
        status = "Image Alignment (" + aligned_images.method + ") (metric = " + "{0:.2f}".format(metric) + ")"
        self.set_status_message(status, offset_msg)

    def _set_mouse_display_offset(self):
        frame_size = self._frame.size()
        scaled_size = self._scaled_size

        x_off = int((frame_size.width() - scaled_size[0]) / 2)
        y_off = int((frame_size.height() - scaled_size[1]) / 2)
        self._mouse_display_offset = (x_off, y_off)

    def eventFilter(self, source, event):
        """ Catches events on the image frame and re-directs mouse movements to the reporting function. """
        if event.type() == QEvent.MouseMove and source is self._frame:
            self.mouseMoveEvent(event)
            return False

        return QWidget.eventFilter(self, source, event)

    def mouseMoveEvent(self, mouse_event):
        """ Called when the mouse moves across the image frame. Displays the current position of the mouse
        in image pixels (scaled to the original image size, not the displayed size). """
        if self._image is not None:
            coords = mouse_event.pos()
            x = coords.x() - self._mouse_display_offset[0]
            y = coords.y() - self._mouse_display_offset[1]

            x_perc = x / self._scaled_size[0]
            y_perc = y / self._scaled_size[1]

            real_size = self._image.size

            real_x_pixels = int(real_size[0] * x_perc)
            real_y_pixels = int(real_size[1] * y_perc)
            real_x_um = real_x_pixels * self._image.pixel_size
            real_y_um = real_y_pixels * self._image.pixel_size

            if 0 <= real_x_pixels <= real_size[0] and 0 <= real_y_pixels <= real_size[1]:
                position_txt = "{:.2f} um, {:.2f} um ({} px, " \
                               "{} px)".format(real_x_um, real_y_um, real_x_pixels, real_y_pixels)
            else:
                position_txt = ""

            self._lbl_cursor.setText(position_txt)
