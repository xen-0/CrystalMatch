from __future__ import division

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QWidget, QMessageBox

from dls_imagematch.match.align import ImageAligner, ImageAlignmentError


class AutoImageAligner(QWidget):
    signal_aligned = pyqtSignal(object)

    def __init__(self, config):
        super(AutoImageAligner, self).__init__()

        self._config = config
        self._img1 = None
        self._img2 = None

    def set_image_1(self, image):
        self._img1 = image
        self._perform_alignment()

    def set_image_2(self, image):
        self._img2 = image
        self._perform_alignment()

    def _perform_alignment(self):
        if self._img1 is None or self._img2 is None:
            return

        method = self._config.align_detector.value()
        adapt = self._config.align_adapt.value()

        aligner = ImageAligner(self._img1, self._img2)
        aligner.set_detector_type(method)
        aligner.set_adaptation_type(adapt)

        try:
            aligned_images = aligner.align()
            self.signal_aligned.emit(aligned_images)
        except ImageAlignmentError as ex:
            QMessageBox.critical(self, "Image Alignment Error", str(ex), QMessageBox.Ok)
