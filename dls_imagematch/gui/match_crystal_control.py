from __future__ import division

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox

from dls_imagematch.gui import RegionSelectDialog
from dls_imagematch.util import Color
from dls_imagematch.match import CrystalMatcher, CrystalMatchSet, FeatureMatchException


class CrystalMatchControl(QGroupBox):
    """ Widget that allows control of the Secondary Matching process.
    """

    def __init__(self, selector_a, selector_b, results_frame, aligner):
        super(CrystalMatchControl, self).__init__()

        self._selector_a = selector_a
        self._selector_b = selector_b
        self._results_frame = results_frame
        self._aligner = aligner

        self._matcher = CrystalMatcher()

        self._aligned_images = None

        self._img_a_region = None
        self._img_a_rect = None

        self._init_ui()
        self.setTitle("Crystal Matching")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Matching function buttons
        self._btn_region = QPushButton("Select Region")
        self._btn_region.clicked.connect(self._fn_select_region)

        self._btn_locate = QPushButton("Perform Match")
        self._btn_locate.clicked.connect(self._fn_perform_match)
        self._btn_locate.setEnabled(False)

        # Selection Image Frames
        self._frame = QLabel()
        self._frame.setStyleSheet("color: red; font-size: 20pt; text-align: center; border:1px solid black")
        self._frame.setFixedWidth(150)
        self._frame.setFixedHeight(150)
        self._frame.setAlignment(Qt.AlignCenter)

        # Create widget layout
        vbox_btns = QVBoxLayout()
        vbox_btns.addStretch(1)
        vbox_btns.addWidget(self._btn_region)
        vbox_btns.addWidget(self._btn_locate)
        vbox_btns.addStretch(1)

        hbox_btns = QHBoxLayout()
        hbox_btns.addLayout(vbox_btns)
        hbox_btns.addWidget(self._frame)
        hbox_btns.addStretch(1)

        self.setLayout(hbox_btns)

    def reset(self):
        self._aligned_images = None
        self._img_a_region = None
        self._img_a_rect = None
        self._btn_locate.setEnabled(False)

    ''' ----------------------
    BUTTON FUNCTIONS
    ------------------------'''
    def _fn_select_region(self):
        """ For a completed primary matching procedure, select a sub-region (feature) to track. """
        self.reset()
        self._aligned_images = self._aligner.last_images

        if self._aligned_images is not None:
            region_image, rect = RegionSelectDialog.get_region(self._aligned_images)
            self._img_a_region = region_image
            self._img_a_rect = rect
        else:
            QMessageBox.warning(self, "Warning", "Perform image alignment first", QMessageBox.Ok)

        if self._img_a_region is not None:
            self._display_image(self._img_a_region)
            self._display_image_b_marked()
            self._btn_locate.setEnabled(True)

    def _fn_perform_match(self):
        try:
            self._perform_match()
        except FeatureMatchException as e:
            QMessageBox.critical(self, "Feature Matching Error", e.message, QMessageBox.Ok)

    ''' ----------------------
    OTHER FUNCTIONS
    ------------------------'''
    def _perform_match(self):
        selected_img1_points = list()
        selected_img1_points.append(self._img_a_rect.center())

        match_set = CrystalMatchSet(self._aligned_images, selected_img1_points)
        self._matcher.match(match_set)

        self._display_results(match_set)

    def _display_image_b_marked(self):
        img_b = self._aligned_images.img_b
        rect = self._matcher._make_image2_region(img_b, self._aligned_images.pixel_offset(), self._img_a_rect)
        marked_img = img_b.copy()
        marked_img.draw_rectangle(rect)

        self._results_frame.display_image(marked_img)
        self._results_frame.set_status_message("Image B search region")

    def _display_image(self, image):
        """ Display the specified Image object in the frame, scaled to fit the frame and maintain aspect ratio. """
        frame_size = self._frame.size()

        # Convert to a QT pixmap and display
        pixmap = image.to_qt_pixmap()
        scaled = pixmap.scaled(frame_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._frame.setPixmap(scaled)

    def _display_results(self, crystal_match_set):
        status = "Crystal matching complete"

        self._results_frame.clear()
        self._results_frame.set_status_message(status)

        img1 = crystal_match_set.img1().copy()
        img2 = crystal_match_set.img2().copy()

        print(status)
        for i, match in enumerate(crystal_match_set.matches):

            pixel1, real1 = match.img1_point(), match.img1_point_real()
            pixel2, real2 = match.img2_point(), match.img2_point_real()

            beam_position = "Beam Position: x={0:.2f} um, " \
                            "y={1:.2f} um ({2} px, {3} px)".format(real2.x, real2.y, pixel2.x, pixel2.y)

            delta_pixel = pixel2 - pixel1 - crystal_match_set.pixel_offset()
            delta_real = real2 - real1 - crystal_match_set.real_offset()
            delta = "Crystal Movement: x={0:.2f} um, y={1:.2f} um ({2} px, " \
                    "{3} px)".format(delta_real.x, delta_real.y, delta_pixel.x, delta_pixel.y)

            print("-- Match {} --".format(i))
            print(beam_position)
            print(delta)

            px2 = match.img1_point() - match._transformation.translation().to_point()
            off = crystal_match_set.pixel_offset()
            img1.draw_cross(pixel1, Color.Red(), size=10, thickness=2)
            img1.draw_cross(px2+off, Color.Blue(), size=10, thickness=2)
            img1.draw_cross(pixel2+off, Color.Green(), size=10, thickness=2)
            img1.draw_circle(pixel2+off, 30, Color.Green())

            img2.draw_cross(pixel1-off, Color.Red(), size=10, thickness=2)
            img2.draw_cross(pixel2, Color.Green(), size=10, thickness=2)
            img2.draw_cross(px2, Color.Blue(), size=10, thickness=2)


        img1.popup()
        img2.popup()























