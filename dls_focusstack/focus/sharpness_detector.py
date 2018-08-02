import logging
import logconfig

#logging.getLogger(__name__).addHandler(logging.NullHandler())

class SharpnessDetector(object):
    """Class which applies the result of image FFT calculation to find images which will be stacked.
    This is an initial filtering step used currently in the process."""

    def __init__(self, img_fft, config):
        self.fft_img = img_fft
        self.config = config

    def images_to_stack(self):
        """Function which finds the maximum of mean FFT values provided.
        It uses the maximum value to pick a subset of images from an initial set.
        The subset is later used by the stacking algorithm (pyramid) to create the all-in-focus-image.
        The number of images to stack is defined by IMG_TO_STACK"""
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        level = 0
        max = None
        images = []
        for s in self.fft_img:
            fft = s.getFFT()
            if fft > level:
                level = fft
                max = s.getImageNumber()

        range = self.find_range(max)

        log.info("Stacking " + str(self.config.number_to_stack.value()) + " images " +
                 " Image: " + str(max) + " has best value of FFT: " + str(level) +
                 " First img: " + str(range[0]) + " last img: " + str(len(range)))

        for s in self.fft_img:
            if s.getImageNumber() in range:
                images.append(s.getImage())

        return images

    def find_range(self, max):
        """Function which defines the range of images to stack."""
        n = len(self.fft_img)
        num_to_stuck = self.config.number_to_stack.value()
        if num_to_stuck >= n:
            return range(1, num_to_stuck)
        elif max -(num_to_stuck / 2) < 1:
            return range(1, num_to_stuck)
        elif max + (num_to_stuck / 2) > n:
            return range(-num_to_stuck, n)
        else:
            return range(max - num_to_stuck / 2, max + num_to_stuck / 2)
