from __future__ import division

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPushButton, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox

from dls_imagematch.gui import RegionSelectDialog
from dls_imagematch.match import FeatureMatcher, FeatureMatchException
from dls_imagematch.match import AlignedImages
from dls_imagematch.util import Translate


class CrystalMatchControl(QGroupBox):
    """ Widget that allows control of the Secondary Matching process.
    """

    def __init__(self, selector_a, selector_b, results_frame, aligner):
        super(CrystalMatchControl, self).__init__()

        self._selector_a = selector_a
        self._selector_b = selector_b
        self._results_frame = results_frame
        self._aligner = aligner

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
            region_image, roi = RegionSelectDialog.get_region(self._aligned_images)
            self._img_a_region = region_image
            self._img_a_rect = roi
        else:
            QMessageBox.warning(self, "Warning", "Perform image alignment first", QMessageBox.Ok)

        if self._img_a_region is not None:
            self._display_image(self._img_a_region)
            self._make_image_b_region()
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
        crystal_img_a = self._img_a_region
        crystal_img_b = self._img_b_region
        crystal_img_a_gray = crystal_img_a.make_gray()
        crystal_img_b_gray = crystal_img_b.make_gray()

        method = "Consensus"
        adapt = 'Pyramid'

        FeatureMatcher.POPUP_RESULTS = True
        matcher = FeatureMatcher(crystal_img_b_gray, crystal_img_a_gray)
        matcher.match(method, adapt)

        crystal_translate = matcher.net_transform
        status = "Crystal matching complete"
        position = Translate(self._img_b_rect[0], self._img_b_rect[1])
        position = position.offset(crystal_translate)

        img_b = self._aligned_images.img_b
        aligned = AlignedImages(img_b, crystal_img_a, position)
        self._results_frame.display_match_results(aligned, status)

    def _display_image(self, image):
        """ Display the specified Image object in the frame, scaled to fit the frame and maintain aspect ratio. """
        frame_size = self._frame.size()

        # Convert to a QT pixmap and display
        pixmap = image.to_qt_pixmap()
        scaled = pixmap.scaled(frame_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._frame.setPixmap(scaled)

    def _make_image_b_region(self):
        align_offset = self._aligned_images.pixel_offset()
        img_b = self._aligned_images.img_b
        roi_a = self._img_a_rect

        # Find the center of the rectangle in image A
        center_a = (roi_a[2]+roi_a[0])/2, (roi_a[3]+roi_a[1])/2

        # Convert the center to Image B coordinates
        center_b = center_a[0] - align_offset[0], center_a[1] - align_offset[1]

        # Determine size (in pixels) of the search box in image B
        SEARCH_WIDTH = 200
        SEARCH_HEIGHT = 400
        width = SEARCH_WIDTH / img_b.pixel_size
        height = SEARCH_HEIGHT / img_b.pixel_size

        # Create a rectangle area of image B
        # Its tall because crystal likely to move downwards under gravity
        x1 = center_b[0] - (width / 2.0)
        y1 = center_b[1] - (width / 2.0)
        x2 = x1 + width
        y2 = y1 + height

        x1, y1 = max(x1, 0), max(y1, 0)
        x2, y2 = min(x2, img_b.size[0]), min(y2, img_b.size[1])
        rect = (x1, y1, x2, y2)

        region = img_b.sub_image(rect)
        self._img_b_region = region
        self._img_b_rect = rect

        marked_img = img_b.copy()
        marked_img.draw_rectangle(rect)

        self._results_frame.display_image(marked_img)
        self._results_frame.set_status_message("Image B search region")





















