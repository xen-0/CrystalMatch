from __future__ import division

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox

from dls_imagematch.gui import PointSelectDialog
from dls_imagematch.util import Color, Rectangle
from dls_imagematch.match import CrystalMatcher, CrystalMatchSet, FeatureMatchException


class CrystalMatchControl(QGroupBox):
    """ Widget that allows control of the Secondary Matching process.
    """

    NUM_FRAMES = 10
    FRAME_SIZE = 75

    def __init__(self, selector_a, selector_b, results_frame, aligner, config):
        super(CrystalMatchControl, self).__init__()

        self._selector_a = selector_a
        self._selector_b = selector_b
        self._results_frame = results_frame
        self._aligner = aligner

        self._matcher = CrystalMatcher(config)

        self._aligned_images = None
        self._selected_points = []

        self._config = config

        self._init_ui()
        self.setTitle("Crystal Matching")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Matching function buttons
        self._btn_region = QPushButton("Select Region")
        self._btn_region.clicked.connect(self._fn_select_points)

        self._btn_locate = QPushButton("Perform Match")
        self._btn_locate.clicked.connect(self._fn_perform_match)
        self._btn_locate.setEnabled(False)

        # Selection Image Frames
        self._frames = []
        hbox_frames = QHBoxLayout()
        for i in range(self.NUM_FRAMES):
            frame = QLabel()
            frame.setStyleSheet("color: red; font-size: 20pt; text-align: center; border:1px solid black")
            frame.setFixedWidth(self.FRAME_SIZE)
            frame.setFixedHeight(self.FRAME_SIZE)
            frame.setAlignment(Qt.AlignCenter)
            self._frames.append(frame)
            hbox_frames.addWidget(frame)

        # Create widget layout
        vbox_btns = QVBoxLayout()
        vbox_btns.addStretch(1)
        vbox_btns.addWidget(self._btn_region)
        vbox_btns.addWidget(self._btn_locate)
        vbox_btns.addStretch(1)

        hbox_btns = QHBoxLayout()
        hbox_btns.addLayout(vbox_btns)
        hbox_btns.addLayout(hbox_frames)
        hbox_btns.addStretch(1)

        self.setLayout(hbox_btns)

    def reset(self):
        self._aligned_images = None
        self._selected_points = []
        self._btn_locate.setEnabled(False)

    ''' ----------------------
    BUTTON FUNCTIONS
    ------------------------'''
    def _fn_select_points(self):
        """ For a completed primary matching procedure, select a sub-region (feature) to track. """
        self.reset()
        self._aligned_images = self._aligner.last_images

        if self._aligned_images is not None:
            self._selected_points = PointSelectDialog.get_points(self._aligned_images, self._config)
        else:
            QMessageBox.warning(self, "Warning", "Perform image alignment first", QMessageBox.Ok)

        if len(self._selected_points) > 0:
            self._clear_images()
            self._display_image_regions()
            self._display_marked_img2()
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
        selected_img1_points = self._selected_points
        region_size = self._config.region_size

        match_set = CrystalMatchSet(self._aligned_images, selected_img1_points)
        self._matcher.match(match_set, region_size)

        self._display_results(match_set)

    def _display_image_regions(self):
        img1 = self._aligned_images.img1
        region_size = self._config.region_size

        for i, point in enumerate(self._selected_points):
            if i >= self.NUM_FRAMES:
                break

            rect = Rectangle.from_center(point, region_size, region_size)
            img = img1.crop(rect).resize((self.FRAME_SIZE, self.FRAME_SIZE))
            img.draw_cross(img.bounds().center(), color=Color.Green(), thickness=1)
            self._display_image(img, i)

    def _display_image(self, image, frame_number):
        """ Display the specified Image object in the frame, scaled to fit the frame and maintain aspect ratio. """
        frame = self._frames[frame_number]
        frame_size = frame.size()

        # Convert to a QT pixmap and display
        pixmap = image.to_qt_pixmap()
        scaled = pixmap.scaled(frame_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        frame.setPixmap(scaled)

    def _clear_images(self):
        for i in range(self.NUM_FRAMES):
            self._frames[i].clear()

    def _display_marked_img2(self):
        match_set = CrystalMatchSet(self._aligned_images, self._selected_points)
        region_size = self._config.region_size
        img2 = match_set.img2().copy()

        for crystal_match in match_set.matches:
            img1_rect = crystal_match.img1_region(region_size)
            img2_rect = self._matcher.make_image2_region(match_set.img2(),
                                                match_set.pixel_offset(), img1_rect)

            img2.draw_rectangle(img2_rect, color=Color.Orange())

        status = "Ready for Crystal Matching"
        self._results_frame.clear()
        self._results_frame.set_status_message(status)
        self._results_frame.display_image(img2)

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























