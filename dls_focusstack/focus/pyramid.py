#This is code take from https://github.com/sjawhar/focus-stacking
#which implements the methods described in http://www.ece.drexel.edu/courses/ECE-C662/notes/LaplacianPyramid/laplacian2011.pdf

import cv2
import numpy as np

from focus.pyramid_layer import PyramidLayer


class Pyramid:

    def __init__(self, pyramid_array):
        self.pyramid_array = pyramid_array

    def get_pyramid_array(self):
        return self.pyramid_array


    def fuse(self, kernel_size):
        fused = [self.get_fused_base(kernel_size)]
        for layer in range(len(self.pyramid_array) - 2, -1, -1):
            fused.append(self.get_fused_laplacian(layer))

        return fused[::-1]

    def get_fused_base(self, kernel_size):
        images = self.pyramid_array[-1]
        layers = images.shape[0]
        entropies = np.zeros(images.shape[:3], dtype=np.float64)
        deviations = np.copy(entropies)
        for layer in range(layers):
            gray_image = PyramidLayer(images[layer].astype(np.uint8))
            entropies[layer] = gray_image.entropy(kernel_size)
            deviations[layer] = gray_image.deviation(kernel_size)

        best_e = np.argmax(entropies, axis=0)
        best_d = np.argmax(deviations, axis=0)
        fused = np.zeros(images.shape[1:], dtype=np.float64)

        for layer in range(layers):
            fused += np.where(best_e[:, :] == layer, images[layer], 0)
            fused += np.where(best_d[:, :] == layer, images[layer], 0)

        return (fused / 2).astype(images.dtype)

    def get_fused_laplacian(self, layer):
        laplacians = self.pyramid_array[layer]
        layers = laplacians.shape[0]
        region_energies = np.zeros(laplacians.shape[:3], dtype=np.float64)

        for layer in range(layers):
            gray_lap = PyramidLayer(laplacians[layer])
            region_energies[layer] = gray_lap.region_energy()

        best_re = np.argmax(region_energies, axis=0)
        fused = np.zeros(laplacians.shape[1:], dtype=laplacians.dtype)

        for layer in range(layers):
            fused += np.where(best_re[:, :] == layer, laplacians[layer], 0)

        return fused
