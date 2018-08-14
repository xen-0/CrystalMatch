import logging
from multiprocessing import Process, Queue

import cv2
import numpy as np

from dls_focusstack import logconfig
from dls_focusstack.focus.imagefft import ImageFFT


def fft(file_obj,q,count):
    "Function that reads an image of a given name and  starts fft calculation."
    #read as soon as it appears
    name = file_obj.name
    img_color = cv2.imread(name)
    img = cv2.cvtColor(img_color.astype(np.float32), cv2.COLOR_BGR2GRAY)
    image_fft = ImageFFT(img, count, name)
    image_fft.runFFT()
    q.put(image_fft)


class ImageFFTManager:
    """Class which manages fft calculations."""
    def __init__(self, name_list):
        self._image_file_list = name_list
        self.fft_images = []


    def read_ftt_images(self):
        """Function which starts fft calculation for each input image name.
        Multiprocessing is used to speed up the calculation.
        One process for one input image name."""
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        #log.info("t4")

        q = Queue()
        #log.info("t5")
        processes=[]
        #log.info("t6")

        for idx, file_obj in enumerate(self._image_file_list):
            process = Process(target=fft, args=(file_obj,q,idx))
            process.start()
            processes.append(process)
        #log.info("t7")
        self.fft_images = [q.get() for p in processes]
        for p in processes:
            p.join()
        #log.info("t8")

    def get_fft_images(self):
        return self.fft_images