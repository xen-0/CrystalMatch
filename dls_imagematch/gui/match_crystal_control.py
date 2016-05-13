from __future__ import division

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox

from dls_imagematch.gui import RegionSelectDialog
from dls_imagematch.match import CrystalMatcher, FeatureMatchException


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
        self._img_b_region = None
        self._img_a_rect = None
        self._img_b_rect = None

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

    def match(self):
        """ Begin the matching process. """
        self._fn_begin_matching()

    def reset(self):
        self._aligned_images = None
        self._img_a_region = None
        self._img_b_region = None
        self._img_a_rect = None
        self._img_b_rect = None
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
            crystal_aligned = self._matcher.match(self._aligned_images, self._img_a_rect)
            self._display_results(crystal_aligned)
        except FeatureMatchException as e:
            QMessageBox.critical(self, "Feature Matching Error", e.message, QMessageBox.Ok)

    ''' ----------------------
    OTHER FUNCTIONS
    ------------------------'''
    def _display_image_b_marked(self):
        _, rect = self._matcher._make_image_b_region(self._aligned_images, self._img_a_rect)
        marked_img = self._aligned_images.img_b.copy()
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

    def _display_results(self, crystal_aligned):
        status = "Crystal matching complete"
        self._results_frame.display_match_results(crystal_aligned, status)

        x, y = crystal_aligned.pixel_center()
        x_um, y_um = crystal_aligned.real_center()

        beam_position = "Beam Position: x={0:.2f} um, y={1:.2f} um ({2} px, {3} px)".format(x_um, y_um, x, y)
        print(beam_position)






















