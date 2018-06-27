import cv2
import numpy as np


class SharpnessDetector:

    LAPLACE_VAR_TRESH = 76.9
    FURIER_TRESH = 450

    def __init__(self, input_img):
        self.img = input_img
        self.fft_level = None

    def runFFT(self):
        self.fft_level = self.furier()

    def getFFT(self):
        return self.fft_level

    def getImage(self):
        return self.img

    def furier(self):
        rows, cols = self.img.shape
        nrows = cv2.getOptimalDFTSize(rows)
        ncols = cv2.getOptimalDFTSize(cols)
        nimg = np.zeros((nrows, ncols))
        nimg[:rows, :cols] = self.img
        dft = cv2.dft(nimg, flags=cv2.DFT_COMPLEX_OUTPUT)
        result = np.mean(np.abs(dft))
        return result




