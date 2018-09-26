from pkg_resources import require

from dls_focusstack.focus.pyramid import collapse

require('pygelf==0.2.11')
require("numpy==1.11.1")
require("scipy")

from unittest import TestCase

import numpy as np

from dls_focusstack.focus.pyramid_manager import PyramidManager

from mock import MagicMock


class TestPyramidManager(TestCase):

    def setUp(self):
        #case1
        self._config = MagicMock()
        self._array = np.array([[10, 20, 30, 40], [10, 20, 30, 40], [11, 21, 31, 41], [12, 22, 32, 42]],
                               dtype=np.float64)
        self._depth = 2
        self._images = np.array([self._array, self._array / 10])
        #case2
        self._array1 = np.array([[10, 20, 30], [10, 20, 30], [11, 21, 31], [12, 22, 32]],
                               dtype=np.float64)
        self._images1 = np.array([self._array1, self._array1 / 10])


    def test_gaussian_pyramid_has_correct_size(self):
        #gaussian pyramid
        p = PyramidManager(self._images, self._config)._gaussian_pyramid(self._depth).get_pyramid_array()
        #piramid hight size depth+1
        self.assertEqual(len(p), self._depth+1)
        #zero level of p - the input
        self.assertEquals(p[0][0].shape, self._array.shape) #first image
        self.assertEquals(p[0][1].shape, self._array.shape) #second image
        #size of first level is half of first
        self.assertEquals(p[1][0].shape, (2,2)) #first image
        self.assertEquals(p[1][1].shape, (2,2))  #second image
        #size of second level one fought of first
        self.assertEquals(p[2][1].shape, (1,1))
        #zero level of the pyramid is made out of input images
        self.assertEquals(p[0][0][0][0], 10)

    def test_laplacian_has_correct_size(self):
        l = PyramidManager(self._images, self._config).laplacian_pyramid(self._depth).get_pyramid_array()
        # pyramid height size depth+1
        self.assertEquals(len(l), self._depth + 1)
        #test larger images on level zero
        self.assertGreater(l[0][0].shape, l[1][0].shape)
        # zero level of p - the input
        self.assertEquals(l[0][0].shape, self._array.shape)  # first image
        # size of first level is half of first
        self.assertEquals(l[1][0].shape, (2, 2))  # first image
        #top level of laplacian pyrami is the same as top of gaussian
        l1 = PyramidManager(self._images1, self._config).laplacian_pyramid(self._depth).get_pyramid_array()
        # pyramid height size depth+1
        self.assertEquals(len(l1), self._depth + 1)

    def test_top_level_of_laplacian_and_gaussian_pyramids_are_the_same(self):
        l = PyramidManager(self._images, self._config).laplacian_pyramid(self._depth).get_pyramid_array()
        p = PyramidManager(self._images, self._config)._gaussian_pyramid(self._depth).get_pyramid_array()
        #top level
        self.assertEquals(l[self._depth][0][:][:], p[self._depth][0][:][:])
        #other level
        self.assertNotIn(l[self._depth-1][0][:][:], p[self._depth-1][0][:][:])

    def test_that_the_top_of_pyramids_has_the_lowest_resolution(self):
        l = PyramidManager(self._images, self._config).laplacian_pyramid(self._depth).get_pyramid_array()
        p = PyramidManager(self._images, self._config)._gaussian_pyramid(self._depth).get_pyramid_array()
        # top level has lowest resolution
        self.assertLess(l[self._depth][0][:][:].shape, l[self._depth - 1][0][:][:].shape)
        # top level has lowest resolution
        self.assertLess(p[self._depth][0][:][:].shape, p[self._depth - 1][0][:][:].shape)


    def test_collapse_returns_an_array_of_the_same_size_as_the_bottom_level(self):
        pyr_manager = PyramidManager(self._images, self._config)
        fused = [self._array]
        fused.append(np.array([[30, 40], [30, 40], [31, 41], [32, 42]], dtype=np.float64))
        result = collapse(fused)
        self.assertEquals(result.shape, self._array.shape)

    #the elements of upper level are all the same - pyrUp just extends the size the values stay the same
    def test_collapse_returns_sum_of_a_level_and_extended_upper_level(self):
        pyr_manager = PyramidManager(self._images, self._config)
        fused = [np.array([[2, 1], [1, 1], [1, 1], [1, 0]], dtype=np.float64)]
        fused.append(np.array([[2, 2], [2, 2]], dtype=np.float64))
        result = collapse(fused)
        test = np.array([[4, 3], [3, 3], [3, 3], [3, 2]],  dtype=np.float64)
        self.assertIn(result, test)
        self.assertEquals(result[1][1], test[1][1])
        self.assertEquals(result[0][0], test[0][0])

    def test_get_pyramid_fusion_calls_once_laplacian_pyramid_and_collapse(self):
        self._config.pyramid_min_size.value.return_value = 1
        p = PyramidManager(self._images, self._config)
        p.laplacian_pyramid = MagicMock(return_value = MagicMock())
        p.collapse = MagicMock()
        p.get_pyramid_fusion()
        collapse.assert_called_once()
        p.laplacian_pyramid.assert_called_once()
