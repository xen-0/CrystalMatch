from unittest import TestCase

from mock import MagicMock

from focus.pyramid import Pyramid


class TestPyramid(TestCase):

    def test_generating_kernel_returns_correct_values(self):
        images = MagicMock()
        config = MagicMock()

        p = Pyramid(images,config)

        kernel = p.generating_kernel(0.4)
        self.assertEqual(kernel[0][0], 1/256)

