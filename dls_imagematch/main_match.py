from __future__ import division

import sys

from PyQt4 import QtGui
from PyQt4.QtGui import (QWidget, QMainWindow, QIcon, QHBoxLayout, QVBoxLayout, QApplication, QAction)

sys.path.append("..")

from dls_imagematch.gui import *
from dls_imagematch.config import Config


class VMXiCrystalMatcher(QMainWindow):
    CONFIG_FILE = "../config.ini"

    def __init__(self):
        super(VMXiCrystalMatcher, self).__init__()

        self.gui_state = None
        self.matcher = None

        self._config = Config(VMXiCrystalMatcher.CONFIG_FILE)

        self.init_ui()

    def init_ui(self):
        """ Create all elements of the user interface. """
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowTitle('Diamond VMXi Image Matching')
        self.setWindowIcon(QIcon('web.png'))

        self.init_menu_bar()

        # Image selectors
        selector_a = ImageSelector("Select Image A", self._config)
        selector_b = ImageSelector("Select Image B", self._config)

        # Plate well selector (example data set)
        well_selector2 = WellSelector2(selector_a, selector_b, self._config)

        # Main image frame - shows progress of image matching
        image_frame = ImageFrame(self._config)

        # Feature Matching Control
        aligner = FeatureMatchControl(selector_a, selector_b, image_frame, with_popup=False)

        # Secondary Matching Control
        secondary_match = CrystalMatchControl(selector_a, selector_b, image_frame, aligner, self._config)

        # Create layout
        vbox_img_selection = QVBoxLayout()
        vbox_img_selection.addWidget(well_selector2)
        vbox_img_selection.addWidget(aligner)
        vbox_img_selection.addWidget(selector_a)
        vbox_img_selection.addWidget(selector_b)
        vbox_img_selection.addStretch(1)

        vbox_matching = QVBoxLayout()
        vbox_matching.addWidget(secondary_match)
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

        well_selector2._select_well()

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

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

        option_menu = menu_bar.addMenu('&Option')
        option_menu.addAction(options_action)

    def _open_config_dialog(self):
        dialog = ConfigDialog(self._config)
        dialog.exec_()


def main():
    app = QApplication(sys.argv)
    ex = VMXiCrystalMatcher()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
