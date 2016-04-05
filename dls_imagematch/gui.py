from __future__ import division

import sys

from PyQt4 import QtGui
from PyQt4.QtGui import (QWidget, QMainWindow, QIcon,
                         QHBoxLayout, QVBoxLayout, QApplication, QAction)

from dls_imagematch.gui import ImageSelector, WellSelector, RegionMatchControl, ImageFrame
from dls_imagematch.match import FeatureMatcher, Overlayer

INPUT_DIR_ROOT = "../test-images/"
OUTPUT_DIRECTORY = "../test-output/"


class ImageMatcherGui(QMainWindow):
    def __init__(self):
        super(ImageMatcherGui, self).__init__()

        self.gui_state = None
        self.matcher = None

        self.init_ui()

        # Select and Display the default images
        self.well_selector._select_well()

        #self.iterate_over_441350000072_data_set()

    def init_ui(self):
        """ Create all elements of the user interface. """
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowTitle('Diamond VMXi Image Matching')
        self.setWindowIcon(QIcon('web.png'))

        self.init_menu_bar()

        # Image selectors
        self.selector_a = ImageSelector("Select Image A")
        self.selector_b = ImageSelector("Select Image B")

        # Plate well selector (example data set)
        self.well_selector = WellSelector(self.selector_a, self.selector_b)

        # Main image frame - shows progress of image matching
        self.image_frame = ImageFrame()

        # Region Matching Control
        self.region_match = RegionMatchControl(self.selector_a, self.selector_b, self.image_frame)

        # Create layout
        vbox_img_selection = QVBoxLayout()
        vbox_img_selection.addWidget(self.well_selector)
        vbox_img_selection.addWidget(self.selector_a)
        vbox_img_selection.addWidget(self.selector_b)
        vbox_img_selection.addStretch(1)

        vbox_matching = QVBoxLayout()
        vbox_matching.addWidget(self.region_match)
        vbox_matching.addWidget(self.image_frame)
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

    def init_menu_bar(self):
        """Create and populate the menu bar. """
        # Exit Application
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)

        # Region Match Action
        region_match_action = QAction(QIcon('exit.png'), '&Region Match', self)
        region_match_action.setShortcut('Ctrl+M')
        region_match_action.setStatusTip('Perform Region Match')
        region_match_action.triggered.connect(self._fn_region_match)

        # Region Match Action
        feature_match_action = QAction(QIcon('exit.png'), '&Feature Match', self)
        feature_match_action.setShortcut('Ctrl+F')
        feature_match_action.setStatusTip('Perform Feature Match')
        feature_match_action.triggered.connect(self._fn_feature_match)

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

        match_menu = menu_bar.addMenu('&Match')
        match_menu.addAction(region_match_action)
        match_menu.addAction(feature_match_action)


    ''' ----------------------
    IMAGE MATCHING FUNCTIONS
    ------------------------'''
    def _fn_region_match(self):
        self.region_match.match()

    def _fn_feature_match(self):
        self.feature_matching()

    def feature_matching(self):
        img_a, img_b = self.prepare_match_images()
        self.matcher = FeatureMatcher(img_a, img_b)
        self.matcher.perform_match()
        self.display_match_results()

    def prepare_match_images(self):
        # Get the selected images
        self.img_a = self.selector_a.image()
        self.img_b = self.selector_b.image()

        # Resize the mov image so it has the same size per pixel as the ref image
        factor = self.img_b.pixel_size / self.img_a.pixel_size
        self.img_b = self.img_b.rescale(factor)
        self.mov_img_scale_factor = factor

        return self.img_a.make_gray(), self.img_b.make_gray()

    def _display_results(self):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        transform = self.matcher.net_transform

        # Create image of B overlaid on A
        img = Overlayer.create_overlay_image(self.img_a, self.img_b, transform)
        self.image_frame.display_image(img)

    def iterate_over_441350000072_data_set(self):
        """ Perform primary match for every image in the data set. """
        for c in range(ord('A'), ord('H')+1):
            row = chr(c)
            for col in range(1,13):
                ref, mov = WellSelector._get_441350000072_files(row, col)
                self._display_image(self.frame_a, ref)
                self._display_image(self.frame_b, mov)
                self._set_filename_label(self.lbl_selection_a, ref)
                self._set_filename_label(self.lbl_selection_b, mov)
                self.file_a = ref
                self.file_b = mov
                self._perform_image_matching()
                self._skip_to_end_pushed()

                out_file = "441350000072/" + str(row) + "_" + str(col)
                self.matcher.match_img.save(out_file)


def main():
    app = QApplication(sys.argv)
    ex = ImageMatcherGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
