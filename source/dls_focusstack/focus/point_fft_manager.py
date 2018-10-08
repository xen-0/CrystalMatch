
from dls_focusstack.focus.pointfft import PointFFT

class PointFFTManager:
    """
    Initialise z new PointFFTManager object.
    :param fftimages: list of fftimages
    :param match: single point match result
    :param z_level_region_size: size of region used in pointfft
    """
    def __init__(self, fftimages, match, z_level_region_size):
        self.images = fftimages
        self.match = match
        self.region_size = z_level_region_size

    def find_z_level_for_point(self):
        if self.images is not None:
            fftlevels = []
            for image in  self.images:
                pointfft = PointFFT(self.match.get_transformed_poi(), image, self.region_size)
                pointfft.runFFT()
                fftlevels.append(pointfft)
            max_fft_point = max(fftlevels, key=lambda fftpoint: fftpoint.getFFT())
            self.match.set_poi_z_level(max_fft_point.get_level())
