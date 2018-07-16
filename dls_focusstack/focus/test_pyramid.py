from unittest import TestCase
from pkg_resources import require

require("numpy==1.11.1")
require("scipy")

import numpy as np

from mock import MagicMock

from focus.pyramid import Pyramid


class TestPyramid(TestCase):

    def setUp(self):
        self._images = MagicMock()
        self._config = MagicMock()
        self._array = np.array([[10, 20, 30, 40], [10, 20, 30, 40], [11, 21, 31, 41], [12, 22, 32, 42]], dtype=np.float64)
        self._depth = 2
        #two input images
        self._images.astype.return_value = np.array([self._array, self._array/10])
        #shape of input
        self._images.shape = [2, self._array.shape[0], self._array.shape[1]]

    def test_gaussian_pyramid_has_correct_size(self):
        #gaussian pyramid
        p = Pyramid(self._images, self._config).gaussian_pyramid(self._depth)
        #piramid hight size depth+1
        self.assertEqual(len(p), self._depth+1)
        #zero level of p - the input
        self.assertEquals(p[0][0].shape, self._array.shape) #first image
        self.assertEquals(p[0][1].shape, self._array.shape) #second image
        #size of first level is half of first
        self.assertEquals(p[1][0].shape, (2,2)) #first image
        self.assertEquals(p[1][1].shape, (2,2))  #second image
        #size of second level one fought of first
        self.assertEquals(p[2][1].shape, (1,1))  # second image
        #zero level of the pyramid is made out of input images
        self.assertEquals(p[0][0][0][0], 10)

    def test_laplacian_has_correct_size(self):
        l = Pyramid(self._images, self._config).laplacian_pyramid(self._depth)
        # pyramid height size depth+1
        self.assertEquals(len(l), self._depth + 1)
        #test larger images on top
        self.assertGreater(l[0][0].shape, l[1][0].shape)
        # zero level of p - the input
        self.assertEquals(l[0][0].shape, self._array.shape)  # first image
        # size of first level is half of first
        self.assertEquals(l[1][0].shape, (2, 2))  # first image
        #top level of laplacian pyrami is the same as top of gaussian

    def test_top_level_of_laplacian_and_gaussian_pyramids_are_the_same(self):
        l = Pyramid(self._images, self._config).laplacian_pyramid(self._depth)
        p = Pyramid(self._images, self._config).gaussian_pyramid(self._depth)
        #top level
        self.assertEquals(l[self._depth][0][:][:], p[self._depth][0][:][:])
        #other level
        self.assertNotIn(l[self._depth-1][0][:][:], p[self._depth-1][0][:][:])



