from unittest import TestCase

from pkg_resources import require

require("numpy==1.11.1")

import numpy as np

from focus.image_fft import Image_FFT

from mock import MagicMock

class TestImageFFT(TestCase):

    def setUp(self):
        img = np.array([(0, 2, 3, 4),
                        (1, 3, 4, 5),
                        (1, 0, 2, 5)])
        self._img_fft = Image_FFT(img, 1)


