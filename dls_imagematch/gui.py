import os
import sys
from enum import Enum

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import (Qt, SIGNAL)
from PyQt4.QtGui import (QWidget, QFileSystemModel, QTreeView, QLabel, QPushButton,
                         QMainWindow, QIcon, QHBoxLayout, QVBoxLayout, QPixmap, QApplication, QAction)


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
        self._region_matcher = None
        self.mov_img_scale_factor = 1

        self._selection_A = None
        self._selection_B = None

        self._result_frame = None
        self._selection_A_frame = None
        self._selection_A_label = None
        self._selection_B_frame = None
        self._selection_B_label = None

        self._init_ui()

        self.set_gui_state(GuiStates.SELECTION)

        # Select and Display the default images
        filepath = INPUT_DIR_ROOT + "441350000072/A01_13.jpg"
        self._display_image(self._selection_A_frame, filepath)
        self._set_filename_label(self._selection_A_label, filepath)
        self._selection_A = filepath

        filepath = INPUT_DIR_ROOT + "441350000072_OAVS/_1_A1.png"
        self._display_image(self._selection_B_frame, filepath)
        self._set_filename_label(self._selection_B_label, filepath)
        self._selection_B = filepath

        #self.iterate_over_441350000072_data_set()

    def _init_ui(self):
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowTitle('Diamond VMXi Image Matching')
        self.setWindowIcon(QIcon('web.png'))

        self.init_menu_bar()

        # Image frame - displays the image currently selected in the file tree
        self._result_frame = QLabel()
        self._result_frame.setStyleSheet("background-color: black; color: red; font-size: 30pt; text-align: center")
        self._result_frame.setFixedWidth(850)
        self._result_frame.setFixedHeight(850)

        # Dropdown box to select data set
        self.data_combo1 = QtGui.QComboBox()
        self.data_combo2 = QtGui.QComboBox()
        for c in range(ord('A'), ord('H')+1):
            self.data_combo1.addItem(chr(c))
        for col in range(1,13):
            self.data_combo2.addItem(str(col))

        data_button = QPushButton("Select")
        data_button.clicked.connect(self.function_select_well)
        data_select_label = QLabel()
        data_select_label.setText("Select Well:")

        # Selection buttons - make selection of currently displayed image as A or B
        self._select_A_button = QPushButton("Select Reference Image")
        self._select_A_button.clicked.connect(self.function_select_A)
        self._select_B_button = QPushButton("Select Matching Image")
        self._select_B_button.clicked.connect(self.function_select_B)

        # Selection filename - displays filename of selected images (A and B)
        self._selection_A_label = QLabel()
        self._selection_A_label.setFixedWidth(300)
        self._selection_A_label.setText("No Image Selected")

        self._selection_B_label = QLabel()
        self._selection_B_label.setFixedWidth(300)
        self._selection_B_label.setText("No Image Selected")

        # Selection Image Frames - displays smaller versions of currently selected images (A and B)
        self._selection_A_frame = QLabel()
        self._selection_A_frame.setStyleSheet("background-color: black; color: red; font-size: 20pt; text-align: center")
        self._selection_A_frame.setFixedWidth(400)
        self._selection_A_frame.setFixedHeight(400)
        self._selection_A_frame.setText("No Image Selected")
        self._selection_A_frame.setAlignment(Qt.AlignCenter)

        self._selection_B_frame = QLabel()
        self._selection_B_frame.setStyleSheet("background-color: black; color: red; font-size: 20pt; text-align: center")
        self._selection_B_frame.setFixedWidth(400)
        self._selection_B_frame.setFixedHeight(400)
        self._selection_B_frame.setText("No Image Selected")
        self._selection_B_frame.setAlignment(Qt.AlignCenter)

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
        hbox_A = QHBoxLayout()

        hbox_A.addWidget(self._select_A_button)
        hbox_A.addWidget(self._selection_A_label)
        vbox_A = QVBoxLayout()
        vbox_A.addLayout(hbox_A)
        vbox_A.addWidget(self._selection_A_frame)

        hbox_B = QHBoxLayout()
        hbox_B.addWidget(self._select_B_button)
        hbox_B.addWidget(self._selection_B_label)
        vbox_B = QVBoxLayout()
        vbox_B.addLayout(hbox_B)
        vbox_B.addWidget(self._selection_B_frame)

        hbox_C = QHBoxLayout()
        hbox_C.addWidget(data_select_label)
        hbox_C.addWidget(self.data_combo1)
        hbox_C.addWidget(self.data_combo2)
        hbox_C.addWidget(data_button)
        hbox_C.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_C)
        vbox.addLayout(vbox_A)
        vbox.addLayout(vbox_B)
        vbox.addStretch(1)

        vbox_buttons = QVBoxLayout()
        vbox_buttons.addStretch(1)
        vbox_buttons.addWidget(self.btn_begin_match)
        vbox_buttons.addWidget(self.btn_next_frame)
        vbox_buttons.addWidget(self.btn_next_scale)
        vbox_buttons.addWidget(self.btn_end_match)
        vbox_buttons.addWidget(self.btn_region_select)
        vbox_buttons.addStretch(1)

        hbox = QHBoxLayout()
        hbox.setSpacing(10)
        hbox.addLayout(vbox)
        hbox.addWidget(self._result_frame)
        hbox.addLayout(vbox_buttons)
        hbox.addStretch(1)

        main_widget = QWidget()
        main_widget.setLayout(hbox)
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
        match_action.triggered.connect(self.primary_image_matching)

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
        row = self.data_combo1.currentText()
        col = self.data_combo2.currentText()

        fileA, fileB = self._get_441350000072_files(row, col)
        self.function_select_A(fileA)
        self.function_select_B(fileB)

        self.set_gui_state(GuiStates.SELECTION)

    def function_select_A(self, filepath=None):
        """ Display open dialog for Image slot A, load the selected image. """
        if filepath is None or not filepath:
            filepath = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', INPUT_DIR_ROOT))
        if filepath:
            self._display_image(self._selection_A_frame, filepath)
            self._set_filename_label(self._selection_A_label, filepath)
            self._selection_A = filepath

    def function_select_B(self, filepath=None):
        """ Display open dialog for Image slot A, load the selected image. """
        if filepath is None or not filepath:
            filepath = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', INPUT_DIR_ROOT))
        if filepath:
            self._display_image(self._selection_B_frame, filepath)
            self._set_filename_label(self._selection_B_label, filepath)
            self._selection_B = filepath

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
        mov_filepath = INPUT_DIR_ROOT + "441350000072_OAVS/_1_" + row + str(col) + ".png"
        col = int(col)
        if col < 10:
            col = '0' + str(col)

        ref_filepath = INPUT_DIR_ROOT + "441350000072/" + row + str(col) + "_13.jpg"
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
        if self._region_matcher is not None:
            self._region_matcher.next_frame()
            self.display_match_results()

    def function_next_scale(self):
        """ Advance to the next scale factor of the matching procedure. """
        if self._region_matcher is not None:
            self._region_matcher.skip_to_next_scale()
            self.display_match_results()

    def function_skip_to_end(self):
        """ Advance to the end of the matching procedure (dont show any frames). """
        if self._region_matcher is not None:
            self._region_matcher.skip_to_end()
            self.display_match_results()

    def function_select_region(self):
        """ For a completed primary matching procedure, select a sub-region (feature) to track. """
        filename = self._selection_A
        region_image, roi = RegionSelectDialog.get_region(self, filename)

        if region_image is not None:
            imgA = Image.from_file(self._selection_B, region_image.pixel_size)
            imgA = imgA.rescale(self.mov_img_scale_factor)
            self.secondary_image_matching(imgA, region_image, roi)
            self.set_gui_state(GuiStates.MATCHING_2ND)

    ''' ----------------------
    IMAGE MATCHING FUNCTIONS
    ------------------------'''
    def primary_image_matching(self):
        if not self._selection_A or not self._selection_B or self._selection_A == self._selection_B:
            return

        # For the 441350000072 test set - approximate, we are assuming the well width is about 5mm
        # Made up but approx correct ratio for well #A1
        SET_FACTOR = 6.55
        pixel_size_A = 4.0
        pixel_size_B = pixel_size_A / SET_FACTOR
        guess_x = 0.1
        guess_y = 0.4

        '''
        pixel_size_A = pixel_size_B = 2.17217391
        guess_x = 0.2
        guess_y = 0.1
        '''

        # Read the selected images and convert to grayscale
        ref_file = self._selection_A
        trans_file = self._selection_B

        # Get greyscale versions of the selected images
        ref_gray_img = Image.from_file(ref_file, pixel_size_A).make_gray()
        mov_gray_img = Image.from_file(trans_file, pixel_size_B).make_gray()

        # Resize the mov image so it has the same size per pixel as the ref image
        factor = mov_gray_img.pixel_size / ref_gray_img.pixel_size
        mov_gray_img = mov_gray_img.rescale(factor)
        self.mov_img_scale_factor = factor

        # Perform the matching operation to determine the transformation that maps image B to image A
        guess = Translate(guess_x*ref_gray_img.size[0], guess_y*ref_gray_img.size[1]); print(guess.x, guess.y)
        self._region_matcher = RegionMatcher(ref_gray_img, mov_gray_img, guess)
        self.function_next_frame()

    def secondary_image_matching(self, imgA, imgB, roi):
        imgA_gray = imgA.make_gray()
        imgB_gray = imgB.make_gray()

        primary_transform = self._region_matcher.net_transform
        guessX = roi[0] - primary_transform.x
        guessY = roi[1] - primary_transform.y
        guess = Translate(guessX, guessY)

        self._region_matcher = RegionMatcher(imgA_gray, imgB_gray, guess, scales=(1,))
        self.function_next_frame()

    def display_match_results(self):
        frame = self._result_frame
        pixmap = self._region_matcher.match_img.make_color().to_qt_pixmap()
        frame.setPixmap(pixmap.scaled(frame.size(),
                                      Qt.KeepAspectRatio, Qt.SmoothTransformation))

        if self._region_matcher.match_complete:
            matcher = self._region_matcher

            # Determine transformation in real units (um)
            net_transform = matcher.net_transform
            x, y = net_transform.x, net_transform.y

            pixel_size = matcher.stat_img.pixel_size
            delta_x = x * pixel_size
            delta_y = y * pixel_size

            # Print results
            print("Image offset: x=" + str(delta_x), "µm (" + str(int(x)) + " pixels), y="
                  + str(delta_y) + " µm (" + str(int(y)) + " pixels)")

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
                self._display_image(self._selection_A_frame, ref)
                self._display_image(self._selection_B_frame, mov)
                self._set_filename_label(self._selection_A_label, ref)
                self._set_filename_label(self._selection_B_label, mov)
                self._selection_A = ref
                self._selection_B = mov
                self._perform_image_matching()
                self._skip_to_end_pushed()

                out_file = "441350000072/" + str(row) + "_" + str(col)
                self._region_matcher.match_img.save(out_file)



def main():
    app = QApplication(sys.argv)
    ex = ImageMatcherGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
