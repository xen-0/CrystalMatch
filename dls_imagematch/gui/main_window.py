from PyQt4 import QtGui
from PyQt4.QtGui import (QWidget, QMainWindow, QIcon, QHBoxLayout, QVBoxLayout, QAction)

from dls_imagematch.crystal import CrystalMatchConfig, AlignConfig
from dls_imagematch.feature.detector import DetectorConfig, DetectorType
from dls_util.config import ConfigDialog
from .components import AutoImageAligner
from .components import CrystalMatchControl
from .components import ImageFrame
from .components import ImageSelector
from .components import WellSelectorFormulatrix
from .config import GuiConfig


class VMXiCrystalMatchMainWindow(QMainWindow):
    def __init__(self, config_dir):
        super(VMXiCrystalMatchMainWindow, self).__init__()

        self.gui_state = None
        self.matcher = None
        self._aligner = None

        self._gui_config = GuiConfig(config_dir)
        self._crystal_config = CrystalMatchConfig(config_dir)
        self._align_config = AlignConfig(config_dir)

        self.init_ui()

    def init_ui(self):
        """ Create all elements of the user interface. """
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowTitle('Diamond VMXi Image Matching')
        self.setWindowIcon(QIcon('web.png'))

        self.init_menu_bar()

        # Image selectors
        selector1 = ImageSelector("Select Image 1", self._gui_config)
        selector2 = ImageSelector("Select Image 2", self._gui_config)

        # Plate well selector (example data set)
        well_selector = WellSelectorFormulatrix(self._gui_config)

        # Main image frame - shows progress of image matching
        image_frame = ImageFrame(self._gui_config)

        # Automatic Image Aligner
        self._aligner = AutoImageAligner(self._gui_config, self._align_config)

        # Secondary Matching Control
        crystal_match = CrystalMatchControl(image_frame, self._gui_config, self._crystal_config)

        # Connect signals
        self._aligner.signal_aligned.connect(crystal_match.set_aligned_images)
        self._aligner.signal_aligned.connect(image_frame.display_align_results)

        selector1.signal_selected.connect(self._aligner.set_image_1)
        selector2.signal_selected.connect(self._aligner.set_image_2)

        well_selector.signal_image1_selected.connect(selector1.set_image)
        well_selector.signal_image2_selected.connect(selector2.set_image)
        well_selector.signal_images_selected.connect(self._aligner.set_images)

        well_selector.signal_image1_selected.connect(crystal_match.reset)
        well_selector.signal_image1_selected.connect(image_frame.clear)

        # Create layout
        vbox_image_selection = QVBoxLayout()
        vbox_image_selection.addWidget(well_selector)
        vbox_image_selection.addWidget(selector1)
        vbox_image_selection.addWidget(selector2)
        vbox_image_selection.addStretch(1)

        vbox_matching = QVBoxLayout()
        vbox_matching.addWidget(crystal_match)
        vbox_matching.addWidget(image_frame)
        vbox_matching.addStretch(1)

        hbox_main = QHBoxLayout()
        hbox_main.setSpacing(10)
        hbox_main.addLayout(vbox_image_selection)
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
        crystal_opt = QtGui.QAction('&Crystal Matching...', self)
        crystal_opt.setStatusTip('Open Crystal Matching Options Dialog')
        crystal_opt.triggered.connect(lambda: self._open_config_dialog(self._crystal_config))

        align_opt = QtGui.QAction('&Image Alignment...', self)
        align_opt.setStatusTip('Open Image Alignment Options Dialog')
        align_opt.triggered.connect(lambda: self._open_config_dialog(self._align_config))

        gui_opt = QtGui.QAction('&Gui...', self)
        gui_opt.setStatusTip('Open GUI Options Dialog')
        gui_opt.triggered.connect(lambda: self._open_config_dialog(self._gui_config))

        detector_menu = QtGui.QMenu('Detectors', self)
        for det_type in DetectorType.LIST_ALL:
            detector_menu.addAction(self._init_detector_menu(det_type))

        license_opt = QtGui.QAction('&Licensing...', self)
        license_opt.setStatusTip('Open Detector Licensing Options Dialog')
        config = DetectorConfig(self._gui_config.config_dir.value()).get_licensing_options()
        license_opt.triggered.connect(lambda: self._open_config_dialog(config))

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

        option_menu = menu_bar.addMenu('&Option')
        option_menu.addAction(gui_opt)
        option_menu.addAction(align_opt)
        option_menu.addAction(crystal_opt)
        option_menu.addAction(license_opt)
        option_menu.addMenu(detector_menu)

    def _init_detector_menu(self, detector):
        action = QtGui.QAction(detector + "...", self)
        action.triggered.connect(lambda: self._open_detector_config_dialog(detector))
        return action

    def _open_detector_config_dialog(self, detector):
        config_dir = self._gui_config.config_dir.value()
        config = DetectorConfig(config_dir)
        options = config.get_detector_options(detector)
        self._open_config_dialog(options)

    @staticmethod
    def _open_config_dialog(config):
        dialog = ConfigDialog(config)
        dialog.auto_layout()
        dialog.exec_()
