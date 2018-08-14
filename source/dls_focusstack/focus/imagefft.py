
import cv2
import numpy as np

class ImageFFT:
    """Image class which holds the image and number of the image in a sequence of images.
    FFT is implemented in the class. Mean value of the image FFT is held in the fft_level parameter."""

    def __init__(self, input_img, number, name):
        self.img = input_img
        self.image_number = number
        self.fft_level = None
        self.name = name

    def runFFT(self):
        self.fft_level = self.fourier()

    def getFFT(self):
        return self.fft_level

    def get_image(self):
        return self.img

    def get_image_number(self):
        return self.image_number

    def get_name(self):
        return self.name

    # algorithm provided by Charles - a slight modification of the optimal sizes
    # has been added to speed up the procedure
    def fourier(self):
        """Function used to calculate FFT of the image - created by Charles."""
        rows, cols = self.img.shape
        nrows = cv2.getOptimalDFTSize(rows)
        ncols = cv2.getOptimalDFTSize(cols)
        nimg = np.zeros((nrows, ncols))
        nimg[:rows, :cols] = self.img

        data_fft1 = np.fft.rfft2(nimg) #the opcv version uses fft2 not rfft2
        fft_abs1 = np.abs(data_fft1).copy()
        h1, w1 = fft_abs1.shape
        # -1 is the last element, last excluded
        # zero frequency is in the top left corner
        part1 = fft_abs1[int(0.05 * h1) : int(0.95 * h1)-1, int(0.05 * w1) : -1]
        output = np.mean(part1)

        return output


