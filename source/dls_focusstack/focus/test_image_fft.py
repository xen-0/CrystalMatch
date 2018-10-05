from pkg_resources import require
require('pygelf==0.2.11')
require("numpy==1.11.1")
require("scipy")

from unittest import TestCase

import numpy as np

from dls_focusstack.focus.imagefft import ImageFFT
from mock import MagicMock


class TestImageFFT(TestCase):

    def setUp(self):
        self._img = np.array([(0, 2, 3, 4),
                        (1, 3, 4, 5),
                        (1, 0, 2, 5)])

    def test_runFFT_calculates_a_fourier_value_of_an_image(self):
        sh = ImageFFT(self._img, 1, 'test')
        sh.runFFT()
        self.assertIsNotNone(sh.getFFT())

    def test_getFFT_returns_none_before_furrier_is_run(self):
        sh = ImageFFT(self._img, 1, 'test')
        self.assertIsNone(sh.getFFT())

    def test_getFFT_returns_not_none_furrier_is_run(self):
        sh = ImageFFT(self._img, 1, 'test')
        sh.runFFT()
        self.assertIsNotNone(sh.getFFT())

    def test_get_image_number_returns_correct_value(self):
        sh = ImageFFT(self._img, 1, 'test')
        self.assertEqual(sh.get_image_number(), 1)

    def test_get_image_returns_correct_value(self):
        sh = ImageFFT(self._img, 1, 'test')
        self.assertIn(sh.get_image(), self._img)







