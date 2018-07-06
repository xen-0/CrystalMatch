#This is code take from https://github.com/sjawhar/focus-stacking
#which implements the methods described in http://www.ece.drexel.edu/courses/ECE-C662/notes/LaplacianPyramid/laplacian2011.pdf

import cv2
import numpy as np
from scipy import ndimage

class pyramid:

    def __init__(self, aligned_images, config):
        self.images = aligned_images
        self.config = config

    def generating_kernel(a):
        kernel = np.array([0.25 - a / 2.0, 0.25, a, 0.25, 0.25 - a / 2.0])
        return np.outer(kernel, kernel)

    def convolve(self, image, kernel=generating_kernel(0.4)):
        return ndimage.convolve(image.astype(np.float64), kernel, mode='mirror')

    def gaussian_pyramid(self, depth):
        pyramid = [self.images.astype(np.float64)]
        num_images = self.images.shape[0]

        while depth > 0:
            next_layer = cv2.pyrDown(pyramid[-1][0]) #image
            next_layer_size = [num_images] + list(next_layer.shape)
            pyramid.append(np.zeros(next_layer_size, dtype=next_layer.dtype))
            pyramid[-1][0] = next_layer
            for layer in range(1, num_images):
                pyramid[-1][layer] = cv2.pyrDown(pyramid[-2][layer]) #downscaled image
            depth = depth - 1

        return pyramid

    def laplacian_pyramid(self, depth):
        gaussian = self.gaussian_pyramid(depth)

        pyramid = [gaussian[-1]]
        for level in range(len(gaussian) - 1, 0, -1):
            gauss = gaussian[level - 1]
            pyramid.append(np.zeros(gauss.shape, dtype=gauss.dtype))
            for layer in range(self.images.shape[0]):
                gauss_layer = gauss[layer]
                expanded = cv2.pyrUp(gaussian[level][layer])
                if expanded.shape != gauss_layer.shape:
                    expanded = expanded[:gauss_layer.shape[0], :gauss_layer.shape[1]]
                pyramid[-1][layer] = gauss_layer - expanded

        return pyramid[::-1]

    def collapse(self, pyramid):
        image = pyramid[-1]
        for layer in pyramid[-2::-1]:
            expanded = cv2.pyrUp(image)
            if expanded.shape != layer.shape:
                expanded = expanded[:layer.shape[0], :layer.shape[1]]
            image = expanded + layer

        return image

    def get_probabilities(self, gray_image):
        levels, counts = np.unique(gray_image.astype(np.uint8), return_counts=True)
        probabilities = np.zeros((256,), dtype=np.float64)
        probabilities[levels] = counts.astype(np.float64) / counts.sum()
        return probabilities

    def entropy(self, image, kernel_size):
        def _area_entropy(area, probabilities):
            levels = area.flatten()
            return -1. * (levels * np.log(probabilities[levels])).sum()

        probabilities = self.get_probabilities(image)
        pad_amount = int((kernel_size - 1) / 2)
        padded_image = cv2.copyMakeBorder(image, pad_amount, pad_amount, pad_amount, pad_amount, cv2.BORDER_REFLECT101)
        entropies = np.zeros(image.shape[:2], dtype=np.float64)
        offset = np.arange(-pad_amount, pad_amount + 1)
        for row in range(entropies.shape[0]):
            for column in range(entropies.shape[1]):
                area = padded_image[row + pad_amount + offset[:, np.newaxis], column + pad_amount + offset]
                entropies[row, column] = _area_entropy(area, probabilities)

        return entropies

    def deviation(self, image, kernel_size):
        def _area_deviation(area):
            average = np.average(area).astype(np.float64)
            return np.square(area - average).sum() / area.size

        pad_amount = int((kernel_size - 1) / 2)
        padded_image = cv2.copyMakeBorder(image, pad_amount, pad_amount, pad_amount, pad_amount, cv2.BORDER_REFLECT101)
        deviations = np.zeros(image.shape[:2], dtype=np.float64)
        offset = np.arange(-pad_amount, pad_amount + 1)
        for row in range(deviations.shape[0]):
            for column in range(deviations.shape[1]):
                area = padded_image[row + pad_amount + offset[:, np.newaxis], column + pad_amount + offset]
                deviations[row, column] = _area_deviation(area)

        return deviations

    def get_fused_base(self, images, kernel_size):
        layers = images.shape[0]
        entropies = np.zeros(images.shape[:3], dtype=np.float64)
        deviations = np.copy(entropies)
        for layer in range(layers):
            gray_image = images[layer].astype(np.uint8)
            entropies[layer] = self.entropy(gray_image, kernel_size)
            deviations[layer] = self.deviation(gray_image, kernel_size)

        best_e = np.argmax(entropies, axis=0)
        best_d = np.argmax(deviations, axis=0)
        fused = np.zeros(images.shape[1:], dtype=np.float64)

        for layer in range(layers):
            fused += np.where(best_e[:, :] == layer, images[layer], 0)
            fused += np.where(best_d[:, :] == layer, images[layer], 0)

        return (fused / 2).astype(images.dtype)

    def fuse_pyramids(self,pyramids, kernel_size):
        fused = [self.get_fused_base(pyramids[-1], kernel_size)]
        for layer in range(len(pyramids) - 2, -1, -1):
            fused.append(self.get_fused_laplacian(pyramids[layer]))

        return fused[::-1]

    def get_fused_laplacian(self,laplacians):
        layers = laplacians.shape[0]
        region_energies = np.zeros(laplacians.shape[:3], dtype=np.float64)

        for layer in range(layers):
            gray_lap = laplacians[layer]
            region_energies[layer] = self.region_energy(gray_lap)

        best_re = np.argmax(region_energies, axis=0)
        fused = np.zeros(laplacians.shape[1:], dtype=laplacians.dtype)

        for layer in range(layers):
            fused += np.where(best_re[:, :] == layer, laplacians[layer], 0)

        return fused

    def region_energy(self, laplacian):
        return self.convolve(np.square(laplacian))

    def get_pyramid_fusion(self):
        smallest_side = min(self.images[0].shape[:2])
        cfg = self.config
        min_size = cfg.pyramid_min_size.value()
        depth = int(np.log2(smallest_side / min_size))
        kernel_size = cfg.kernel_size.value()

        pyramids = self.laplacian_pyramid(depth)
        fusion = self.fuse_pyramids(pyramids, kernel_size)

        return self.collapse(fusion)
