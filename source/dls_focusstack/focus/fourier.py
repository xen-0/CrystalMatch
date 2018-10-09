
import cv2
import numpy as np

class Fourier:
    """
    Initialise a new fourier object.
    :param input_array: input for the fourier transform calculation
    """
    def __init__(self, input_array):
        self.array = input_array

    def runFFT(self):
        return self.fourier()

    # algorithm provided by Charles - a slight modification of the optimal sizes
    # has been added to speed up the procedure
    def fourier(self):
        """Function used to calculate FFT of the image - created by Charles."""
        rows, cols = self.array.shape
        nrows = cv2.getOptimalDFTSize(rows)
        ncols = cv2.getOptimalDFTSize(cols)
        nimg = np.zeros((nrows, ncols))
        nimg[:rows, :cols] = self.array

        data_fft1 = np.fft.rfft2(nimg) #the opcv version uses fft2 not rfft2
        fft_abs1 = np.abs(data_fft1).copy()
        h1, w1 = fft_abs1.shape
        # -1 is the last element, last excluded
        # zero frequency is in the top left corner
        part1 = fft_abs1[int(0.05 * h1) : int(0.95 * h1)-1, int(0.05 * w1) : -1]
        output = np.mean(part1)

        return output



