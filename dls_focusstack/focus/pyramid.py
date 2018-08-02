"""This is code taken from https://github.com/sjawhar/focus-stacking
which implements the methods described in http://www.ece.drexel.edu/courses/ECE-C662/notes/LaplacianPyramid/laplacian2011.pdf"""
from multiprocessing import Queue, Process

import numpy as np

import logging
import logconfig


from pyramid_layer import PyramidLayer

def entropy_diviation(pyramid_layer,kernel_size,q):
    """On the top level of the pyramid (the one with the lowest resolution) two fusion operators:
    entropy and deviation are used"""
    gray_image = pyramid_layer
    gray_image.entropy(kernel_size)
    gray_image.deviation(kernel_size)

    q.put(gray_image)

def fused_laplacian(laplacians, region_kernel, q):
    """On other levels of the pyramid one fusion operator: region energy is used"""
    layers = laplacians.shape[0]
    region_energies = np.zeros(laplacians.shape[:3], dtype=np.float64)

    for layer in range(layers):
        gray_lap = PyramidLayer(laplacians[layer],layer)
        region_energies[layer] = gray_lap.region_energy(region_kernel)

    best_re = np.argmax(region_energies, axis=0)
    fused = np.zeros(laplacians.shape[1:], dtype=laplacians.dtype)

    for layer in range(layers):
        fused += np.where(best_re[:, :] == layer, laplacians[layer], 0)

    q.put(fused)

class Pyramid:
    """Pyramid has is an array with 4 dimensions: level, layer, image wight and image height
    number of levels is defined by pyramid depth
    number of layers is the number of input images each one focused on a different z-level"""
    def __init__(self, pyramid_array):
        self.pyramid_array = pyramid_array

    def get_pyramid_array(self):
        return self.pyramid_array

    def get_region_kernel(self):
        a = 0.4
        kernel = np.array([0.25 - a / 2.0, 0.25, a, 0.25, 0.25 - a / 2.0])
        return np.outer(kernel, kernel)

    def fuse(self, kernel_size):
        """Function which fuses each level of the pyramid using appropriate fusion operators
        the output is a 3 dimensional array (level, image wight, image high)
        - the input array is flattened along layers"""
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        log.info("t12")
        fused = [self.get_fused_base(kernel_size)]
        q = Queue()
        processes = []
        region_kernel = self.get_region_kernel()
        for level in range(len(self.pyramid_array) - 2, -1, -1):
            laplacians = self.pyramid_array[level]

            process = Process(target=fused_laplacian, args=(laplacians, region_kernel,q))
            process.start()
            processes.append(process)
        log.info("t13")
        for level in range(len(self.pyramid_array) - 2, -1, -1):
            pyramid_level = q.get()
            fused.append(pyramid_level)
        log.info("t14")
        for p in processes:
            p.join() #this one won't work if there is still something in the Queue
        log.info("t15")
        fused.sort(key=len, reverse=True)  # highest resolution on level 0
        return fused

    def get_fused_base(self, kernel_size):
        """Fuses the base of the pyramid - the one with the lowest resolution."""
        images = self.pyramid_array[-1]
        layers = images.shape[0]
        entropies = np.zeros(images.shape[:3], dtype=np.float64)
        deviations = np.copy(entropies)
        q = Queue()
        processes = []
        for layer in range(layers):
            gray_image = PyramidLayer(images[layer], layer)

            process = Process(target=entropy_diviation, args=(gray_image, kernel_size, q))
            process.start()
            processes.append(process)

        for layer in range(layers):
            #should always do all threads as all the processes are the same and should take roughly the same time
            l = q.get() #picks the first one which is ready
            entropies[l.get_layer_number()] = l.get_entropies()
            deviations[l.get_layer_number()] = l.get_deviations()

        for p in processes:
            p.join() #this one won't work if there is still something in the Queue

        best_e = np.argmax(entropies, axis=0)
        best_d = np.argmax(deviations, axis=0)
        fused = np.zeros(images.shape[1:], dtype=np.float64)

        for layer in range(layers):
            fused += np.where(best_e[:, :] == layer, images[layer], 0)
            fused += np.where(best_d[:, :] == layer, images[layer], 0)

        return (fused / 2).astype(images.dtype)

