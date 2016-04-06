from __future__ import division

from PyQt4.QtGui import (QPushButton, QGroupBox, QHBoxLayout, QMessageBox)

from dls_imagematch.match import FeatureMatcher, Overlayer


class FeatureMatchControl(QGroupBox):
    """ Widget that allows control of the Feature Matching process.
    """
    def __init__(self, selector_a, selector_b, image_frame):
        super(FeatureMatchControl, self).__init__()

        self.selector_a = selector_a
        self.selector_b = selector_b
        self.image_frame = image_frame

        self._init_ui()

        self.matcher = None

        self.setTitle("Feature Matching")

    def _init_ui(self):
        """ Create all the display elements of the widget. """
        # Matching function buttons
        self.btn_begin = QPushButton("Begin Match")
        self.btn_begin.clicked.connect(self._fn_begin_matching)

        # Create widget layout
        hbox_btns = QHBoxLayout()
        hbox_btns.addWidget(self.btn_begin)
        hbox_btns.addStretch(1)

        self.setLayout(hbox_btns)

    def match(self):
        self._fn_begin_matching()

    def _fn_begin_matching(self):
        """ Being the feature matching process for the two selected images. """
        img_a, img_b = self._prepare_images()
        self.matcher = FeatureMatcher(img_a, img_b)
        try:
            self.matcher.perform_match()
            self._display_results()
        except AttributeError as e:
            msg = "Under Windows, this function only works correctly under OpenCV v2 (with Python 2.7) " \
                  "and not under OpenCV v3. This is a widely known and reported problem but it doesn't " \
                  "seem to have been fixed yet. Install Python 2.7 with OpenCV 2.4 and try again."
            QMessageBox.critical(self, "OpenCV Error", msg, QMessageBox.Ok)

    def _prepare_images(self):
        """ Load the selected images to be matched, scale them appropriately and
        convert to grayscale. """
        # Get the selected images
        self.img_a = self.selector_a.image()
        self.img_b = self.selector_b.image()

        # Resize the image B so it has the same size per pixel as image A
        factor = self.img_b.pixel_size / self.img_a.pixel_size
        self.img_b = self.img_b.rescale(factor)

        return self.img_a.make_gray(), self.img_b.make_gray()

    def _display_results(self):
        """ Display the results of the matching process (display overlaid image
        and print the offset. """
        transform = self.matcher.net_transform

        # Create image of B overlaid on A
        img = Overlayer.create_overlay_image(self.img_a, self.img_b, transform)
        self.image_frame.display_image(img)

        # Determine transformation in real units (um)
        x, y = transform.x, transform.y

        pixel_size = self.img_a.pixel_size
        delta_x = "{0:.2f}".format(x * pixel_size)
        delta_y = "{0:.2f}".format(y * pixel_size)

        # Print results
        print("Image offset: x=" + str(delta_x) + " um (" + str(int(x)) + " pixels), y="
              + str(delta_y) + " um (" + str(int(y)) + " pixels)")