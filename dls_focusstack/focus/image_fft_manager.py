
from multiprocessing import Process, Queue

import cv2
import numpy as np

from focus.image_fft import Image_FFT

def f(file_obj,q,count):
    img_color = cv2.imread(file_obj.name)
    img = cv2.cvtColor(img_color.astype(np.float32), cv2.COLOR_BGR2GRAY)
    image_fft = Image_FFT(img, count)
    image_fft.runFFT()
    q.put(image_fft)


class ImageFFTManager:

    def __init__(self, name_list):
        self._image_file_list = name_list
        self.fft_images = []


    def read_ftt_images(self):

        q = Queue()
        processes=[]
        count = 1
        for file_obj in self._image_file_list:
            process = Process(target=f, args=(file_obj,q,count))
            processes.append(process)
            count = count+1

        for p in processes:
            p.start()

        self.fft_images = [q.get() for p in processes]

        for p in processes:
            p.join()


    def get_fft_images(self):
        return self.fft_images

