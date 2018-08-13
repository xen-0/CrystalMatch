from unittest import TestCase

from pkg_resources import require

require("numpy==1.11.1")

import numpy as np

from focus.image_fft import Image_FFT
from mock import MagicMock


class TestImageFFT(TestCase):

    def setUp(self):
        self._img = np.array([(0, 2, 3, 4),
                        (1, 3, 4, 5),
                        (1, 0, 2, 5)])

    def test_runFFT_calls_furrier2(self):
        sh = Image_FFT(self._img, 1, 'test')
        sh.fourier2 = MagicMock()

        sh.runFFT()
        sh.fourier2.assert_called_once()

    def test_getFFT_returns_none_before_furrier_is_run(self):
        sh = Image_FFT(self._img, 1, 'test')
        self.assertIsNone(sh.getFFT())

    def test_getFFT_returns_not_none_furrier_is_run(self):
        sh = Image_FFT(self._img, 1, 'test')
        sh.runFFT()
        self.assertIsNotNone(sh.getFFT())

    def test_get_image_number_returns_correct_value(self):
        sh = Image_FFT(self._img, 1, 'test')
        self.assertEqual(sh.getImageNumber(),1)

    def test_get_image_returns_correct_value(self):
        sh = Image_FFT(self._img, 1, 'test')
        self.assertIn(sh.getImage(), self._img)







