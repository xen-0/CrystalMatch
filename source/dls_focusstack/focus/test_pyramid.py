from pkg_resources import require

require("numpy==1.11.1")
require("scipy")
from unittest import TestCase

from dls_focusstack.focus.pyramid_manager import PyramidManager
from dls_focusstack.focus.pyramid import fused_laplacian, entropy_diviation

import numpy as np
from multiprocessing import Queue
from mock import MagicMock


class TestPyramid(TestCase):

    def setUp(self):
        #case1
        self._config = MagicMock()
        self._array = np.array([[10, 20, 30, 40], [10, 20, 30, 40], [11, 21, 31, 41], [12, 22, 32, 42]],
                               dtype=np.float64)
        self._depth = 2
        self._images = np.array([self._array, self._array / 10])

        self._pyramid = PyramidManager(self._images, self._config).laplacian_pyramid(self._depth)
        self._kernel_size = 5

    def test_fuse_does_not_change_the_depth_of_the_pyramid(self):
        fused = self._pyramid.fuse(self._kernel_size)
        self.assertEquals(len(fused), self._depth+1)

    def test_fuse_flattens_the_pyramid_along_images(self):
        #original size level zero
        self.assertEqual(self._pyramid.get_pyramid_array()[0].shape, (2,4,4))
        fused = self._pyramid.fuse(self._kernel_size)
        #size after fusion level zero
        self.assertEqual(fused[0].shape, self._array.shape)

    def test_fused_laplacian_of_level0_has_size_of_input_array(self):
        laplacians_level0 = self._pyramid.get_pyramid_array()[0]
        q = Queue()
        fused_laplacian(laplacians_level0, self._pyramid.get_region_kernel(),q)
        fused_level = q.get()
        self.assertEquals(fused_level.shape, self._array.shape)

    def test_fused_laplacian_picks_the_layer_with_high_region_energy_from_given_level(self):
        laplacians_level0 = self._pyramid.get_pyramid_array()[0]
        q = Queue()
        fused_laplacian(laplacians_level0, self._pyramid.get_region_kernel(), q)
        fused_level = q.get()
        #layer 0 has the highiest region energy as all the values are 10 times larger than layer1
        self.assertIn(laplacians_level0[0], fused_level)

    def test_entropy_deviation_calls_entropy_abd_deviation_once(self):
        layer = MagicMock()
        q = MagicMock()
        entropy_diviation(layer, self._pyramid.get_region_kernel(),q)

        layer.entropy.assert_called_once()
        layer.deviation.assert_called_once()












