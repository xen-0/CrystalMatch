from pkg_resources import require

from focus import image_fft_manager

require("scipy")

from unittest import TestCase

from mock import MagicMock

from focus.image_fft_manager import ImageFFTManager
import os

class TestImageFFTManager(TestCase):

    def setUp(self):
        self._file1= MagicMock()
        self._file2 = MagicMock()

        dict = os.path.join(os.sep, "home", "rqq82173","PycharmProjects", "CrystalMatch","test-images", "Focus", "VMXI-AA0019-H01-1-R0DRP1", "levels")
        self._file1.name = os.path.join(dict, "FL1.tif")
        self._file2.name = os.path.join(dict, "FL2.tif")
        file_list = [self._file1, self._file2]
        self._imgFFTmanEmpty = ImageFFTManager(file_list)
        self._imgFFTman = ImageFFTManager(file_list)
        self._imgFFTman.read_ftt_images()

    def test_read_ftt_images_creates_list_of_two_fft_images_for_two_input_file_objects(self):
        self.assertEquals(len(self._imgFFTmanEmpty.fft_images), 0)
        self._imgFFTmanEmpty.read_ftt_images()
        self.assertEquals(len(self._imgFFTmanEmpty.fft_images), 2)

    def test_an_exception_is_raised_when_trying_to_read_a_file_which_does_not_exist(self):
        file3 = MagicMock()
        file3.name = "FL0"
        self.failUnlessRaises(ImageFFTManager([file3]))

    def test_get_fft_images_return_the_correct_field(self):
        self.assertEquals(self._imgFFTman.fft_images, self._imgFFTman.get_fft_images())

    def test_the_created_fft_images_contain_image_array(self):
        for fft_img in self._imgFFTman.get_fft_images():
            self.assertIsNotNone(fft_img.get_image())

    def test_the_created_fft_images_are_numbered_according_to_the_sequence_of_the_input_list(self):
        file_list = [self._file1, self._file2]
        manager = ImageFFTManager(file_list)
        manager.read_ftt_images()
        for idx, name in enumerate(file_list):
            for fft_img in manager.get_fft_images():
                if(fft_img.get_name() == name): #assuming the names are unique, which is not required
                    self.failUnlessEqual(fft_img.get_image_number, idx)

    def test_the_created_fft_images_contain_fft(self):
        for fft_img in self._imgFFTman.get_fft_images():
            self.assertIsNotNone(fft_img.getFFT())

    def test_q_put_called_once_by_fft_method(self):
        q =MagicMock()
        image_fft_manager.fft(self._file1, q, 10)
        q.put.assert_called_once()


