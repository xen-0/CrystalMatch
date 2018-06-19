import cv2
import numpy as np

from config.focus_config import FocusConfig
from dls_util.imaging import Image
from focus.pyramid import pyramid
from os.path import join


class FocusStack:
    CONFIG_FILE_NAME = "focus_stack.ini"

    def __init__(self, images, config_dir):
        self._image_file_list = images
        self._config = FocusConfig(join(config_dir, self.CONFIG_FILE_NAME))

    def composite(self):

        images = self.find_sharp()
        images = np.array(images, dtype=images[0].dtype)

        #TODO:Implement alignment algo
        aligned_images, gray_images = self.align(images)

        stacked_image = pyramid(aligned_images, self._config).get_pyramid_fusion()
        stacked_image  = cv2.convertScaleAbs(stacked_image)
        return Image(stacked_image)

    def find_sharp(self):
        images = []
        for file_obj in self._image_file_list:
            img = cv2.imread(file_obj.name)
            i = np.array(img, img.dtype)
            fourier = np.fft.fft(i)
            images.append(img)
        return images



    def align(self, images, iterations=5000, epsilon=1e-10):
        def _get_homography(image_1, image_2):
            warp_matrix = np.eye(3, 3, dtype=np.float32)
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iterations, epsilon)
            _, homography = cv2.findTransformECC(image_1, image_2, warp_matrix, cv2.MOTION_HOMOGRAPHY, criteria)
            return homography

        def _warp(image, shape, homography):
            return cv2.warpPerspective(image, homography, shape, flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

        def _convert_to_grayscale(image):
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        gray_images = np.zeros(images.shape[:-1], dtype=np.uint8)
        gray_image_shape = gray_images[0].shape[::-1]

        aligned_images = np.zeros(images.shape, dtype=images.dtype)

        aligned_images[0] = images[0]
        gray_images[0] = _convert_to_grayscale(images[0])
        for index in range(1, images.shape[0]):
            image2_gray = _convert_to_grayscale(images[index])
            # homography = _get_homography(gray_images[0], image2_gray)

            # gray_images[index] = _warp(image2_gray, gray_image_shape, homography)
            # aligned_images[index] = _warp(images[index], gray_image_shape, homography)

        # return aligned_images, gray_images
        return images, images