import cv2
import logging
import numpy as np
from os.path import join

from config.focus_config import FocusConfig
from dls_imagematch.crystal import ImageAligner, AlignConfig
from dls_imagematch.feature.detector import DetectorType, DetectorConfig
from dls_imagematch.feature.detector.factory import DetectorFactory
from dls_util.imaging import Image
from dls_util.shape import Rectangle, Point

LAPLACE_VAR = 96.8


class FocusStack:
    CONFIG_FILE_NAME = "focus_stack.ini"

    def __init__(self, image_file_list, config_dir):
        self._image_file_list = image_file_list
        self._config = FocusConfig(join(config_dir, self.CONFIG_FILE_NAME))

    def composite(self):
        """ Finds the points of best focus in all images and produces a merged result """
        cfg = self._config

        # Convert images to util Image class
        images = []
        for file_obj in self._image_file_list:
            img = Image.from_file(file_obj.name)
            img = img.crop(Rectangle(Point(200,500), Point(2500,2500)))
            laplace_var = self._variance_of_laplacian(img)
            if laplace_var > LAPLACE_VAR: #not blurred
                print(laplace_var, file_obj.name)
                images.append(img)


        #align_images = self.align_images(images)
        align_images = images

        kernel_size = cfg.kernel_size.value()
        blur_radius = cfg.blur_radius.value()
        laplacians = self._compute_laplacians(align_images, kernel_size, blur_radius)

        focused_image = self._determine_focused_pixels(align_images, laplacians)

        return focused_image

    @staticmethod
    def _variance_of_laplacian(image):
        # compute the Laplacian of the image and then return the focus
        # measure, which is simply the variance of the Laplacian
        return cv2.Laplacian(image.to_mono().raw(), cv2.CV_64F).var()

    @staticmethod
    def _compute_laplacians(images, kernel_size, blur_size):
        """ Compute the gradient map of the image """

        logging.info("Computing the laplacian of the blurred images")
        laps = []
        for i in range(len(images)):
            logging.info("Lap {}".format(i))
            image = images[i].to_mono().raw()
            blurred = cv2.GaussianBlur(image, (blur_size, blur_size), 0)
            result = cv2.Laplacian(blurred, cv2.CV_64F, ksize=kernel_size)
            laps.append(result)

        laps = np.asarray(laps)
        logging.debug("Shape of array of laplacians = {}".format(laps.shape))

        return laps

    @staticmethod
    def _determine_focused_pixels(images, laplacians):

        max_values = laplacians[0].copy()
        for i in range(1, len(laplacians)):
            max_values = np.maximum(max_values, laplacians[i])

        output = images[0].raw().copy()
        for i in range(len(laplacians)):
            mask = laplacians[i] == max_values
            mask = np.reshape(np.repeat(mask, 3), output.shape) #pogrubia maske
            output = np.where(mask, images[i].raw(), output) #nadpisuje - bierze pixel z ostatniegdobego obazka

        return Image(output)


    #
    #   Align the images so they overlap properly...
    #
    #
    def align_images(self, images):

        #   SIFT generally produces better results, but it is not FOSS, so chose the feature detector
        #   that suits the needs of your project.  ORB does OK


        outimages = []

        base_img = images[0]
        align_config = AlignConfig('config')
        detectorConfig = DetectorConfig('config')
        outimages.append(base_img)
        for i in range(1, len(images)):
            print "Aligning image {}".format(i)
            #cv2.namedWindow('base' + str(i), cv2.WINDOW_NORMAL)
            #cv2.namedWindow('base' + str(i), 600)
            #tr1 = cv2.bitwise_and(base_img.raw(),images[i].raw())
            #cv2.imshow('base' + str(i), tr1)
            #cv2.waitKey(0)

            aligner = ImageAligner(base_img, images[i], align_config, detectorConfig)
            match_result = aligner._perform_match(DetectorType.SURF)
            aligned_images = aligner._generate_alignment(match_result, DetectorType.FAST)
            outimages.append(aligned_images.image2)
            tr = cv2.absdiff(base_img.raw(), aligned_images.image2.raw())
            #tr = cv2.bitwise_and(base_img.raw(), aligned_images.image2.raw())
            #cv2.namedWindow('t'+str(i), cv2.WINDOW_NORMAL)
            #cv2.namedWindow('t'+str(i), 600)
            #cv2.imshow('t'+str(i), tr)
            #cv2.waitKey(0)


        return outimages
