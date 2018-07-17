import cv2
import numpy as np
from scipy import ndimage

class PyramidLayer:

    def __init__(self, array, number):
        self.layer_array = array
        self.layer_number = number
        self.diviations = []
        self.entropies = []

    def get_layer_number(self):
        return self.layer_number


    def region_energy(self):
        a = 0.4
        kernel = np.array([0.25 - a / 2.0, 0.25, a, 0.25, 0.25 - a / 2.0])
        kernel = np.outer(kernel, kernel)
        return  ndimage.convolve(np.square(self.layer_array).astype(np.float64), kernel, mode='mirror')


    def get_probabilities(self):
        levels, counts = np.unique(self.layer_array.astype(np.uint8), return_counts=True)
        probabilities = np.zeros((256,), dtype=np.float64)
        probabilities[levels] = counts.astype(np.float64) / counts.sum()
        return probabilities

    def entropy(self, kernel_size):
        def _area_entropy(area, probabilities):
            levels = area.flatten()
            return -1. * (levels * np.log(probabilities[levels])).sum()

        probabilities = self.get_probabilities()
        pad_amount = int((kernel_size - 1) / 2)
        padded_image = cv2.copyMakeBorder(self.layer_array, pad_amount, pad_amount, pad_amount, pad_amount, cv2.BORDER_REFLECT101)
        entropies = np.zeros(self.layer_array.shape[:2], dtype=np.float64)
        offset = np.arange(-pad_amount, pad_amount + 1)
        for row in range(entropies.shape[0]):
            for column in range(entropies.shape[1]):
                area = padded_image[row + pad_amount + offset[:, np.newaxis], column + pad_amount + offset]
                entropies[row, column] = _area_entropy(area, probabilities)

        self.entropies = entropies

    def get_entropies(self):
        return self.entropies

    def deviation(self, kernel_size):
        def _area_deviation(area):
            average = np.average(area).astype(np.float64)
            return np.square(area - average).sum() / area.size

        pad_amount = int((kernel_size - 1) / 2)
        padded_image = cv2.copyMakeBorder(self.layer_array, pad_amount, pad_amount, pad_amount, pad_amount, cv2.BORDER_REFLECT101)
        deviations = np.zeros(self.layer_array.shape[:2], dtype=np.float64)
        offset = np.arange(-pad_amount, pad_amount + 1)
        for row in range(deviations.shape[0]):
            for column in range(deviations.shape[1]):
                area = padded_image[row + pad_amount + offset[:, np.newaxis], column + pad_amount + offset]
                deviations[row, column] = _area_deviation(area)

        self.diviations = deviations

    def get_diviations(self):
        return self.diviations