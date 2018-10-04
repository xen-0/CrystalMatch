
import cv2
import numpy as np

from dls_focusstack.focus.fourier import Fourier
from dls_util.imaging import Image
from dls_util.shape import Rectangle


class PointFFT:
    """

    """

    def __init__(self, point, fftimg):
        self.point = point
        self.fft_level = None
        self.img = fftimg.get_image()
        self.level = fftimg.get_image_number()

    def runFFT(self):
        self.fft_level = Fourier(self.crop_region_from_image()).runFFT()

    def getFFT(self):
        return self.fft_level

    def get_point(self):
        return self.point

    def crop_region_from_image(self):
        img = Image(self.img).crop(self._getRegion(100))
        return img.raw()

    def _getRegion(self, size):
        return Rectangle.from_center(self.point, size, size)

    def get_level(self):
        return self.level

