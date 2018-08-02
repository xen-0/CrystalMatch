#This is code take from https://github.com/sjawhar/focus-stacking
#which implements the methods described in http://www.ece.drexel.edu/courses/ECE-C662/notes/LaplacianPyramid/laplacian2011.pdf

import cv2
import numpy as np
import logging
import logconfig

from focus.pyramid import Pyramid


class PyramidManager:
    """This is a pyramid manages class."""

    def __init__(self, aligned_images, config):
        self.images = aligned_images
        self.config = config

    def get_pyramid_fusion(self):
        """This is the function which maintains the steps of pyramid processing.
        It creates the laplacian pyramid,
        starts the fusion process which flattens the pyramid along layers and finally collapses the pyramid."""
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        smallest_side = min(self.images[0].shape[:2])
        cfg = self.config
        min_size = cfg.pyramid_min_size.value()
        depth = int(np.log2(smallest_side / min_size))
        kernel_size = cfg.kernel_size.value()
        log.info("t10")
        #create pyramid
        pyramid = self.laplacian_pyramid(depth)
        log.info("t11")
        #fuse pyramid
        fusion = pyramid.fuse(kernel_size)
        log.info("t16")
        #collaps pyramid
        return self.collapse(fusion)

    #this is only used by the laplacian pyramid function
    def _gaussian_pyramid(self, depth):
        """Creates the gaussian pyramid of a certain depth"""
        pyramid_array = [self.images.astype(np.float64)]
        num_images = self.images.shape[0]

        while depth > 0:
            image_zero = pyramid_array[-1][0]
            next_level = cv2.pyrDown(image_zero)  # image
            next_level_size = [num_images] + list(next_level.shape)
            pyramid_array.append(np.zeros(next_level_size, dtype=next_level.dtype))  # pyramid extended
            pyramid_array[-1][0] = next_level
            for layer in range(1, num_images):
                next_image = cv2.pyrDown(pyramid_array[-2][layer])  # -2 due to the extension above
                pyramid_array[-1][layer] = next_image  # downscaled image
            depth = depth - 1

        return Pyramid(pyramid_array)

    def laplacian_pyramid(self, depth):
        """Create laplacian pyramid of a certain depth."""
        gaussian = self._gaussian_pyramid(depth)
        gaussian_array = gaussian.get_pyramid_array()

        pyramid = [gaussian_array[-1]]

        for level in range(len(gaussian_array) - 1, 0, -1):
            gauss = gaussian_array[level - 1]
            pyramid.append(np.zeros(gauss.shape, dtype=gauss.dtype))
            for layer in range(self.images.shape[0]):
                gauss_layer = gauss[layer]
                expanded = cv2.pyrUp(gaussian_array[level][layer])
                if expanded.shape != gauss_layer.shape:
                    expanded = expanded[:gauss_layer.shape[0], :gauss_layer.shape[1]]
                pyramid[-1][layer] = gauss_layer - expanded

        return Pyramid(pyramid[::-1])  # revert the sequence

    def collapse(self, pyramid_array):
        """Collapse the pyramid - effectively flatten a fused pyramid along levels to get one all in focus image."""
        image = pyramid_array[-1]
        for layer in pyramid_array[-2::-1]:
            expanded = cv2.pyrUp(image)
            if expanded.shape != layer.shape:
                expanded = expanded[:layer.shape[0], :layer.shape[1]]
            image = expanded + layer

        return image