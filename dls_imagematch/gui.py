from __future__ import division

import sys

from PyQt4 import QtGui
from PyQt4.QtGui import (QWidget, QLabel, QPushButton, QMainWindow, QIcon,
                         QHBoxLayout, QVBoxLayout, QApplication, QAction)
from enum import Enum

from dls_imagematch import RegionMatcher
from dls_imagematch.gui import ImageSelector, WellSelector, ImageFrame
from dls_imagematch.gui.image_frame import ImageFrame
from dls_imagematch.image import Image
from dls_imagematch.match import FeatureMatcher
from dls_imagematch.match.overlay import Overlayer
from dls_imagematch.regionselect import RegionSelectDialog
from dls_imagematch.util.translate import Translate

INPUT_DIR_ROOT = "../test-images/"
OUTPUT_DIRECTORY = "../test-output/"

class GuiStates(Enum):
    SELECTION = 1
    MATCHING = 2
    MATCHING_COMPLETE = 3
    MATCHING_2ND = 4
    MATCHING_2ND_COMPLETE = 5



class ImageMatcherGui(QMainWindow):
    def __init__(self):
        super(ImageMatcherGui, self).__init__()

        self.gui_state = None
        self.matcher = None
        self.mov_img_scale_factor = 1
        self.file_a = None
        self.file_b = None
        self.img_a = None
        self.img_b = None

        self.init_ui()

        self.set_gui_state(GuiStates.SELECTION)

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

        # Matching guess
        gpBox_match_guess = QtGui.QGroupBox("Region Matching")
        self.txt_guess_x = QtGui.QLineEdit("0.1")
        self.txt_guess_x.setFixedWidth(40)
        self.txt_guess_y = QtGui.QLineEdit("0.4")
        self.txt_guess_y.setFixedWidth(40)

        # Matching function buttons
        self.btn_begin_match = QPushButton("Begin Match")
        self.btn_begin_match.clicked.connect(self.function_begin_matching)
        self.btn_next_frame = QPushButton("Next Frame >>")
        self.btn_next_frame.clicked.connect(self.function_next_frame)
        self.btn_next_scale = QPushButton("Next Scale >>")
        self.btn_next_scale.clicked.connect(self.function_next_scale)
        self.btn_end_match = QPushButton("Skip To End >>")
        self.btn_end_match.clicked.connect(self.function_skip_to_end)
        self.btn_region_select = QPushButton("Select Region")
        self.btn_region_select.clicked.connect(self.function_select_region)
        self.btn_region_select.setEnabled(False)

        # Main image frame - shows progress of image matching
        self.image_frame = ImageFrame()

        # Create layout
        vbox_img_selection = QVBoxLayout()
        vbox_img_selection.addWidget(self.well_selector)
        vbox_img_selection.addWidget(self.selector_a)
        vbox_img_selection.addWidget(self.selector_b)
        vbox_img_selection.addStretch(1)

        hbox_match_btns = QHBoxLayout()
        hbox_match_btns.addWidget(self.btn_begin_match)
        hbox_match_btns.addWidget(self.btn_next_frame)
        hbox_match_btns.addWidget(self.btn_next_scale)
        hbox_match_btns.addWidget(self.btn_end_match)
        hbox_match_btns.addWidget(self.btn_region_select)
        hbox_match_btns.addStretch(1)

        hbox_match_guess = QHBoxLayout()
        hbox_match_guess.addWidget(QLabel("X:"))
        hbox_match_guess.addWidget(self.txt_guess_x)
        hbox_match_guess.addWidget(QLabel("Y:"))
        hbox_match_guess.addWidget(self.txt_guess_y)
        hbox_match_guess.addStretch(1)
        hbox_match_guess.addLayout(hbox_match_btns)
        hbox_match_guess.addStretch(3)
        gpBox_match_guess.setLayout(hbox_match_guess)

        vbox_matching = QVBoxLayout()
        vbox_matching.addWidget(gpBox_match_guess)
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
        region_match_action.triggered.connect(self.function_begin_matching)

        # Region Match Action
        feature_match_action = QAction(QIcon('exit.png'), '&Feature Match', self)
        feature_match_action.setShortcut('Ctrl+F')
        feature_match_action.setStatusTip('Perform Feature Match')
        feature_match_action.triggered.connect(self.feature_matching)

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

        match_menu = menu_bar.addMenu('&Match')
        match_menu.addAction(region_match_action)
        match_menu.addAction(feature_match_action)


    ''' ----------------------
    BUTTON FUNCTIONS
    ------------------------'''
    def set_gui_state(self, state):
        """ Set the current state of the GUI, enabling/disabling elements as appropriate. """
        self.gui_state = state

        self.btn_begin_match.setEnabled(False)
        self.btn_next_frame.setEnabled(False)
        self.btn_next_scale.setEnabled(False)
        self.btn_end_match.setEnabled(False)
        self.btn_region_select.setEnabled(False)

        if state == GuiStates.SELECTION:
            self.btn_begin_match.setEnabled(True)
        elif state == GuiStates.MATCHING:
            self.btn_next_frame.setEnabled(True)
            self.btn_next_scale.setEnabled(True)
            self.btn_end_match.setEnabled(True)
        elif state == GuiStates.MATCHING_COMPLETE:
            self.btn_region_select.setEnabled(True)
        elif state == GuiStates.MATCHING_2ND:
            self.btn_next_frame.setEnabled(True)
            self.btn_end_match.setEnabled(True)
        elif state == GuiStates.MATCHING_2ND_COMPLETE:
            self.btn_begin_match.setEnabled(True)
        else:
            raise NotImplementedError

    def function_begin_matching(self):
        """ Begin the matching procedure using the two selected images. """
        self.region_matching_primary()
        self.set_gui_state(GuiStates.MATCHING)

    def function_next_frame(self):
        """ Advance to the next frame of the matching procedure. """
        if self.matcher is not None:
            self.matcher.next_frame()
            self.display_match_results()

    def function_next_scale(self):
        """ Advance to the next scale factor of the matching procedure. """
        if self.matcher is not None:
            self.matcher.skip_to_next_scale()
            self.display_match_results()

    def function_skip_to_end(self):
        """ Advance to the end of the matching procedure (dont show any frames). """
        if self.matcher is not None:
            self.matcher.skip_to_end()
            self.display_match_results()

    def function_select_region(self):
        """ For a completed primary matching procedure, select a sub-region (feature) to track. """
        filename = self.file_a
        region_image, roi = RegionSelectDialog.get_region(self, filename)

        if region_image is not None:
            pixel_size = self.img_b.pixel_size * self.mov_img_scale_factor
            img_a = Image.from_file(self.file_b, pixel_size)
            img_a = img_a.rescale(self.mov_img_scale_factor)
            self.region_matching_secondary(img_a, region_image, roi)
            self.set_gui_state(GuiStates.MATCHING_2ND)

    ''' ----------------------
    IMAGE MATCHING FUNCTIONS
    ------------------------'''
    def feature_matching(self):
        img_a, img_b = self.prepare_match_images()
        self.matcher = FeatureMatcher(img_a, img_b)
        self.matcher.perform_match()
        self.display_match_results()

    def region_matching_primary(self):
        img_a, img_b = self.prepare_match_images()

        guess_x = float(self.txt_guess_x.text())
        guess_y = float(self.txt_guess_y.text())
        guess = Translate(guess_x*img_a.size[0], guess_y*img_a.size[1])
        self.matcher = RegionMatcher(img_a, img_b, guess)
        self.function_next_frame()

    def prepare_match_images(self):
        self.file_a = self.selector_a.file()
        self.file_b = self.selector_b.file()
        if not self.file_a or not self.file_b:
            return None, None

        # Get pixel sizes and starting guess position
        pixel_size_a = self.selector_a.pixelSize()
        pixel_size_b = self.selector_b.pixelSize()

        # Get greyscale versions of the selected images
        self.img_a = Image.from_file(self.file_a, pixel_size_a)
        img_b = Image.from_file(self.file_b, pixel_size_b)

        # Resize the mov image so it has the same size per pixel as the ref image
        factor = img_b.pixel_size / self.img_a.pixel_size
        self.img_b = img_b.rescale(factor)
        self.mov_img_scale_factor = factor

        return self.img_a.make_gray(), self.img_b.make_gray()

    def region_matching_secondary(self, imgA, imgB, roi):
        self.img_a = imgA
        self.img_b = imgB
        imgA_gray = imgA.make_gray()
        imgB_gray = imgB.make_gray()

        primary_transform = self.matcher.net_transform
        guessX = roi[0] - primary_transform.x
        guessY = roi[1] - primary_transform.y
        guess = Translate(guessX, guessY)

        self.matcher = RegionMatcher(imgA_gray, imgB_gray, guess, scales=(1,))
        self.function_next_frame()

    def display_match_results(self):
        transform = self.matcher.net_transform

        # Create image of B overlaid on A
        img = Overlayer.create_overlay_image(self.img_a, self.img_b, transform)
        self.image_frame.display_image(img)

        if self.matcher.match_complete:
            # Determine transformation in real units (um)
            x, y = transform.x, transform.y

            pixel_size = self.img_a.pixel_size
            delta_x = "{0:.2f}".format(x * pixel_size)
            delta_y = "{0:.2f}".format(y * pixel_size)

            # Print results
            print("Image offset: x=" + str(delta_x) + " um (" + str(int(x)) + " pixels), y="
                  + str(delta_y) + " um (" + str(int(y)) + " pixels)")

            if self.gui_state == GuiStates.MATCHING:
                self.set_gui_state(GuiStates.MATCHING_COMPLETE)
            elif self.gui_state == GuiStates.MATCHING_2ND:
                self.set_gui_state(GuiStates.MATCHING_2ND_COMPLETE)

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
