import time
from multiprocessing import Process, Queue, current_process, Pool

import cv2
import numpy as np

from config.focus_config import FocusConfig
from dls_util.imaging import Image
from focus.pyramid import pyramid
from os.path import join

from focus.image_fft import Image_FFT

IMG_TO_STACK = 8 #how many images will be stacked


def f(file_obj,q,count):
    img_color = cv2.imread(file_obj.name)
    img = cv2.cvtColor(img_color.astype(np.float32), cv2.COLOR_BGR2GRAY)
    image_fft = Image_FFT(img, count)
    image_fft.runFFT()
    q.put(image_fft)


class FocusStack:
    CONFIG_FILE_NAME = "focus_stack.ini"

    def __init__(self, images, config_dir):
        self._image_file_list = images
        self._config = FocusConfig(join(config_dir, self.CONFIG_FILE_NAME))

    def composite(self):
        t1 = time.clock()
        images = self.find_sharp()
        t2 = time.clock() - t1
        print 'time fft:', t2
        images = np.array(images, dtype=images[0].dtype)

        #TODO:Implement alignment algo
        #aligned_images, gray_images = self.align(images)

        #stacked_image = pyramid(aligned_images, self._config).get_pyramid_fusion()
        stacked_image = pyramid(images, self._config).get_pyramid_fusion()
        stacked_image  = cv2.convertScaleAbs(stacked_image)
        return Image(stacked_image)

    def find_sharp(self):

        q = Queue()

        #processes = [Process(target=f, args=(file_obj,q)) for file_obj in self._image_file_list]
        processes=[]
        count = 1
        for file_obj in self._image_file_list:
            process = Process(target=f, args=(file_obj,q,count))
            processes.append(process)
            count = count+1

        for p in processes:
            p.start()

        sd = [q.get() for p in processes]

        for p in processes:
            p.join()

        images = self.images_to_stack(sd)
        #take n images from the stuck
        return images


    def images_to_stack(self, sd):
        n = len(sd)
        level = 0
        max = None
        images = []
        for s in sd:
            fft = s.getFFT()
            if fft > level:
                level = fft
                max = s.getImageNumber()

        range = self.find_range(max,n)
        for s in sd:
            if s.getImageNumber() in range:
                images.append(s.getImage())

        return images


    @staticmethod
    def find_range(max,n):
        if max -(IMG_TO_STACK / 2) < 1:
            return range(1, IMG_TO_STACK)
        elif max + (IMG_TO_STACK / 2) > n:
            return range(-IMG_TO_STACK, n)
        else:
            return range(max - IMG_TO_STACK / 2, max + IMG_TO_STACK / 2)




