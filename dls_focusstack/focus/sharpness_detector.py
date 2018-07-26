import logging

IMG_TO_STACK = 12 #how many images will be stacked

class SharpnessDetector(object):
    """Class which applies the result of image FFT calculation to find images which will be stacked.
    This is an initial filtering step used currently in the process."""

    def __init__(self, img_fft):
        self.fft_img = img_fft

    def images_to_stack(self):
        """Function which finds the maximum of mean FFT values provided.
        It uses the maximum value to pick a subset of images from an initial set.
        The subset is later used by the stacking algorithm (pyramid) to create the all-in-focus-image.
        The number of images to stack is defined by IMG_TO_STACK"""
        level = 0
        max = None
        images = []
        for s in self.fft_img:
            fft = s.getFFT()
            if fft > level:
                level = fft
                max = s.getImageNumber()
        logger = logging.getLogger(__name__)
        logger.debug("Image: " + str(max) + " has best value of FFT: " + str(level))
        range = self.find_range(max)

        for s in self.fft_img:
            if s.getImageNumber() in range:
                images.append(s.getImage())

        logger.debug("First image number : " + str(range[0])  + " last image number : " + str(len(range)) + " added to stack" )

        return images

    def find_range(self, max):
        """Function which defines the range of images to stack."""
        n = len(self.fft_img)
        if IMG_TO_STACK >= n:
            return range(1, IMG_TO_STACK)
        elif max -(IMG_TO_STACK / 2) < 1:
            return range(1, IMG_TO_STACK)
        elif max + (IMG_TO_STACK / 2) > n:
            return range(-IMG_TO_STACK, n)
        else:
            return range(max - IMG_TO_STACK / 2, max + IMG_TO_STACK / 2)
