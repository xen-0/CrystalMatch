from unittest import TestCase

from pkg_resources import require

require("numpy==1.11.1")

import numpy as np


from focus.image_fft import Image_FFT


class TestImageFFT(TestCase):

    def test_furier(self):
        img =  np.array([(0, 2, 3, 4),
                         (1, 3, 4, 5),
                         (1, 0, 2, 5)])
        sh = Image_FFT(img,1)
        r = sh.furier()
        r1 = sh.furier2()


