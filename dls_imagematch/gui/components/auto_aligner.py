from __future__ import division

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QWidget, QMessageBox

from dls_imagematch.match.align import ImageAligner, ImageAlignmentError
from feature.detector import DetectorConfig


class AutoImageAligner(QWidget):
    """ Used by the GUI main window to perform image alignment.
    """
    signal_aligned = pyqtSignal(object)

    def __init__(self, gui_config, align_config):
        super(AutoImageAligner, self).__init__()

        self._gui_config = gui_config
        self._align_config = align_config
        self._img1 = None
        self._img2 = None

    def set_images(self, image1, image2):
        self._img1 = image1
        self._img2 = image2
        self._perform_alignment()

    def set_image_1(self, image):
        self._img1 = image
        self._perform_alignment()

    def set_image_2(self, image):
        self._img2 = image
        self._perform_alignment()

    def _perform_alignment(self):
        if self._img1 is None or self._img2 is None:
            return

        detector_config_dir = self._gui_config.config_dir.value()
        detector_config = DetectorConfig(detector_config_dir)

        aligner = ImageAligner(self._img1, self._img2, self._align_config, detector_config)

        try:
            aligned_images = aligner.align()
            self.signal_aligned.emit(aligned_images)

            if aligned_images.is_alignment_poor():
                QMessageBox.warning(self, "Image Alignment Warning", "The quality of the image alignment "
                                                                     "was poor", QMessageBox.Ok)
            elif aligned_images.is_alignment_bad():
                QMessageBox.critical(self, "Image Alignment Error", "Alignment failed due to very bad "
                                                                    "fit.", QMessageBox.Ok)

        except ImageAlignmentError as ex:
            QMessageBox.critical(self, "Image Alignment Error", str(ex), QMessageBox.Ok)
