from unittest import TestCase

from pkg_resources import require

import focus
from focus.sharpness_detector import SharpnessDetector

require("numpy==1.11.1")


from mock import MagicMock

class TestSharpnessDetector(TestCase):

    def setUp(self):
        self._fft_images = MagicMock()
        self._config = MagicMock()
        self._fft_images.__len__= MagicMock(return_value = 20)


    def test_returns_correct_range_when_number_to_stack_even(self):
        max = 10
        number_to_stuck = 12
        self._config.number_to_stack.value = MagicMock(return_value = number_to_stuck)
        sd = SharpnessDetector(self._fft_images, self._config)
        range = sd.find_range(max)
        self.assertEqual(len(range), number_to_stuck)
        self.assertEqual(range[0], max - number_to_stuck / 2)
        self.assertEqual(range[number_to_stuck-1], max -1 + number_to_stuck / 2) #range dose not include the final number

    def test_returns_correct_range_when_number_to_stack_uneven(self):
        max = 10
        number_to_stuck = 11
        self._config.number_to_stack.value = MagicMock(return_value = number_to_stuck)
        sd = SharpnessDetector(self._fft_images, self._config)
        range = sd.find_range(max)
        self.assertEqual(len(range), number_to_stuck)
        self.assertEqual(range[0], max - number_to_stuck / 2)
        self.assertEqual(range[number_to_stuck-1], max -1 + number_to_stuck / 2) #range dose not include the final number
