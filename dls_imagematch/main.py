from __future__ import division

import sys

from PyQt4 import QtGui
from PyQt4.QtGui import (QWidget, QMainWindow, QIcon, QHBoxLayout, QVBoxLayout, QApplication, QAction)

sys.path.append("..")

from dls_imagematch.gui import *


class VMXiCrystalMatcher(QMainWindow):
    def __init__(self):
        super(VMXiCrystalMatcher, self).__init__()

        self.gui_state = None
        self.matcher = None

        self.init_ui()

    def init_ui(self):
        """ Create all elements of the user interface. """
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowTitle('Diamond VMXi Image Matching')
        self.setWindowIcon(QIcon('web.png'))

        self.init_menu_bar()

        # Image selectors
        selector_a = ImageSelector("Select Image A")
        selector_b = ImageSelector("Select Image B")

        # Plate well selector (example data set)
        well_selector = WellSelector(selector_a, selector_b)
        well_selector2 = WellSelector2(selector_a, selector_b)

        # Main image frame - shows progress of image matching
        image_frame = ImageFrame()

        # Region Matching Control
        region_match = RegionMatchControl(selector_a, selector_b, image_frame)

        # Feature Matching Control
        feature_match = FeatureMatchControl(selector_a, selector_b, image_frame)

        # Create layout
        vbox_img_selection = QVBoxLayout()
        vbox_img_selection.addWidget(well_selector)
        vbox_img_selection.addWidget(well_selector2)
        vbox_img_selection.addWidget(selector_a)
        vbox_img_selection.addWidget(selector_b)
        vbox_img_selection.addStretch(1)

        vbox_matching = QVBoxLayout()
        vbox_matching.addWidget(feature_match)
        vbox_matching.addWidget(region_match)
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

        # Select and Display the default images
        well_selector._select_well()

    def init_menu_bar(self):
        """Create and populate the menu bar. """
        # Exit Application
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)


def main():
    app = QApplication(sys.argv)
    ex = VMXiCrystalMatcher()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
