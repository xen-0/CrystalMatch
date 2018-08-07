from unittest import TestCase

from mock import MagicMock, Mock

import focus
from focus.image_fft_manager import ImageFFTManager


class TestImageFFTManager(TestCase):

    def setUp(self):
        file1= MagicMock()
        file2 = MagicMock()
        self._file_list = [file1, file2]


    def test_read_ftt_images(self):
        imgFFTman = ImageFFTManager(self._file_list).read_ftt_images()


    def test_get_fft_images(self):
        self.fail()
