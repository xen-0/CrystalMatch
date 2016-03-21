import os
import sys

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

USE_SET_441350000072 = True


class ImageMatcherGui(QMainWindow):
    def __init__(self):
        super(ImageMatcherGui, self).__init__()

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

        # Select and Display the default images
        filepath = INPUT_DIR_ROOT + "old/translate-test-B/1_1.png"
        if USE_SET_441350000072:
            filepath = INPUT_DIR_ROOT + "441350000072/A01_13.jpg"
        self._display_image(self._selection_A_frame, filepath)
        self._set_filename_label(self._selection_A_label, filepath)
        self._selection_A = filepath

        filepath = INPUT_DIR_ROOT + "old/translate-test-B/1_2_cropped.png"
        if USE_SET_441350000072:
            filepath = INPUT_DIR_ROOT + "441350000072_OAVS/_1_A1.png"
        self._display_image(self._selection_B_frame, filepath)
        self._set_filename_label(self._selection_B_label, filepath)
        self._selection_B = filepath

        '''
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
        '''


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

        # Selection buttons - make selection of currently displayed image as A or B
        self._select_A_button = QPushButton("Select Reference Image")
        self._select_A_button.clicked.connect(self._select_A_pushed)
        self._select_B_button = QPushButton("Select Matching Image")
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

        self.begin_match_button = QPushButton("Begin Match")
        self.begin_match_button.clicked.connect(self._primary_image_matching)
        self.next_frame_button = QPushButton("Next Frame >>")
        self.next_frame_button.clicked.connect(self._next_frame_pushed)
        self.next_scale_button = QPushButton("Next Scale >>")
        self.next_scale_button.clicked.connect(self._next_scale_pushed)
        self.end_match_button = QPushButton("Skip To End >>")
        self.end_match_button.clicked.connect(self._skip_to_end_pushed)
        self.region_select_button = QPushButton("Select Region")
        self.region_select_button.clicked.connect(self._select_region_pushed)
        self.region_select_button.setEnabled(False)

        self.next_frame_button.setEnabled(False)
        self.next_scale_button.setEnabled(False)
        self.end_match_button.setEnabled(False)
        self.region_select_button.setEnabled(False)

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

        vbox = QVBoxLayout()
        vbox.addLayout(vbox_A)
        vbox.addLayout(vbox_B)
        vbox.addStretch(1)

        vbox_buttons = QVBoxLayout()
        vbox_buttons.addStretch(1)
        vbox_buttons.addWidget(self.begin_match_button)
        vbox_buttons.addWidget(self.next_frame_button)
        vbox_buttons.addWidget(self.next_scale_button)
        vbox_buttons.addWidget(self.end_match_button)
        vbox_buttons.addWidget(self.region_select_button)
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
        match_action.triggered.connect(self._primary_image_matching)

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

        match_menu = menu_bar.addMenu('&Match')
        match_menu.addAction(match_action)

    def new_file_selected(self, selected, deselected):
        filepath = self._get_selected_filepath()
        self._display_image(self._result_frame, filepath)

    def _select_A_pushed(self):
        filepath = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', INPUT_DIR_ROOT))
        if filepath:
            self._display_image(self._selection_A_frame, filepath)
            self._set_filename_label(self._selection_A_label, filepath)
            self._selection_A = filepath

    def _select_B_pushed(self):
        filepath = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', INPUT_DIR_ROOT))
        if filepath:
            self._display_image(self._selection_B_frame, filepath)
            self._set_filename_label(self._selection_B_label, filepath)
            self._selection_B = filepath

    def _next_frame_pushed(self):
        if self._region_matcher is not None:
            self._region_matcher.next_frame()
            self._display_match_results()

    def _next_scale_pushed(self):
        if self._region_matcher is not None:
            self._region_matcher.skip_to_next_scale()
            self._display_match_results()

    def _skip_to_end_pushed(self):
        if self._region_matcher is not None:
            self._region_matcher.skip_to_end()
            self._display_match_results()

    def _select_region_pushed(self):
        filename = self._selection_A

        region_image, roi = RegionSelectDialog.get_region(self, filename)

        if region_image is not None:
            imgA = Image.from_file(self._selection_B, region_image.pixel_size)
            imgA = imgA.rescale(self.mov_img_scale_factor)
            self._secondary_image_matching(imgA, region_image, roi)

    def _display_match_results(self):
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

            '''
            if DEBUG_MODE and OUTPUT_DIRECTORY is not None:
                grain_extract = np.subtract(ref_gray_img.img, apply_tr(net_transform, mov_gray_img)) + 128
                cv2.imwrite(
                    path.join(OUTPUT_DIRECTORY, 'Match_Overlay_Results.jpg'),
                    grain_extract)
            '''

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

    def _primary_image_matching(self):
        if not self._selection_A or not self._selection_B:
            return
        if self._selection_A == self._selection_B:
            return

        DEBUG_MODE = False

        # For the 441350000072 test set - approximate, we are assuming the well width is about 5mm
        if USE_SET_441350000072:
            # Made up but approx correct ratio for well #A1
            SET_FACTOR = 6.55
            pixel_size_A = 4.0
            pixel_size_B = pixel_size_A / SET_FACTOR
            #guess = tlib.Transform(0.2,-0.9,1,0)
            guess_x = 0.1
            guess_y = 0.4
        else:
            # (These dimensions are for test set A.)
            pixel_size_A = pixel_size_B = 2.17217391
            #guess = tlib.Transform(0.2,-0.1,1,0)
            guess_x = 0.2
            guess_y = 0.1

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
        self.mov_img_scale_factor = factor

        if DEBUG_MODE:
            print("resized pix " + str(mov_gray_img.pixel_size))
            mov_gray_img.save("resized_bubble")

        # Perform the matching operation to determine the transformation that maps image B to image A
        guess = Translate(guess_x*ref_gray_img.size[0], guess_y*ref_gray_img.size[1]); print(guess.x, guess.y)
        self._region_matcher = RegionMatcher(ref_gray_img, mov_gray_img, guess)
        self._next_frame_pushed()

        self.next_frame_button.setEnabled(True)
        self.next_scale_button.setEnabled(True)
        self.end_match_button.setEnabled(True)
        self.region_select_button.setEnabled(True)

    def _secondary_image_matching(self, imgA, imgB, roi):
        imgA_gray = imgA.make_gray()
        imgB_gray = imgB.make_gray()

        primary_transform = self._region_matcher.net_transform
        guessX = roi[0] - primary_transform.x
        guessY = roi[1] - primary_transform.y
        guess = Translate(guessX-5, guessY-5)


        self._region_matcher = RegionMatcher(imgA_gray, imgB_gray, guess, scales=(1,))
        self._next_frame_pushed()

    def _get_441350000072_files(self, row, col):
        mov_filepath = INPUT_DIR_ROOT + "441350000072_OAVS/_1_" + row + str(col) + ".png"

        if col < 10:
            col = '0' + str(col)

        ref_filepath = INPUT_DIR_ROOT + "441350000072/" + row + str(col) + "_13.jpg"

        return ref_filepath, mov_filepath


def main():
    app = QApplication(sys.argv)
    ex = ImageMatcherGui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
