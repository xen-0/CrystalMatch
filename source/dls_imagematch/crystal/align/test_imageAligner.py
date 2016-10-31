from unittest import TestCase

from mock.mock import create_autospec, MagicMock

from dls_imagematch.crystal.align.aligner import ImageAligner
from dls_imagematch.crystal.align.sized_image import SizedImage


class TestImageAligner(TestCase):
    @staticmethod
    def create_aligner_with_mock_images(image_1_pixel_size, image_2_pixel_size):
        image1 = create_autospec(SizedImage, spec_set=True)
        image1.pixel_size = MagicMock(return_value=image_1_pixel_size)
        image2 = create_autospec(SizedImage, spec_set=True)
        image2.pixel_size = MagicMock(return_value=image_2_pixel_size)
        align_config = MagicMock()
        align_config.pixel_size_1.value = MagicMock(return_value=image_1_pixel_size)
        align_config.pixel_size_2.value = MagicMock(return_value=image_2_pixel_size)
        aligner = ImageAligner(image1, image2, align_config)

        # Static method used which return new image objects in aligner - override the assignment
        aligner._image1 = image1
        aligner._image2 = image2
        return aligner, image1, image2

    def test_aligner_cannot_be_created_without_setting_config_file(self):
        # Setup
        image1 = create_autospec(SizedImage, spec_set=True)
        image2 = create_autospec(SizedImage, spec_set=True)
        self.failUnlessRaises(AssertionError, ImageAligner, image1, image2, None)

    def test_smaller_image_1_is_rescaled_to_size_of_image_2(self):
        # Setup
        image_1_pixel_size = 2.5
        image_2_pixel_size = 5.0
        aligner, image1, image2 = self.create_aligner_with_mock_images(image_1_pixel_size, image_2_pixel_size)

        # Run test
        aligner._get_scaled_mono_images()

        # Test image1 is rescaled
        scale_factor = image_1_pixel_size / image_2_pixel_size
        image1.rescale.assert_called_with(scale_factor)

        # Test image2 is not rescaled
        image2.rescale.assert_not_called()

    def test_larger_image_1_is_rescaled_to_size_of_image_2(self):
        # Setup
        image_1_pixel_size = 6.0
        image_2_pixel_size = 3.0
        aligner, image1, image2 = self.create_aligner_with_mock_images(image_1_pixel_size, image_2_pixel_size)

        # Run test
        aligner._get_scaled_mono_images()

        # Test image1 is rescaled
        scale_factor = image_1_pixel_size / image_2_pixel_size
        image1.rescale.assert_called_with(scale_factor)

        # Test image2 is not rescaled
        image2.rescale.assert_not_called()
