from __future__ import division

from PyQt4.QtGui import QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QWidget
from PyQt4.QtCore import Qt, QEvent

from dls_imagematch.match import Overlayer, OverlapMetric


class ImageFrame(QGroupBox):
    """ Widget that displays an image as well as an editable status message and a readout of
    the current mouse position on the image.
    """
    def __init__(self):
        super(ImageFrame, self).__init__()

        self.image = None
        self.scaled_size = (0, 0)
        self.offset = (0, 0)

        self._init_ui()
        self.setTitle("Results")

    def _init_ui(self):
        """ Create all the ui elements of the widget."""
        self.frame = QLabel()
        self.frame.setMouseTracking(True)
        self.frame.installEventFilter(self)
        self.frame.setStyleSheet("border:1px solid black")
        self.frame.setAlignment(Qt.AlignCenter)
        self.frame.setFixedWidth(900)
        self.frame.setFixedHeight(600)

        # Image frame status and cursor position labels
        self.lbl_status1 = QLabel("")
        self.lbl_status2 = QLabel("")
        self.lbl_cursor = QLabel()

        # Widget layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.lbl_status2)
        hbox.addStretch(1)
        hbox.addWidget(self.lbl_cursor)

        vbox = QVBoxLayout()
        vbox.addWidget(self.lbl_status1)
        vbox.addLayout(hbox)
        vbox.addWidget(self.frame)

        self.setLayout(vbox)

    def clear(self):
        """ Reset the frame, clearing the image and status text. """
        self.image = None
        self.scaled_size = (0, 0)
        self.offset = (0, 0)
        self.set_status_message("")
        self.lbl_cursor.setText("")
        self.frame.clear()

    def display_match_results(self, img_a, img_b, transform, message):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        # Create image of B overlaid on A
        img = Overlayer.create_overlay_image(img_a, img_b, transform)
        self.display_image(img)

        # Calculate metric value
        metric_calc = OverlapMetric(img_a, img_b, None)
        metric = metric_calc.calculate_overlap_metric((int(transform.x), int(transform.y)))

        # Determine transformation in real units (um)
        x, y = int(transform.x), int(transform.y)
        pixel_size = img_a.pixel_size
        x_um, y_um = int(x * pixel_size), int(y * pixel_size)
        offset_msg = "x={} um, y={} um ({} px, {} px)".format(x_um, y_um, x, y)

        status = message + " (metric = " + "{0:.2f}".format(metric) + ")"
        self.set_status_message(status, offset_msg)

    def set_status_message(self, line1, line2=""):
        """ Set the text to be displayed in the status message area (2 lines). """
        self.lbl_status1.setText(line1)
        self.lbl_status2.setText(line2)

    def display_image(self, image):
        """ Display the specified Image object in the frame, scaled to fit the frame and maintain aspect ratio. """
        self.image = image
        frame_size = self.frame.size()

        # Convert to a QT pixmap and display
        pixmap = image.to_qt_pixmap()
        scaled = pixmap.scaled(frame_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.frame.setPixmap(scaled)

        # Calculate the offset which is used to correctly report the mouse position on the image
        self.scaled_size = (scaled.width(), scaled.height())
        x_off = int((frame_size.width() - self.scaled_size[0]) / 2)
        y_off = int((frame_size.height() - self.scaled_size[1]) / 2)
        self.offset = (x_off, y_off)

    def eventFilter(self, source, event):
        """ Catches events on the image frame and re-directs mouse movements to the reporting function. """
        if event.type() == QEvent.MouseMove and source is self.frame:
            self.mouseMoveEvent(event)
            return False

        return QWidget.eventFilter(self, source, event)

    def mouseMoveEvent(self, mouse_event):
        """ Called when the mouse moves across the image frame. Displays the current position of the mouse
        in image pixels (scaled to the original image size, not the displayed size). """
        if self.image is not None:
            coords = mouse_event.pos()
            x = coords.x() - self.offset[0]
            y = coords.y() - self.offset[1]

            x_perc = x / self.scaled_size[0]
            y_perc = y / self.scaled_size[1]

            real_size = self.image.size

            real_x_pixels = int(real_size[0] * x_perc)
            real_y_pixels = int(real_size[1] * y_perc)
            real_x_um = real_x_pixels * self.image.pixel_size
            real_y_um = real_y_pixels * self.image.pixel_size

            if 0 <= real_x_pixels <= real_size[0] and 0 <= real_y_pixels <= real_size[1]:
                position_txt = str(real_x_pixels) + " px, " + str(real_y_pixels) + " px (" + \
                    "{0:.2f}".format(real_x_um) + " um, " + "{0:.2f}".format(real_y_um) + " um)"
            else:
                position_txt = ""

            self.lbl_cursor.setText(position_txt)