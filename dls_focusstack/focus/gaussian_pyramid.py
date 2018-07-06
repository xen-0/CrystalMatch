
from multiprocessing import Process, Queue

import cv2
import numpy as np

def ff(d,layer,img,q):
    pyramid_layer =  cv2.pyrDown(img)
    element =  gausian_element(d, layer, pyramid_layer)
    q.put(element)

class gaussian_pyramid:

    def __init__(self, images, depth):
        self.images = images
        self.depth = depth

    def calculate_pyramid(self):
        pyramid = [self.images.astype(np.float64)]
        num_images = self.images.shape[0]
        elements = []

        for d in range(1, self.depth):
            q = Queue()
            processes = []
            next_layer = cv2.pyrDown(pyramid[-1][0])  # image
            next_layer_size = [num_images] + list(next_layer.shape)
            pyramid.append(np.zeros(next_layer_size, dtype=next_layer.dtype))
            pyramid[-1][0] = next_layer
            for layer in range(1, num_images):
                process = Process(target=ff, args=(d, layer, pyramid[-2][layer],q))
                processes.append(process)
            for p in processes:
                p.start()
                elements.append(q.get())


            for e in elements:
                pyramid[e.get_level()] [e.get_layer()] = e.get_img()

            for p in processes:
                p.join()

        return pyramid

class gausian_element:

    def __init__(self, level, layer,img):
        self._level = level
        self._layer = layer
        self._img = img

    def get_layer(self):
        return self._layer

    def get_level(self):
        return self._level

    def get_img(self):
        return self._img





