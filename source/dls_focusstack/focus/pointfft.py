
from dls_focusstack.focus.fourier import Fourier
from dls_util.imaging import Image
from dls_util.shape import Rectangle


class PointFFT:
    """
    Initialise a new pointfft object which links an a point and allows to calculate fft within an ragion of a given size.
    :param point: point for which the fft can be calculated
    :param fftimage: fftimage from which a region of interes is cropped
    :param region size: size of region taken to calculate fft - it is a square (size x size)
    """

    def __init__(self, point, fftimg, region_size):
        self.point = point
        self.fft_level = None
        self.fftimg = fftimg
        self.region_size = region_size

    def runFFT(self):
        self.fft_level = Fourier(self.crop_region_from_image()).runFFT()

    def getFFT(self):
        return self.fft_level

    def get_point(self):
        return self.point

    def crop_region_from_image(self):
        img = Image(self.fftimg.get_image()).crop(self._getRegion())
        return img.raw()

    def _getRegion(self):
        return Rectangle.from_center(self.point, self.region_size, self.region_size)

    def get_level(self):
        return self.fftimg.get_image_number()

    def get_image_name(self):
        return self.fftimg.get_name()

