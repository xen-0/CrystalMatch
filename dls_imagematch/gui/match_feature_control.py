from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QMessageBox, QComboBox

from dls_imagematch.match import FeatureMatcher, FeatureDetector, AlignedImages
from dls_imagematch.match import FeatureMatchException


class FeatureMatchControl(QGroupBox):
    """ Widget that allows control of the Feature Matching process.
    """
    signal_aligned = QtCore.pyqtSignal(object)

    def __init__(self, selector_a, selector_b):
        super(FeatureMatchControl, self).__init__()

        self._selector_a = selector_a
        self._selector_b = selector_b
        self._matcher = None

        self.last_images = None

        self._init_ui()
        self.setTitle("Image Alignment (Feature Matching)")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Feature Detector method
        self._cmbo_method = QComboBox()
        self._cmbo_method.addItems(FeatureDetector.types())

        self._cmbo_adapt = QComboBox()
        self._cmbo_adapt.addItems(FeatureDetector.adaptations())

        # Matching function buttons
        self._btn_begin = QPushButton("Align Images")
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
        img1, img2 = self._prepare_images()

        method = self._cmbo_method.currentText()
        adapt = self._cmbo_adapt.currentText()

        self._matcher = FeatureMatcher(img1, img2)
        self._matcher.set_detector(method, adapt)
        try:
            match_result = self._matcher.match_translation_only()
        except FeatureMatchException as e:
            QMessageBox.critical(self, "Feature Matching Error", e.message, QMessageBox.Ok)

        self._display_results(match_result)
        self.signal_aligned.emit(self.last_images)

    def _prepare_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Get the selected images
        self._img1 = self._selector_a.image()
        self._img2 = self._selector_b.image()

        # Resize image B so it has the same size per pixel as image A
        factor = self._img2.pixel_size / self._img1.pixel_size
        self._img2 = self._img2.rescale(factor)

        return self._img1.to_mono(), self._img2.to_mono()

    def _display_results(self, match_result):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        align_method = "Feature matching - " + match_result.method
        if match_result.method_adapt != '':
            align_method += " with " + match_result.method_adapt

        translation = match_result.transform.translation()
        aligned = AlignedImages(self._img1, self._img2, translation, align_method)

        self.last_images = aligned
