import os
import sys
from os import path

import cv2
import numpy as np
from PyQt4 import QtGui
from PyQt4.QtCore import (Qt, SIGNAL)
from PyQt4.QtGui import (QWidget, QFileSystemModel, QTreeView, QLabel, QPushButton,
                         QMainWindow, QIcon, QHBoxLayout, QVBoxLayout, QPixmap, QApplication, QAction)

import dls_imagematch.util.transforms as tlib
from dls_imagematch.match.image import Image
from dls_imagematch import ImageMatcher

INPUT_DIR_ROOT = "../test-images/"

OUTPUT_DIRECTORY = "../test-output/"

USE_SET_441350000072 = True


class ImageMatcherGui(QMainWindow):
    def __init__(self):
        super(ImageMatcherGui, self).__init__()

        self._fileTreeView = None
        self.model = None
        self._selection_A = None
        self._selection_B = None

        self._main_frame = None
        self._selection_A_frame = None
        self._selection_A_label = None
        self._selection_B_frame = None
        self._selection_B_label = None

        self._init_ui()

        filepath = INPUT_DIR_ROOT + "old/translate-test-B/1_1.png"
        if USE_SET_441350000072:
            filepath = INPUT_DIR_ROOT + "441350000072/H12_13.jpg"
        self._display_image(self._selection_A_frame, filepath)
        self._set_filename_label(self._selection_A_label, filepath)
        self._selection_A = filepath

        filepath = INPUT_DIR_ROOT + "old/translate-test-B/1_2_cropped.png"
        if USE_SET_441350000072:
            filepath = INPUT_DIR_ROOT + "441350000072_OAVS/_1_H12.png"
        self._display_image(self._selection_B_frame, filepath)
        self._set_filename_label(self._selection_B_label, filepath)
        self._selection_B = filepath

    def _init_ui(self):
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowTitle('Diamond VMXi Image Matching')
        self.setWindowIcon(QIcon('web.png'))

        self.init_menu_bar()

        # Create view and model for file explorer - selecting an image displays it in the main frame
        self.model = QFileSystemModel()
        self.model.setRootPath(INPUT_DIR_ROOT)

        self._fileTreeView = QTreeView()
        self._fileTreeView.setModel(self.model)
        self._fileTreeView.setRootIndex(self.model.index(INPUT_DIR_ROOT))
        self._fileTreeView.setFixedWidth(300)
        self._fileTreeView.setFixedHeight(600)

        self._fileTreeView.setColumnWidth(0, 175)
        self._fileTreeView.setColumnWidth(1, 25)
        self._fileTreeView.hideColumn(3)
        self._fileTreeView.hideColumn(2)

        self._fileTreeView.connect(self._fileTreeView.selectionModel(),
                                   SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
                                   self.new_file_selected)

        # Image frame - displays the image currently selected in the file tree
        self._main_frame = QLabel()
        self._main_frame.setStyleSheet("background-color: black; color: red; font-size: 30pt; text-align: center")
        self._main_frame.setFixedWidth(600)
        self._main_frame.setFixedHeight(600)

        # Selection buttons - make selection of currently displayed image as A or B
        self._select_A_button = QPushButton("Select A")
        self._select_A_button.clicked.connect(self._select_A_pushed)
        self._select_B_button = QPushButton("Select B")
        self._select_B_button.clicked.connect(self._select_B_pushed)

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
        self._selection_A_frame.setFixedWidth(250)
        self._selection_A_frame.setFixedHeight(250)
        self._selection_A_frame.setText("No Image Selected")
        self._selection_A_frame.setAlignment(Qt.AlignCenter)

        self._selection_B_frame = QLabel()
        self._selection_B_frame.setStyleSheet("background-color: black; color: red; font-size: 20pt; text-align: center")
        self._selection_B_frame.setFixedWidth(250)
        self._selection_B_frame.setFixedHeight(250)
        self._selection_B_frame.setText("No Image Selected")
        self._selection_B_frame.setAlignment(Qt.AlignCenter)

        # Create layout
        hbox = QHBoxLayout()
        hbox.setSpacing(10)
        hbox.addWidget(self._fileTreeView)
        hbox.addWidget(self._main_frame)

        hbox_A = QHBoxLayout()
        hbox_A.addWidget(self._select_A_button)
        hbox_A.addWidget(self._selection_A_label)
        vbox_A = QVBoxLayout()
        vbox_A.addLayout(hbox_A)
        vbox_A.addWidget(self._selection_A_frame)
        vbox_A.addStretch(1)

        hbox_B = QHBoxLayout()
        hbox_B.addWidget(self._select_B_button)
        hbox_B.addWidget(self._selection_B_label)
        vbox_B = QVBoxLayout()
        vbox_B.addLayout(hbox_B)
        vbox_B.addWidget(self._selection_B_frame)
        vbox_B.addStretch(1)


        vbox = QVBoxLayout()
        vbox.addLayout(vbox_A)
        vbox.addLayout(vbox_B)
        #vbox.addStretch(1)

        hbox.addLayout(vbox)
        hbox.addStretch(1)

        main_widget = QWidget()
        main_widget.setLayout(hbox)
        self.setCentralWidget(main_widget)
        self.show()

    def init_menu_bar(self):
        """Create and populate the menu bar.
        """
        # Exit Application
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)

        # Match Action
        match_action = QAction(QIcon('exit.png'), '&Perform Match', self)
        match_action.setShortcut('Ctrl+M')
        match_action.setStatusTip('Perform Match')
        match_action.triggered.connect(self._perform_image_matching)

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

        match_menu = menu_bar.addMenu('&Match')
        match_menu.addAction(match_action)

    def new_file_selected(self, selected, deselected):
        filepath = self._get_selected_filepath()
        self._display_image(self._main_frame, filepath)

    def _select_A_pushed(self):
        filepath = self._get_selected_filepath()
        self._display_image(self._selection_A_frame, filepath)
        self._set_filename_label(self._selection_A_label, filepath)
        self._selection_A = filepath

    def _select_B_pushed(self):
        filepath = self._get_selected_filepath()
        self._display_image(self._selection_B_frame, filepath)
        self._set_filename_label(self._selection_B_label, filepath)
        self._selection_B = filepath

    def _get_selected_filepath(self):
        indexes = self._fileTreeView.selectedIndexes()
        if indexes:
            index = indexes[0]
            filepath = self.model.filePath(index)
            return filepath
        else:
            return None

    def _display_image(self, frame, filename):
        frame.clear()
        frame.setAlignment(Qt.AlignCenter)

        if filename is None:
            frame.setText("No Image Selected")
        elif os.path.isfile(filename):
            pixmap = QPixmap(filename)
            frame.setPixmap(pixmap.scaled(frame.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            frame.setText("Image Not Found")

    def _set_filename_label(self, label, filepath):
        if filepath and filepath != "":
            label.setText(filepath.split('/')[-1])
        else:
            label.setText("No Image Selected")

    def _perform_image_matching(self):

        if not self._selection_A or not self._selection_B:
            return
        if self._selection_A == self._selection_B:
            return

        DEBUG_MODE = True
        CONSENSUS = False  # If True, cannot display progress.

        # For the 441350000072 test set - approximate, we are assuming the well width is about 5mm
        if USE_SET_441350000072:
            # Made up but approx correct ratio for well #A1
            SET_FACTOR = 6.55
            pixel_size_A = 4.0
            pixel_size_B = pixel_size_A / SET_FACTOR
            guess = tlib.Transform(0.2,-0.9,1,0)
        else:
            # (These dimensions are for test set A.)
            pixel_size_A = pixel_size_B = 2.17217391
            guess = tlib.Transform(0.2,-0.1,1,0)

        # Read the selected images and convert to grayscale
        ref_file = self._selection_A
        trans_file = self._selection_B

        # Get greyscale versions of the selected images
        ref_gray_img = Image.from_file(ref_file, pixel_size_A).make_gray()
        mov_gray_img = Image.from_file(trans_file, pixel_size_B).make_gray()

        if DEBUG_MODE:
            print("ref pix " + str(ref_gray_img.pixel_size))
            print("mov pix " + str(mov_gray_img.pixel_size))

        # Resize the mov image so it has the same size per pixel as the ref image
        factor = mov_gray_img.pixel_size / ref_gray_img.pixel_size
        mov_gray_img = mov_gray_img.rescale(factor)

        if DEBUG_MODE:
            print("resized pix " + str(mov_gray_img.pixel_size))
            mov_gray_img.save("resized_bubble")

        # Create image matcher object to perform the matching
        matcher = ImageMatcher()
        matcher.set_debug(DEBUG_MODE)
        matcher.set_consensus(CONSENSUS)

        # Perform the matching operation to determine the transformation that maps image B to image A
        net_transform = matcher.match(ref_gray_img, mov_gray_img, guess)

        # Determine transformation in real units (um)
        image_width, image_height = ref_gray_img.size
        t = net_transform((image_width, image_height))

        pixel_size = ref_gray_img.pixel_size
        delta_x = -t[0, 2] * pixel_size
        delta_y = +t[1, 2] * pixel_size

        # Print results
        print('---\ndelta_x is', delta_x, 'µm; delta_y is', delta_y, 'µm\n---')
        print(t)
        print('===')

        '''
        if DEBUG_MODE and OUTPUT_DIRECTORY is not None:
            grain_extract = np.subtract(ref_gray_img.img, apply_tr(net_transform, mov_gray_img)) + 128
            cv2.imwrite(
                path.join(OUTPUT_DIRECTORY, 'Match_Overlay_Results.jpg'),
                grain_extract)
        '''


def main():
    app = QApplication(sys.argv)
    ex = ImageMatcherGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
