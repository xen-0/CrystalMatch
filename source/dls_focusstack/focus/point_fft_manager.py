import logging
from multiprocessing import Process, Queue, Pool

import cv2
import numpy as np

from dls_focusstack.focus.pointfft import PointFFT
from dls_imagematch import logconfig
from dls_focusstack.focus.imagefft import ImageFFT


def max_fft_point(param):
    fftimages = param[0]
    point = param[1]
    fftlevels =[]

    for image in fftimages:
        pointfft = PointFFT(point, image)
        pointfft.runFFT()
        fftlevels.append(pointfft)
    max_fft_point = max(fftlevels, key=lambda fftpoint : fftpoint.getFFT())

    return max_fft_point

class PointFFTManager:
    """"""
    def __init__(self, images, match_results):
        self.images = images
        self.match_results = match_results

    def read_ftt_points(self):
        matches = self.match_results.get_matches()
        params = []
        for match in matches:
            param = (self.images, match.get_transformed_poi())
            params.append(param)

        pool = Pool()
        result = pool.map_async(max_fft_point, params)

        pool.close()
        pool.join()

        max_fft_points = result.get()

        # tired to pass the whole match object to max_fft_point but got a pickling error
        # tried this mapping instead
        for match in matches:
            #distnce 0 means same points
            fft_point = filter(lambda x : x.get_point().distance_to(match.get_transformed_poi()) == 0, max_fft_points)
            match.set_poi_z_level(fft_point[0].get_level())


