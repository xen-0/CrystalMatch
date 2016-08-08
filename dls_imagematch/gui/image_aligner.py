from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QMessageBox, QComboBox

from dls_imagematch.match.feature import FeatureDetector
from dls_imagematch.match.align import ImageAligner, ImageAlignmentError


class ImageAlignControl(QGroupBox):
    """ Widget that allows control of the Image Alignment process.
    """
    signal_aligned = QtCore.pyqtSignal(object)

    def __init__(self, selector_a, selector_b):
        super(ImageAlignControl, self).__init__()

        self._selector_a = selector_a
        self._selector_b = selector_b

        self._init_ui()
        self.setTitle("Image Alignment (Feature Matching)")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Feature Detector method
        self._cmbo_method = QComboBox()
        self._cmbo_method.addItems(FeatureDetector.DETECTOR_TYPES)

        self._cmbo_adapt = QComboBox()
        self._cmbo_adapt.addItems(FeatureDetector.ADAPTATION_TYPES)

        # Matching function buttons
        btn_begin = QPushButton("Align Images")
        btn_begin.clicked.connect(self._perform_feature_matching)

        # Create widget layout
        hbox = QHBoxLayout()
        hbox.addWidget(self._cmbo_method)
        hbox.addWidget(self._cmbo_adapt)
        hbox.addWidget(btn_begin)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def _perform_feature_matching(self):
        """ Begin the feature matching process for the two selected images. """
        img1 = self._selector_a.image()
        img2 = self._selector_b.image()

        method = self._cmbo_method.currentText()
        adapt = self._cmbo_adapt.currentText()

        aligner = ImageAligner(img1, img2)
        aligner.set_detector_type(method)
        aligner.set_adaptation_type(adapt)

        try:
            aligned_images = aligner.align()
            self.signal_aligned.emit(aligned_images)
        except ImageAlignmentError as ex:
            QMessageBox.critical(self, "Image Alignment Error", str(ex), QMessageBox.Ok)
