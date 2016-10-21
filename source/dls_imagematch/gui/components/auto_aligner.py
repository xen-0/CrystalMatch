from __future__ import division

from PyQt4.QtCore import pyqtSignal, QThread
from PyQt4.QtGui import QWidget, QMessageBox

from dls_imagematch.feature.detector.config import DetectorConfig
from .progress_dialog import ProgressDialog
from dls_imagematch.crystal.align import ImageAligner, ImageAlignmentError


class AutoImageAligner(QWidget):
    """ Used by the GUI main window to perform image alignment.
    """
    signal_aligned = pyqtSignal(object)

    def __init__(self, gui_config, align_config):
        super(AutoImageAligner, self).__init__()

        self._gui_config = gui_config
        self._align_config = align_config
        self._image1 = None
        self._image2 = None

    def set_images(self, image1, image2):
        self._image1 = image1
        self._image2 = image2
        self._perform_alignment()

    def set_image_1(self, image):
        self._image1 = image
        self._perform_alignment()

    def set_image_2(self, image):
        self._image2 = image
        self._perform_alignment()

    def _perform_alignment(self):
        if self._image1 is None or self._image2 is None:
            return

        aligner = self._create_aligner()

        # Run the alignment in a separate thread and display a blocking progress dialog
        progress = ProgressDialog("Image Alignment In Progress")
        align_task = _AlignTaskThread(aligner)
        align_task.task_finished.connect(progress.on_finished)
        align_task.task_results.connect(self._emit_align_results)
        align_task.task_failed.connect(self._display_failure_message)
        align_task.start()
        progress.exec_()

    def _create_aligner(self):
        detector_config = self._get_detector_config()
        aligner = ImageAligner(self._image1, self._image2, self._align_config, detector_config)
        return aligner

    def _get_detector_config(self):
        detector_config_dir = self._gui_config.config_dir.value()
        detector_config = DetectorConfig(detector_config_dir)
        return detector_config

    def _emit_align_results(self, aligned_images):
        self.signal_aligned.emit(aligned_images)

        if aligned_images.is_alignment_poor():
            QMessageBox().warning(self, "Image Alignment Warning", "The quality of the image alignment "
                                                                   "was poor", QMessageBox.Ok)
        elif aligned_images.is_alignment_bad():
            QMessageBox().critical(self, "Image Alignment Error", "Alignment failed due to very bad "
                                                                  "fit.", QMessageBox.Ok)

    def _display_failure_message(self, message):
        QMessageBox().critical(self, "Image Alignment Error", message, QMessageBox.Ok)


class _AlignTaskThread(QThread):
    task_finished = pyqtSignal()
    task_results = pyqtSignal(object)
    task_failed = pyqtSignal(str)

    def __init__(self, aligner):
        super(_AlignTaskThread, self).__init__()
        self._aligner = aligner

    def run(self):
        try:
            aligned_images = self._aligner.align()

            self.task_finished.emit()
            self.task_results.emit(aligned_images)

        except ImageAlignmentError as ex:
            self.task_failed.emit(str(ex))
