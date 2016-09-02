from __future__ import division

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QWidget, QMessageBox

from dls_imagematch.match.align import ImageAligner, ImageAlignmentError


class AutoImageAligner(QWidget):
    """ Used by the GUI main window to perform image alignment.
    """
    signal_aligned = pyqtSignal(object)

    def __init__(self, gui_config, xtal_config):
        super(AutoImageAligner, self).__init__()

        self._gui_config = gui_config
        self._xtal_config = xtal_config
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

        do_align = self._xtal_config.use_alignment.value()
        method = self._xtal_config.align_detector.value()
        config_dir = self._gui_config.config_dir.value()

        aligner = ImageAligner(self._img1, self._img2, config_dir)
        if do_align:
            aligner.set_detector_type(method)

        try:
            aligned_images = aligner.align()
            self.signal_aligned.emit(aligned_images)
        except ImageAlignmentError as ex:
            QMessageBox.critical(self, "Image Alignment Error", str(ex), QMessageBox.Ok)
