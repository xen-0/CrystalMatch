from __future__ import division
import os
import sys
from enum import Enum

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QWidget, QLabel, QPushButton, QMainWindow, QIcon,
                         QHBoxLayout, QVBoxLayout, QPixmap, QApplication, QAction)


from dls_imagematch.match.image import Image
from dls_imagematch import RegionMatcher
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
        self.region_matcher = None
        self.mov_img_scale_factor = 1
        self.file_a = None
        self.file_b = None

        self.init_ui()

        self.set_gui_state(GuiStates.SELECTION)

        # Select and Display the default images
        self.function_select_well()

        #self.iterate_over_441350000072_data_set()

    def init_ui(self):
        """ Create all elements of the user interface. """
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowTitle('Diamond VMXi Image Matching')
        self.setWindowIcon(QIcon('web.png'))

        self.init_menu_bar()

        gpBox_well_select = QtGui.QGroupBox("Select Well")
        gpBox_select_a = QtGui.QGroupBox("Select Image A")
        gpBox_select_b = QtGui.QGroupBox("Select Image B")

        # Drop-down box to select data set
        self.cmbo_plate_row = QtGui.QComboBox()
        self.cmbo_plate_col = QtGui.QComboBox()
        for c in range(ord('A'), ord('H')+1):
            self.cmbo_plate_row.addItem(chr(c))
        for col in range(1,13):
            self.cmbo_plate_col.addItem(str(col))

        self.btn_select_data = QPushButton("Select")
        self.btn_select_data.clicked.connect(self.function_select_well)

        # Selection buttons - make selection of currently displayed image as A or B
        self.btn_select_a = QPushButton("Load Image")
        self.btn_select_a.clicked.connect(self.function_select_a)
        self.btn_select_b = QPushButton("Load Image")
        self.btn_select_b.clicked.connect(self.function_select_b)

        # Selection filename - displays filename of selected images (A and B)
        self.lbl_selection_a = QLabel("No Image Selected")
        self.lbl_selection_a.setFixedWidth(250)

        self.lbl_selection_b = QLabel("No Image Selected")
        self.lbl_selection_b.setFixedWidth(250)

        # Selection pixel size
        self.lbl_pixelsize_a = QLabel("Size per pixel:")
        self.txt_pixelsize_a = QtGui.QLineEdit()
        self.txt_pixelsize_a.setFixedWidth(60)
        self.lbl_um_a = QLabel("um")

        self.lbl_pixelsize_b = QLabel("Size per pixel:")
        self.txt_pixelsize_b = QtGui.QLineEdit()
        self.txt_pixelsize_b.setFixedWidth(60)
        self.lbl_um_b = QLabel("um")

        # Selection Image Frames - displays smaller versions of currently selected images (A and B)
        self.frame_a = QLabel("No Image Selected")
        self.frame_a.setStyleSheet("background-color: black; color: red; font-size: 20pt; text-align: center")
        self.frame_a.setFixedWidth(350)
        self.frame_a.setFixedHeight(350)
        self.frame_a.setAlignment(Qt.AlignCenter)

        self.frame_b = QLabel("No Image Selected")
        self.frame_b.setStyleSheet("background-color: black; color: red; font-size: 20pt; text-align: center")
        self.frame_b.setFixedWidth(350)
        self.frame_b.setFixedHeight(350)
        self.frame_b.setAlignment(Qt.AlignCenter)

        # Main image frame - shows progress of image matching
        self.frame_main = QLabel()
        self.frame_main.setStyleSheet("background-color: black; color: red; font-size: 30pt; text-align: center")
        self.frame_main.setFixedWidth(850)
        self.frame_main.setFixedHeight(850)

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

        # Create layout
        hbox_well_select = QHBoxLayout()
        hbox_well_select.addWidget(self.cmbo_plate_row)
        hbox_well_select.addWidget(self.cmbo_plate_col)
        hbox_well_select.addWidget(self.btn_select_data)
        hbox_well_select.addStretch(1)
        gpBox_well_select.setLayout(hbox_well_select)

        hbox_select_a = QHBoxLayout()
        hbox_select_a.addWidget(self.btn_select_a)
        hbox_select_a.addWidget(self.lbl_selection_a)
        hbox_select_a2 = QHBoxLayout()
        hbox_select_a2.addWidget(self.lbl_pixelsize_a)
        hbox_select_a2.addWidget(self.txt_pixelsize_a)
        hbox_select_a2.addWidget(self.lbl_um_a)
        hbox_select_a2.addStretch(1)
        vbox_select_a = QVBoxLayout()
        vbox_select_a.addLayout(hbox_select_a)
        vbox_select_a.addWidget(self.frame_a)
        vbox_select_a.addLayout(hbox_select_a2)
        gpBox_select_a.setLayout(vbox_select_a)

        hbox_select_b = QHBoxLayout()
        hbox_select_b.addWidget(self.btn_select_b)
        hbox_select_b.addWidget(self.lbl_selection_b)
        hbox_select_b2 = QHBoxLayout()
        hbox_select_b2.addWidget(self.lbl_pixelsize_b)
        hbox_select_b2.addWidget(self.txt_pixelsize_b)
        hbox_select_b2.addWidget(self.lbl_um_b)
        hbox_select_b2.addStretch(1)
        vbox_select_b = QVBoxLayout()
        vbox_select_b.addLayout(hbox_select_b)
        vbox_select_b.addWidget(self.frame_b)
        vbox_select_b.addLayout(hbox_select_b2)
        gpBox_select_b.setLayout(vbox_select_b)

        vbox_img_selection = QVBoxLayout()
        vbox_img_selection.addWidget(gpBox_well_select)
        vbox_img_selection.addWidget(gpBox_select_a)
        vbox_img_selection.addWidget(gpBox_select_b)
        vbox_img_selection.addStretch(1)

        vbox_match_btns = QVBoxLayout()
        vbox_match_btns.addStretch(1)
        vbox_match_btns.addWidget(self.btn_begin_match)
        vbox_match_btns.addWidget(self.btn_next_frame)
        vbox_match_btns.addWidget(self.btn_next_scale)
        vbox_match_btns.addWidget(self.btn_end_match)
        vbox_match_btns.addWidget(self.btn_region_select)
        vbox_match_btns.addStretch(1)

        hbox_main = QHBoxLayout()
        hbox_main.setSpacing(10)
        hbox_main.addLayout(vbox_img_selection)
        hbox_main.addWidget(self.frame_main)
        hbox_main.addLayout(vbox_match_btns)
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

        # Match Action
        match_action = QAction(QIcon('exit.png'), '&Perform Match', self)
        match_action.setShortcut('Ctrl+M')
        match_action.setStatusTip('Perform Match')
        match_action.triggered.connect(self.function_begin_matching)

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

        match_menu = menu_bar.addMenu('&Match')
        match_menu.addAction(match_action)

    ''' ----------------------
    IMAGE SELECTION FUNCTIONS
    ------------------------'''
    def function_select_well(self):
        """ Select a well from the 441350000072 dataset to use for matching. Display the
        corresponding images in slot A and B. """
        row = self.cmbo_plate_row.currentText()
        col = self.cmbo_plate_col.currentText()

        fileA, fileB = self._get_441350000072_files(row, col)
        self.function_select_a(fileA)
        self.function_select_b(fileB)

        # Set pixel sizes
        SET_FACTOR = 6.55
        pixel_size_a = 4.0
        pixel_size_b = pixel_size_a / SET_FACTOR
        self.txt_pixelsize_a.setText("{0:.5f}".format(pixel_size_a))
        self.txt_pixelsize_b.setText("{0:.5f}".format(pixel_size_b))

        self.set_gui_state(GuiStates.SELECTION)

    def function_select_a(self, filepath=None):
        """ Display open dialog for Image slot A, load the selected image. """
        if filepath is None or not filepath:
            filepath = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', INPUT_DIR_ROOT))
        if filepath:
            self._display_image(self.frame_a, filepath)
            self._set_filename_label(self.lbl_selection_a, filepath)
            self.file_a = filepath

    def function_select_b(self, filepath=None):
        """ Display open dialog for Image slot A, load the selected image. """
        if filepath is None or not filepath:
            filepath = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', INPUT_DIR_ROOT))
        if filepath:
            self._display_image(self.frame_b, filepath)
            self._set_filename_label(self.lbl_selection_b, filepath)
            self.file_b = filepath

    @staticmethod
    def _display_image(frame, filename):
        """ Display the selected image in the specified frame. """
        frame.clear()
        frame.setAlignment(Qt.AlignCenter)

        if filename is None:
            frame.setText("No Image Selected")
        elif os.path.isfile(filename):
            pixmap = QPixmap(filename)
            frame.setPixmap(pixmap.scaled(frame.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            frame.setText("Image Not Found")

    @staticmethod
    def _set_filename_label(label, filepath):
        """ Display the filename in the specified label. """
        if filepath and filepath != "":
            label.setText(filepath.split('/')[-1])
        else:
            label.setText("No Image Selected")

    @staticmethod
    def _get_441350000072_files(row, col):
        """ Get the full paths of the files for the specified well of the 441350000072 data set. """
        mov_filepath = INPUT_DIR_ROOT + "441350000072_OAVS/_1_" + str(row) + str(col) + ".png"
        col = int(col)
        if col < 10:
            col = '0' + str(col)

        ref_filepath = INPUT_DIR_ROOT + "441350000072/" + str(row) + str(col) + "_13.jpg"

        return ref_filepath, mov_filepath

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
        self.primary_image_matching()
        self.set_gui_state(GuiStates.MATCHING)

    def function_next_frame(self):
        """ Advance to the next frame of the matching procedure. """
        if self.region_matcher is not None:
            self.region_matcher.next_frame()
            self.display_match_results()

    def function_next_scale(self):
        """ Advance to the next scale factor of the matching procedure. """
        if self.region_matcher is not None:
            self.region_matcher.skip_to_next_scale()
            self.display_match_results()

    def function_skip_to_end(self):
        """ Advance to the end of the matching procedure (dont show any frames). """
        if self.region_matcher is not None:
            self.region_matcher.skip_to_end()
            self.display_match_results()

    def function_select_region(self):
        """ For a completed primary matching procedure, select a sub-region (feature) to track. """
        filename = self.file_a
        region_image, roi = RegionSelectDialog.get_region(self, filename)

        if region_image is not None:
            img_a = Image.from_file(self.file_b, region_image.pixel_size)
            img_a = img_a.rescale(self.mov_img_scale_factor)
            self.secondary_image_matching(img_a, region_image, roi)
            self.set_gui_state(GuiStates.MATCHING_2ND)

    ''' ----------------------
    IMAGE MATCHING FUNCTIONS
    ------------------------'''
    def primary_image_matching(self):
        """ Begin the image matching process, attempting to map image B onto image A. """
        if not self.file_a or not self.file_b or self.file_a == self.file_b:
            return

        pixel_size_a = float(self.txt_pixelsize_a.text())
        pixel_size_b = float(self.txt_pixelsize_b.text())

        # For the 441350000072 test set
        guess_x = 0.1
        guess_y = 0.4
        #guess_x = 0.2;  guess_y = 0.1

        # Read the selected images and convert to grayscale
        ref_file = self.file_a
        trans_file = self.file_b

        # Get greyscale versions of the selected images
        ref_gray_img = Image.from_file(ref_file, pixel_size_a).make_gray()
        mov_gray_img = Image.from_file(trans_file, pixel_size_b).make_gray()

        # Resize the mov image so it has the same size per pixel as the ref image
        factor = mov_gray_img.pixel_size / ref_gray_img.pixel_size
        mov_gray_img = mov_gray_img.rescale(factor)
        self.mov_img_scale_factor = factor

        # Perform the matching operation to determine the transformation that maps image B to image A
        guess = Translate(guess_x*ref_gray_img.size[0], guess_y*ref_gray_img.size[1]); print(guess.x, guess.y)
        self.region_matcher = RegionMatcher(ref_gray_img, mov_gray_img, guess)
        self.function_next_frame()

    def secondary_image_matching(self, imgA, imgB, roi):
        imgA_gray = imgA.make_gray()
        imgB_gray = imgB.make_gray()

        primary_transform = self.region_matcher.net_transform
        guessX = roi[0] - primary_transform.x
        guessY = roi[1] - primary_transform.y
        guess = Translate(guessX, guessY)

        self.region_matcher = RegionMatcher(imgA_gray, imgB_gray, guess, scales=(1,))
        self.function_next_frame()

    def display_match_results(self):
        frame = self.frame_main
        pixmap = self.region_matcher.match_img.make_color().to_qt_pixmap()
        frame.setPixmap(pixmap.scaled(frame.size(),
                                      Qt.KeepAspectRatio, Qt.SmoothTransformation))

        if self.region_matcher.match_complete:
            matcher = self.region_matcher

            # Determine transformation in real units (um)
            net_transform = matcher.net_transform
            x, y = net_transform.x, net_transform.y

            pixel_size = matcher.stat_img.pixel_size
            delta_x = x * pixel_size
            delta_y = y * pixel_size

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
                ref, mov = self._get_441350000072_files(row, col)
                self._display_image(self.frame_a, ref)
                self._display_image(self.frame_b, mov)
                self._set_filename_label(self.lbl_selection_a, ref)
                self._set_filename_label(self.lbl_selection_b, mov)
                self.file_a = ref
                self.file_b = mov
                self._perform_image_matching()
                self._skip_to_end_pushed()

                out_file = "441350000072/" + str(row) + "_" + str(col)
                self.region_matcher.match_img.save(out_file)



def main():
    app = QApplication(sys.argv)
    ex = ImageMatcherGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
