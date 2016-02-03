import cv2
import numpy as np

OUTPUT_DIRECTORY = "../test-output/"

class Image:
    def __init__(self, img):
        self.img = img

    def D_SAVE(self, filename):
        cv2.imwrite(OUTPUT_DIRECTORY + filename + ".png", self.img)

    def pick_frequency_range(self, coarseness_range, scale_factor):
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

        return Image(grain_extract)

    def resize(self, new_size):
        resized_img = cv2.resize(self.img, new_size)
        return Image(resized_img)


    def size(self):
        """Return the size of an image in pixels in the format [width, height]."""
        if self.img.ndim == 3:  # Colour
            working_size = self.img.shape[::-1][1:3]
        else:
            assert self.img.ndim == 2  # Greyscale
            working_size = self.img.shape[::-1]
        return working_size