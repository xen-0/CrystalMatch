import cv2
import numpy as np

OUTPUT_DIRECTORY = "../test-output/"


class Image:
    def __init__(self, img, real_width):
        self.img = img

        # The size of the image in number of pixels
        self.size = self._size()

        # The real size represented by a single pixel in the image
        self.pixel_size = real_width / self.size[0]

        # The real size represented by the image
        real_height = self.size[1] / self.pixel_size
        self.real_size = (real_width, real_height)



    def save(self, filename):
        cv2.imwrite(OUTPUT_DIRECTORY + filename + ".png", self.img)

    def make_gray(self):
        """ Return a greyscale version of the image
        """
        if len(self.img.shape) in (3, 4):
            gray_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            return Image(gray_img, self.real_size[0])
        else:
            return Image(self.img, self.real_size[0])

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

        return Image(grain_extract, self.real_size[0])

    def rescale(self, factor):
        """ Return a new Image that is a version of this image, resized to the specified scale
        """
        scaled_size = (int(self.size[0] * factor), int(self.size[1] * factor))
        return self.resize(scaled_size)


    def resize(self, new_size):
        """ Return a new Image that is a resized version of this one
        """
        resized_img = cv2.resize(self.img, new_size)
        return Image(resized_img, self.real_size[0])


    def _size(self):
        """Return the size of an image in pixels in the format [width, height].
        """
        if self.img.ndim == 3:  # Colour
            working_size = self.img.shape[::-1][1:3]
        else:
            assert self.img.ndim == 2  # Greyscale
            working_size = self.img.shape[::-1]
        return working_size


    @staticmethod
    def from_file(filename, real_size):
        img = cv2.imread(filename)
        return Image(img, real_size)