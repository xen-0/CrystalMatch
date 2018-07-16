#This is code take from https://github.com/sjawhar/focus-stacking
#which implements the methods described in http://www.ece.drexel.edu/courses/ECE-C662/notes/LaplacianPyramid/laplacian2011.pdf

import cv2
import numpy as np
from scipy import ndimage

from focus.pyramid import Pyramid


class PyramidManager:

    def __init__(self, aligned_images, config):
        self.images = aligned_images
        self.config = config
        self.pyramid = Pyramid(self.images, self.config)

    def get_pyramid_fusion(self):
        smallest_side = min(self.images[0].shape[:2])
        cfg = self.config
        min_size = cfg.pyramid_min_size.value()
        depth = int(np.log2(smallest_side / min_size))
        kernel_size = cfg.kernel_size.value()

        pyramid = self.pyramid.laplacian_pyramid(depth)

        fusion = self.fuse_pyramid(pyramid, kernel_size)

        return self.collapse(fusion)


    @staticmethod
    def collapse(pyramid):
        image = pyramid[-1]
        for layer in pyramid[-2::-1]:
            expanded = cv2.pyrUp(image)
            if expanded.shape != layer.shape:
                expanded = expanded[:layer.shape[0], :layer.shape[1]]
            image = expanded + layer

        return image


    def get_fused_base(self, pyramid, kernel_size):
        images = pyramid[-1]
        layers = images.shape[0]
        entropies = np.zeros(images.shape[:3], dtype=np.float64)
        deviations = np.copy(entropies)
        for layer in range(layers):
            gray_image = images[layer].astype(np.uint8)
            entropies[layer] = self.pyramid.entropy(gray_image, kernel_size)
            deviations[layer] = self.pyramid.deviation(gray_image, kernel_size)

        best_e = np.argmax(entropies, axis=0)
        best_d = np.argmax(deviations, axis=0)
        fused = np.zeros(images.shape[1:], dtype=np.float64)

        for layer in range(layers):
            fused += np.where(best_e[:, :] == layer, images[layer], 0)
            fused += np.where(best_d[:, :] == layer, images[layer], 0)

        return (fused / 2).astype(images.dtype)

    def fuse_pyramid(self, pyramid, kernel_size):
        fused = [self.get_fused_base(pyramid, kernel_size)]
        for layer in range(len(pyramid) - 2, -1, -1):
            fused.append(self.get_fused_laplacian(pyramid,layer))

        return fused[::-1]

    def get_fused_laplacian(self, pyramid, layer):
        laplacians = pyramid[layer]
        layers = laplacians.shape[0]
        region_energies = np.zeros(laplacians.shape[:3], dtype=np.float64)

        for layer in range(layers):
            gray_lap = laplacians[layer]
            region_energies[layer] = +self.pyramid.region_energy(gray_lap)

        best_re = np.argmax(region_energies, axis=0)
        fused = np.zeros(laplacians.shape[1:], dtype=laplacians.dtype)

        for layer in range(layers):
            fused += np.where(best_re[:, :] == layer, laplacians[layer], 0)

        return fused
