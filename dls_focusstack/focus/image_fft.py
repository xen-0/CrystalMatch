import time

import cv2
import numpy as np


class Image_FFT:

    def __init__(self, input_img,number):
        self.img = input_img
        self.image_number = number
        self.fft_level = None

    def runFFT(self):
        #self.fft_level = self.furier()
        self.fft_level = self.furier2()

    def getFFT(self):
        return self.fft_level

    def getImage(self):
        return self.img

    def getImageNumber(self):
        return self.image_number

    def furier(self):
        time1 = time.clock()
        rows, cols = self.img.shape
        nrows = cv2.getOptimalDFTSize(rows)
        ncols = cv2.getOptimalDFTSize(cols)
        nimg = np.zeros((nrows, ncols))
        nimg[:rows, :cols] = self.img

        data_fft = cv2.dft(nimg, flags=cv2.DFT_COMPLEX_OUTPUT)
        # see explenation https://docs.scipy.org/doc/numpy/reference/generated/numpy.fft.rfft.html
        w = ncols/2 +1
        fft_abs = cv2.magnitude(data_fft[:,:w,0],data_fft[:,:w,1])#np.abs(data_fft)
        # -1 is the last element, last excluded
        part = fft_abs[int(0.05 * nrows): int(0.95 * nrows) - 1, int(0.05 * w): -1]
        result = np.mean(part)
        time2 = time.clock() - time1
        return result

    #algorithm porvided by Charles Mitta - a slight modification of the optimal sizes
    # has been added to speed up the procedure
    def furier2(self):
        time1 = time.clock()
        rows, cols = self.img.shape
        nrows = cv2.getOptimalDFTSize(rows)
        ncols = cv2.getOptimalDFTSize(cols)
        nimg = np.zeros((nrows, ncols))
        nimg[:rows, :cols] = self.img

        data_fft1 = np.fft.rfft2(nimg) #the opcv version uses fft2 not rfft2
        fft_abs1 = np.abs(data_fft1).copy()
        h1, w1 = fft_abs1.shape
        # -1 is the last element, last excluded
        part1 = fft_abs1[int(0.05 * h1) : int(0.95 * h1)-1, int(0.05 * w1) : -1] #zero frequency is in the top left corner
        output = np.mean(part1)
        time3 = time.clock()-time1
        return output



