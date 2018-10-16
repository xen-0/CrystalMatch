from pkg_resources import require
require('pygelf')
require("numpy==1.11.1")
require("scipy")

import cv2
import os
from unittest import TestCase

from mock import MagicMock, Mock
from dls_focusstack.focus.focus_stack_lap_pyramid import FocusStack


class TestFocusStackLapPyramid(TestCase):

    def test_focus_stack_results_in_one_rgb_image_of_input_image_size(self):
        self._file1 = MagicMock()
        self._file2 = MagicMock()
        CONFIG_DIR = os.path.join("config")
        dict = os.path.join("test-images", "Focus", "VMXI-AA0019-H01-1-R0DRP1", "levels")
        self._file1.name = os.path.join(dict, "FL1.tif")
        self._file2.name = os.path.join(dict, "FL2.tif")
        file_list = [self._file1, self._file2]
        fs = FocusStack(file_list, CONFIG_DIR)
        result_img = fs.composite()

        self.assertIsNotNone(result_img)
        img = cv2.imread(self._file1.name)
        self.assertEqual(result_img.channels(), 3) #rgb
        self.assertEqual(result_img.size(), (img.shape[1],img.shape[0]))

