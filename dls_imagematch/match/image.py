from __future__ import division
import cv2
from PyQt4.QtGui import QImage, QPixmap
import numpy as np

OUTPUT_DIRECTORY = "../test-output/"


class Image:
    def __init__(self, img, pixel_size):
        self.img = img

        # The size of the image in number of pixels
        self.size = self._size()

        # The real size represented by a single pixel in the image
        self.pixel_size = pixel_size

        # The real size represented by the image
        self.real_size = (self.size[0] * self.pixel_size, self.size[1] * self.pixel_size)

    def save(self, filename):
        cv2.imwrite(OUTPUT_DIRECTORY + filename + ".png", self.img)

    def popup(self):
        """Pop up a window to display an image until a key is pressed (blocking)."""
        cv2.imshow('dbg', self.img)
        cv2.waitKey(0)

    def copy(self):
        """ Return an Image object which is a deep copy of this one.
        """
        return Image(self.img.copy(), self.pixel_size)

    def sub_image(self, roi):
        x1, y1, x2, y2 = roi[0], roi[1], roi[2], roi[3]
        sub = self.img[y1:y2, x1:x2]
        return Image(sub,self.pixel_size)

    def to_qt_pixmap(self):
        width, height = self.size
        bytesPerLine = 3 *width
        qImg = QImage(self.img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        return QPixmap.fromImage( qImg )

    def make_gray(self):
        """ Return a greyscale version of the image
        """
        if len(self.img.shape) in (3, 4):
            gray_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            return Image(gray_img, self.pixel_size)
        else:
            return Image(self.img, self.pixel_size)

    def make_color(self):
        """Convert the image into a 3 channel BGR image
        """
        color = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
        return Image(img=color, pixel_size=self.pixel_size)


    def freq_range(self, coarseness_range, scale_factor):
        """Copy an image, discarding all but a range of frequency components.

        E.g. for a coarseness range of (1, 50), only features with sizes between 1
        and 50 pixels are retained (providing `working_size_factor == 1`).

        `1.0/working_size_factor` is used as a prefactor to the coarseness range
        bounds. This is useful for the purposes of the implementation of
        `find_tr()`. (A full-sized `img` should be passed in, regardless of whether
        `working_size_factor == 1`.)
        """
        (c_lo, c_hi) = coarseness_range
        lower = int(c_lo/scale_factor)
        upper = int(c_hi/scale_factor)

        a = cv2.blur(self.img, (lower, lower))
        b = cv2.blur(self.img, (upper, upper))

        grain_extract = np.subtract(a, b) + 128

        return Image(grain_extract, self.pixel_size)

    def rescale(self, factor):
        """ Return a new Image that is a version of this image, resized to the specified scale
        """
        scaled_size = (int(self.size[0] * factor), int(self.size[1] * factor))
        resized_img = cv2.resize(self.img, scaled_size)

        # Because the image must be an integer number of pixels, we must corect the
        # factor to calculate the pixel size properly.
        corrected_factor = scaled_size[0] / self.size[0]
        pixel_size = self.pixel_size / corrected_factor
        return Image(resized_img, pixel_size)

    '''
    def resize(self, new_size):
        """ Return a new Image that is a resized version of this one
        """
        resized_img = cv2.resize(self.img, new_size)
        return Image(resized_img, self.pixel_size)
    '''

    def draw_rectangle(self, roi, thickness=1):
        """ Draw the specified rectangle on the image (in place) """
        top_left = (int(roi[0]), int(roi[1]))
        bottom_right = (int(roi[2]), int(roi[3]))
        color = (0,0,0,255)
        cv2.rectangle(self.img, top_left, bottom_right, color, thickness=thickness)


    def _size(self):
        """Return the size of an image in pixels in the format [width, height].
        """
        if self.img.ndim == 3:  # Colour
            working_size = self.img.shape[::-1][1:3]
        else:
            assert self.img.ndim == 2  # Greyscale
            working_size = self.img.shape[::-1]
        return working_size

    def paste(self, src, xOff, yOff):
        """ Paste the source image onto the target one at the specified position.
        If any of the source is outside the bounds of this image, it will be
        lost.
        """
        xOff, yOff = int(xOff), int(yOff)

        # Overlap rectangle in target image coordinates
        width, height = src.size[0], src.size[1]
        x1 = max(xOff, 0)
        y1 = max(yOff, 0)
        x2 = min(xOff+width, self.size[0])
        y2 = min(yOff+height, self.size[1])

        # Paste location is totally outside image
        if x1 > x2 or y1 > y2:
            return

        # Overlap rectangle in source image coordinates
        sx1 = x1 - xOff
        sy1 = y1 - yOff
        sx2 = x2 - xOff
        sy2 = y2 - yOff

        # Perform paste
        target = self.img
        source = src.img

        target[y1:y2, x1:x2] = source[sy1:sy2, sx1:sx2]

    def apply_tr(self, transform):
        """Apply an affine transform to an image and return the result.

        `transform` can be an affine transform matrix or a Transform object.
        `img` can be colour or greyscale.

        This function is expensive and its use should be avoided if possible.
        """
        working_size = self.size

        if hasattr(transform, '__call__'):  # We need a matrix.
            transform = transform(working_size)

        return cv2.warpAffine(self.img, transform, working_size)

    @staticmethod
    def from_file(filename, pixel_size):
        img = cv2.imread(filename)
        return Image(img, pixel_size)


