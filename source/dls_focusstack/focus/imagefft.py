

from dls_focusstack.focus.fourier import Fourier


class ImageFFT:
    """Image class which holds the image and number of the image in a sequence of images.
    FFT is implemented in the class. Mean value of the image FFT is held in the fft_level parameter."""

    def __init__(self, input_img, number, name):
        self.img = input_img
        self.image_number = number
        self.fft_level = None
        self.name = name

    def runFFT(self):
        self.fft_level = Fourier(self.img).runFFT()

    def getFFT(self):
        return self.fft_level

    def get_image(self):
        return self.img

    def get_image_number(self):
        return self.image_number

    def get_name(self):
        return self.name


