from unittest import TestCase

from mock.mock import create_autospec, MagicMock, patch

from dls_imagematch.crystal.align.aligner import ImageAligner
from dls_imagematch.crystal.align.sized_image import SizedImage


class TestImageAligner(TestCase):
    @staticmethod
    def create_aligner_with_mock_images(image_1_pixel_size, image_2_pixel_size, mock_sized_image):
        image1 = create_autospec(SizedImage, spec_set=True)
        image1.pixel_size = MagicMock(return_value=image_1_pixel_size)
        image2 = create_autospec(SizedImage, spec_set=True)
        image2.pixel_size = MagicMock(return_value=image_2_pixel_size)
        align_config = MagicMock()
        align_config.pixel_size_1.value = MagicMock(return_value=image_1_pixel_size)
        align_config.pixel_size_2.value = MagicMock(return_value=image_2_pixel_size)

        mock_sized_image.side_effect = [image1, image2]
        aligner = ImageAligner(image1, image2, align_config)
        return aligner, image1, image2

    def test_aligner_cannot_be_created_without_setting_config_file(self):
        # Setup
        image1 = create_autospec(SizedImage, spec_set=True)
        image2 = create_autospec(SizedImage, spec_set=True)
        self.failUnlessRaises(AssertionError, ImageAligner, image1, image2, None)

    @patch("dls_imagematch.crystal.align.sized_image.SizedImage.from_image")
    def test_smaller_image_1_is_rescaled_to_size_of_image_2(self, mock_sized_image):
        # Setup
        image_1_pixel_size = 2.5
        image_2_pixel_size = 5.0

        # Run Test
        aligner, image1, image2 = self.create_aligner_with_mock_images(image_1_pixel_size,
                                                                       image_2_pixel_size,
                                                                       mock_sized_image)

        # Test image1 is rescaled
        scale_factor = image_1_pixel_size / image_2_pixel_size
        image1.rescale.assert_called_with(scale_factor)

        # Test image2 is not rescaled
        image2.rescale.assert_not_called()

    @patch("dls_imagematch.crystal.align.sized_image.SizedImage.from_image")
    def test_larger_image_1_is_rescaled_to_size_of_image_2(self, mock_sized_image):
        # Setup
        image_1_pixel_size = 6.0
        image_2_pixel_size = 3.0

        # Run Test
        aligner, image1, image2 = self.create_aligner_with_mock_images(image_1_pixel_size,
                                                                       image_2_pixel_size,
                                                                       mock_sized_image)

        # Test image1 is rescaled
        scale_factor = image_1_pixel_size / image_2_pixel_size
        image1.rescale.assert_called_with(scale_factor)

        # Test image2 is not rescaled
        image2.rescale.assert_not_called()

    @patch("dls_imagematch.crystal.align.sized_image.SizedImage.from_image")
    def test_that_resolution_is_taken_from_image_2(self, mock_sized_image):
        # Setup
        image_1_pixel_size = 6.0
        image_2_pixel_size = 3.0

        # Run Test
        aligner, image1, image2 = self.create_aligner_with_mock_images(image_1_pixel_size,
                                                                       image_2_pixel_size,
                                                                       mock_sized_image)

        # Test internal value for resolution after initial config
        self.failUnlessEqual(image_2_pixel_size, aligner._resolution, "Resolution not set to pixel_size of image 2.")