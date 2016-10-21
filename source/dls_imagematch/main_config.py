import sys

from os.path import dirname
from sys import path

from PyQt4.QtGui import QMainWindow, QIcon
from PyQt4.QtGui.QAction import QAction
from PyQt4.QtGui.QApplication import QApplication

from dls_util.config import ConfigDialog
from dls_imagematch.crystal import CrystalMatchConfig, AlignConfig
from dls_imagematch.feature.detector import DetectorConfig, DetectorType

path.append(dirname(path[0]))

# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
if IS_BUNDLED:
    CONFIG_DIR = "./config/"
else:
    CONFIG_DIR = "../config/"


class CrystalMatchConfigWindow(QMainWindow):
    """ Small GUI utility to allow configuration options for the Crystal image matching application to be set.
    """
    def __init__(self, config_dir):
        super(CrystalMatchConfigWindow, self).__init__()

        self._crystal_config = CrystalMatchConfig(config_dir)
        self._align_config = AlignConfig(config_dir)
        self._detector_config = DetectorConfig(config_dir)
        self._license_config = self._detector_config.get_licensing_options()

        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle('Crystal Matching Configuration')

        self.init_menu_bar()
        self.show()

    def init_menu_bar(self):
        """Create and populate the menu bar. """
        # Exit Application
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QApplication.quit)

        # Open options dialog
        crystal_opt = self._init_options_menu_item("Crystal Matching", self._crystal_config)
        align_opt = self._init_options_menu_item("Image Alignment", self._align_config)
        license_opt = self._init_options_menu_item("Detector Licensing", self._license_config)

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

        option_menu = menu_bar.addMenu('&Configuration')
        option_menu.addAction(align_opt)
        option_menu.addAction(crystal_opt)
        option_menu.addAction(license_opt)

        detector_menu = menu_bar.addMenu('&Detectors')
        for det_type in DetectorType.LIST_ALL:
            detector_menu.addAction(self._init_detector_menu(det_type))

    def _init_options_menu_item(self, name, config):
        action = QAction('&{}...'.format(name), self)
        action.setStatusTip('Open {} Options Dialog'.format(name))
        action.triggered.connect(lambda: self._open_config_dialog(config))
        return action

    def _init_detector_menu(self, detector):
        action = QAction(detector + "...", self)
        options = self._detector_config.get_detector_options(detector)
        action.triggered.connect(lambda: self._open_config_dialog(options))
        return action

    @staticmethod
    def _open_config_dialog(config):
        dialog = ConfigDialog(config)
        dialog.auto_layout()
        dialog.exec_()


def main():
    app = QApplication(sys.argv)
    CrystalMatchConfigWindow(CONFIG_DIR)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
