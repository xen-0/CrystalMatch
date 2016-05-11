from __future__ import division

from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QMessageBox, QComboBox, QLabel

from dls_imagematch.match import FeatureMatcher, Overlayer, OverlapMetric
from dls_imagematch.match import FeatureMatchException


class FeatureMatchControl(QGroupBox):
    """ Widget that allows control of the Feature Matching process.
    """
    def __init__(self, selector_a, selector_b, image_frame):
        super(FeatureMatchControl, self).__init__()

        self._selector_a = selector_a
        self._selector_b = selector_b
        self._image_frame = image_frame
        self._matcher = None

        self._init_ui()
        self.setTitle("Feature Matching")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Feature Detector method
        self._cmbo_method = QComboBox()
        self._cmbo_method.addItems(FeatureMatcher.DETECTOR_TYPES)

        self._cmbo_adapt = QComboBox()
        self._cmbo_adapt.addItems(FeatureMatcher.ADAPTATION_TYPE)

        # Matching function buttons
        self._btn_begin = QPushButton("Begin Match")
        self._btn_begin.clicked.connect(self._fn_begin_matching)

        # Create widget layout
        hbox = QHBoxLayout()
        hbox.addWidget(self._cmbo_method)
        hbox.addWidget(self._cmbo_adapt)
        hbox.addWidget(self._btn_begin)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def match(self):
        self._fn_begin_matching()

    def _fn_begin_matching(self):
        """ Begin the feature matching process for the two selected images. """
        img_a, img_b = self._prepare_images()

        method = self._cmbo_method.currentText()
        adapt = self._cmbo_adapt.currentText()

        self._matcher = FeatureMatcher(img_a, img_b)
        try:
            self._matcher.match(method, adapt)
            self._display_results(method)
        except FeatureMatchException as e:
            QMessageBox.critical(self, "Feature Matching Error", e.message, QMessageBox.Ok)

    def _prepare_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Get the selected images
        self.img_a = self._selector_a.image()
        self.img_b = self._selector_b.image()

        # Resize the image B so it has the same size per pixel as image A
        factor = self.img_b.pixel_size / self.img_a.pixel_size
        self.img_b = self.img_b.rescale(factor)

        return self.img_a.make_gray(), self.img_b.make_gray()

    def _display_results(self, method):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        transform = self._matcher.net_transform

        # Create image of B overlaid on A
        img = Overlayer.create_overlay_image(self.img_a, self.img_b, transform)
        self._image_frame.display_image(img)

        # Calculate metric value
        metric_calc = OverlapMetric(self.img_a, self.img_b, None)
        metric = metric_calc.calculate_overlap_metric((int(transform.x), int(transform.y)))

        # Determine current transformation in real units (um)
        x, y = int(transform.x), int(transform.y)
        pixel_size = self.img_a.pixel_size
        x_um, y_um = int(x * pixel_size), int(y * pixel_size)
        offset_msg = "x={} um, y={} um ({} px, {} px)".format(x_um,y_um,x,y)

        status = "Feature match complete (" + method + ") - (metric = " + "{0:.2f}".format(metric) + ")"
        self._image_frame.set_status_message(status, offset_msg)