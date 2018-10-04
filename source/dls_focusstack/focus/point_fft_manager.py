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
    fftpoints =[]

    for image in fftimages:
        pointfft = PointFFT(point, image)
        pointfft.runFFT()
        fftpoints.append(pointfft)

    max_fft_point = max(fftpoints, key=lambda fftpoint : fftpoint.getFFT)

    return max_fft_point


class PointFFTManager:
    """"""
    def __init__(self, images, match_result):
        self.images = images
        self.match_result = match_result

    def _get_list_of_translformed_points(self):
        points = []
        for poi in self.match_result:
            points.append(poi.get_transformed_poi())
        return points

    def read_ftt_points(self):
        points = self._get_list_of_translformed_points()
        params = []
        for point in points:
            param = (self.images, point)
            params.append(param)

        pool = Pool()
        result = pool.map_async(max_fft_point, params)

        pool.close()
        pool.join()
        fftpoints = result.get()

        return fftpoints




