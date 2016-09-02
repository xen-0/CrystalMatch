from PyQt4 import QtGui
from PyQt4.QtGui import (QWidget, QMainWindow, QIcon, QHBoxLayout, QVBoxLayout, QAction)

from dls_imagematch.util.config import ConfigDialog
from feature.detector import DetectorConfig, DetectorType
from match.config import XtalConfig, XtalConfigDialog
from .auto_aligner import AutoImageAligner
from .crystal import CrystalMatchControl
from .image_frame import ImageFrame
from .image_select import ImageSelector
from .well_select_formulatrix import WellSelectorFormulatrix


class VMXiCrystalMatchMainWindow(QMainWindow):
    def __init__(self, config_dir):
        super(VMXiCrystalMatchMainWindow, self).__init__()

        self.gui_state = None
        self.matcher = None
        self._aligner = None

        self._config = XtalConfig(config_dir)

        self.init_ui()

    def init_ui(self):
        """ Create all elements of the user interface. """
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowTitle('Diamond VMXi Image Matching')
        self.setWindowIcon(QIcon('web.png'))

        self.init_menu_bar()

        # Image selectors
        selector1 = ImageSelector("Select Image 1", self._config)
        selector2 = ImageSelector("Select Image 2", self._config)

        # Plate well selector (example data set)
        well_selector = WellSelectorFormulatrix(self._config)

        # Main image frame - shows progress of image matching
        image_frame = ImageFrame(self._config)

        # Automatic Image Aligner
        self._aligner = AutoImageAligner(self._config)

        # Secondary Matching Control
        xtal_match = CrystalMatchControl(image_frame, self._config)

        # Connect signals
        self._aligner.signal_aligned.connect(xtal_match.set_aligned_images)
        self._aligner.signal_aligned.connect(image_frame.display_align_results)

        selector1.signal_selected.connect(self._aligner.set_image_1)
        selector2.signal_selected.connect(self._aligner.set_image_2)

        well_selector.signal_image1_selected.connect(selector1.set_image)
        well_selector.signal_image2_selected.connect(selector2.set_image)

        well_selector.signal_image1_selected.connect(xtal_match.reset)
        well_selector.signal_image1_selected.connect(image_frame.clear)

        # Create layout
        vbox_img_selection = QVBoxLayout()
        vbox_img_selection.addWidget(well_selector)
        vbox_img_selection.addWidget(selector1)
        vbox_img_selection.addWidget(selector2)
        vbox_img_selection.addStretch(1)

        vbox_matching = QVBoxLayout()
        vbox_matching.addWidget(xtal_match)
        vbox_matching.addWidget(image_frame)
        vbox_matching.addStretch(1)

        hbox_main = QHBoxLayout()
        hbox_main.setSpacing(10)
        hbox_main.addLayout(vbox_img_selection)
        hbox_main.addLayout(vbox_matching)
        hbox_main.addStretch(1)

        main_widget = QWidget()
        main_widget.setLayout(hbox_main)
        self.setCentralWidget(main_widget)
        self.show()

        if well_selector.is_sample_dir_valid():
            well_selector._emit_well_selected_signal()

    def init_menu_bar(self):
        """Create and populate the menu bar. """
        # Exit Application
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)

        # Open options dialog
        options_action = QtGui.QAction(QtGui.QIcon('exit.png'), '&Options', self)
        options_action.setShortcut('Ctrl+O')
        options_action.setStatusTip('Open Options Dialog')
        options_action.triggered.connect(self._open_config_dialog)

        detector_menu = QtGui.QMenu('Detectors', self)

        detector_menu.addAction(self._init_detector_menu(DetectorType.ORB))
        detector_menu.addAction(self._init_detector_menu(DetectorType.SURF))
        detector_menu.addAction(self._init_detector_menu(DetectorType.SIFT))
        detector_menu.addAction(self._init_detector_menu(DetectorType.BRISK))
        detector_menu.addAction(self._init_detector_menu("Default"))

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

        option_menu = menu_bar.addMenu('&Option')
        option_menu.addAction(options_action)
        option_menu.addMenu(detector_menu)

    def _init_detector_menu(self, detector):
        action = QtGui.QAction(QtGui.QIcon('exit.png'), detector, self)
        action.triggered.connect(lambda: self._open_detector_config(detector))
        return action

    def _open_config_dialog(self):
        dialog = XtalConfigDialog(self._config)
        dialog.exec_()

    def _open_detector_config(self, detector):
        config_dir = self._config.config_dir.value()
        config = DetectorConfig(config_dir)
        options = config.get_detector_options(detector)

        dialog = ConfigDialog(options)
        dialog.auto_layout()
        dialog.exec_()
