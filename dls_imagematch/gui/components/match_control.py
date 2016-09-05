from __future__ import division

from PyQt4 import QtCore
from PyQt4.QtCore import Qt, QThread
from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox

from dls_imagematch.crystal import CrystalMatcher
from dls_imagematch.util import Rectangle
from .progress_dialog import ProgressDialog
from feature.detector import DetectorConfig
from ..crystal import PointSelectDialog
from ..crystal import SingleCrystalDialog


class CrystalMatchControl(QGroupBox):
    """ Widget that allows control of the Secondary Matching process.
    """

    NUM_FRAMES = 10
    FRAME_SIZE = 75

    FRAME_STYLE = "color: {0}; font-size: 16pt; text-align: center; border:1px solid {0};"

    def __init__(self, results_frame, gui_config, crystal_config):
        super(CrystalMatchControl, self).__init__()

        self._results_frame = results_frame

        self._match_results = None

        self._aligned_images = None
        self._selected_points = []

        self._gui_config = gui_config
        self._crystal_config = crystal_config

        self._init_ui()
        self._clear_all_frames()
        self.setTitle("Crystal Matching")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Matching function buttons
        self._btn_region = QPushButton("Select")
        self._btn_region.setFixedHeight(self.FRAME_SIZE)
        self._btn_region.clicked.connect(self._fn_select_points)

        self._btn_locate = QPushButton("Match")
        self._btn_locate.setFixedHeight(self.FRAME_SIZE)
        self._btn_locate.clicked.connect(self._fn_perform_match)
        self._btn_locate.setEnabled(False)

        # Selection Image Frames
        self._frames1 = []
        self._frames2 = []
        hbox_frames1 = QHBoxLayout()
        hbox_frames2 = QHBoxLayout()
        for i in range(self.NUM_FRAMES):
            frame1 = self._ui_make_image_frame()
            frame2 = self._ui_make_image_frame()
            self._frames1.append(frame1)
            hbox_frames1.addWidget(frame1)
            self._frames2.append(frame2)
            hbox_frames2.addWidget(frame2)

        # Display matches buttons
        self._show_matches_btns = []
        hbox_show_btns = QHBoxLayout()
        for i in range(self.NUM_FRAMES):
            btn = self._ui_make_show_matches_button(i)
            self._show_matches_btns.append(btn)
            hbox_show_btns.addWidget(btn)

        # Create widget layout
        vbox_btns = QVBoxLayout()
        vbox_btns.addWidget(self._btn_region)
        vbox_btns.addWidget(self._btn_locate)
        vbox_btns.addStretch(1)

        vbox_frames = QVBoxLayout()
        vbox_frames.addLayout(hbox_frames1)
        vbox_frames.addLayout(hbox_frames2)
        vbox_frames.addLayout(hbox_show_btns)

        hbox_btns = QHBoxLayout()
        hbox_btns.addLayout(vbox_btns)
        hbox_btns.addLayout(vbox_frames)
        hbox_btns.addStretch(1)

        self.setLayout(hbox_btns)

    def _ui_make_image_frame(self):
        frame = QLabel()
        frame.setStyleSheet(self.FRAME_STYLE.format("black"))
        frame.setFixedWidth(self.FRAME_SIZE)
        frame.setFixedHeight(self.FRAME_SIZE)
        frame.setAlignment(Qt.AlignCenter)
        return frame

    def _ui_make_show_matches_button(self, i):
        btn = QPushButton("Matches")
        btn.setFixedWidth(self.FRAME_SIZE)
        btn.clicked.connect(lambda: self._show_matches_dialog(i))
        return btn

    def reset(self):
        self._aligned_images = None
        self._match_results = None
        self._selected_points = []
        self._btn_locate.setEnabled(False)
        self._clear_all_frames()

    def set_aligned_images(self, aligned_images):
        self.reset()
        self._aligned_images = aligned_images

    ''' ----------------------
    BUTTON FUNCTIONS
    ------------------------'''
    def _fn_select_points(self):
        """ For a completed primary matching procedure, select a sub-region (feature) to track. """
        if self._aligned_images is None:
            self._show_perform_alignment_message()
            return

        result_ok, points = self._get_points_from_user_selection()
        if result_ok:
            self._set_selected_points(points)

    def _show_perform_alignment_message(self):
        QMessageBox.warning(self, "Warning", "Perform image alignment first", QMessageBox.Ok)

    def _get_points_from_user_selection(self):
        """ Display a dialog and return the result to the caller. """
        max_points = self.NUM_FRAMES
        size = self._crystal_config.region_size.value()
        color = self._gui_config.color_crystal_img1.value()
        dialog = PointSelectDialog(self, self._aligned_images, max_points, size, color)
        result_ok = dialog.exec_()

        points = []
        if result_ok:
            points = dialog.selected_points()
        return result_ok, points

    def _set_selected_points(self, points):
        self._selected_points = points
        self._clear_all_frames()
        self._display_image1_regions()
        self._display_marked_img2()
        self._btn_locate.setEnabled(True)

    def _fn_perform_match(self):
        selected_img1_points = self._selected_points
        self._perform_matching_task(selected_img1_points)

    def _perform_matching_task(self, selected_points):
        matcher = self._create_crystal_matcher()

        progress = ProgressDialog("Crystal Matching In Progress")
        match_task = _MatchTaskThread(matcher, selected_points)
        match_task.task_finished.connect(progress.on_finished)
        match_task.task_results.connect(self._display_results)
        match_task.start()
        progress.exec_()

    def _create_crystal_matcher(self):
        detector_config_dir = self._gui_config.config_dir.value()
        detector_config = DetectorConfig(detector_config_dir)

        matcher = CrystalMatcher(self._aligned_images, detector_config)
        matcher.set_from_crystal_config(self._crystal_config)
        return matcher

    ''' ----------------------
    SMALL IMAGE FUNCTIONS
    ------------------------'''
    def _clear_all_frames(self):
        color1 = self._gui_config.color_crystal_img1.value().to_hex()
        color2 = self._gui_config.color_crystal_img2.value().to_hex()
        for i in range(self.NUM_FRAMES):
            self._clear_frame(self._frames1[i], i, color1)
            self._clear_frame(self._frames2[i], i, color2)

    def _clear_frame(self, frame, number, color_hex):
        frame.clear()
        frame.setText(str(number + 1))
        frame.setStyleSheet(self.FRAME_STYLE.format(color_hex))

    def _display_image1_regions(self):
        img1 = self._aligned_images.img1
        region_size = self._crystal_config.region_size.value()
        color = self._gui_config.color_crystal_img1.value()

        for i, point in enumerate(self._selected_points):
            if i >= self.NUM_FRAMES:
                break

            rect = Rectangle.from_center(point, region_size, region_size)
            img = img1.crop(rect).resize((self.FRAME_SIZE, self.FRAME_SIZE))
            img.draw_cross(img.bounds().center(), color, thickness=1)
            self._display_image_in_frame(img, 1, i)

    def _display_image_in_frame(self, image, row, frame_number):
        """ Display the specified Image object in the frame, scaled to fit the frame and maintain aspect ratio. """
        if row == 1:
            frame = self._frames1[frame_number]
        else:
            frame = self._frames2[frame_number]

        pixmap = image.to_qt_pixmap(frame.size())
        frame.setPixmap(pixmap)

    def _show_matches_dialog(self, index):
        if self._aligned_images is None:
            self._show_perform_alignment_message()
            return

        if self._match_results is None or self._match_results.num() <= index:
            point = None
        else:
            point = self._match_results.get_crystal_match(index).img1_point()

        dialog = SingleCrystalDialog(self._aligned_images, point, self._gui_config, self._crystal_config)
        dialog.exec_()

    ''' ----------------------
    DISPLAY RESULTS FUNCTIONS
    ------------------------'''
    def _display_marked_img2(self):
        img2 = self._aligned_images.img2.copy()
        color = self._gui_config.color_search.value()

        matcher = self._create_crystal_matcher()

        for point in self._selected_points:
            img2_rect = matcher.make_search_region(point)
            img2.draw_rectangle(img2_rect, color)

        status = "Ready for Crystal Matching"
        self._results_frame.clear()
        self._results_frame.set_status_message(status)
        self._results_frame.display_image(img2)

    def _display_results(self, crystal_match_set):
        self._match_results = crystal_match_set
        status = "Crystal matching complete"

        self._results_frame.clear()
        self._results_frame.set_status_message(status)

        img1 = crystal_match_set.img1().copy()
        img2 = crystal_match_set.img2().copy()

        region_size = self._crystal_config.region_size.value()

        color1 = self._gui_config.color_crystal_img1.value()
        color2 = self._gui_config.color_crystal_img2.value()

        print(status)
        for i, match in enumerate(crystal_match_set.matches):
            if not match.is_match_found():
                continue

            pixel1, real1 = match.img1_point(), match.img1_point_real()
            pixel2, real2 = match.img2_point(), match.img2_point_real()

            beam_position = "Beam Position: x={0:.2f} um, y={1:.2f} um ({2} px, " \
                            "{3} px)".format(real2.x, real2.y, int(round(pixel2.x)), int(round(pixel2.y)))

            delta_pixel = pixel2 - pixel1 + crystal_match_set.pixel_offset()
            delta_real = real2 - real1 + crystal_match_set.real_offset()
            delta = "Crystal Movement: x={0:.2f} um, y={1:.2f} um ({2} px, " \
                    "{3} px)".format(delta_real.x, delta_real.y, int(round(delta_pixel.x)), int(round(delta_pixel.y)))

            print("-- Match {} --".format(i))
            print(beam_position)
            print(delta)

            off = crystal_match_set.pixel_offset()
            img1.draw_cross(pixel1, color1, size=10, thickness=2)
            img1.draw_cross(pixel2+off, color2, size=10, thickness=2)
            img1.draw_circle(pixel2+off, 30, color2)

            img2.draw_cross(pixel1-off, color1, size=10, thickness=2)
            img2.draw_cross(pixel2, color2, size=10, thickness=2)

            if i < self.NUM_FRAMES:
                rect = Rectangle.from_center(pixel2, region_size, region_size)
                img = crystal_match_set.img2().crop(rect).resize((self.FRAME_SIZE, self.FRAME_SIZE))
                img.draw_cross(img.bounds().center(), color=color2, thickness=1)
                self._display_image_in_frame(img, 2, i)

        self._results_frame.display_image(img2)


class _MatchTaskThread(QThread):
    task_finished = QtCore.pyqtSignal()
    task_results = QtCore.pyqtSignal(object)

    def __init__(self, matcher, selected_points):
        super(_MatchTaskThread, self).__init__()
        self._matcher = matcher
        self._selected_points = selected_points

    def run(self):
        match_results = self._matcher.match(self._selected_points)
        self.task_finished.emit()
        self.task_results.emit(match_results)
