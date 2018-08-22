import logging
import math

from dls_imagematch import logconfig


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
        best_fft_img = None
        images = []
        for s in self.fft_img:
            fft = s.getFFT()
            if fft > level:
                level = fft
                best_fft_img = s

        max = best_fft_img.get_image_number()
        range = self.find_range(max)

        extra = {'best_fft_val': round(level, 4),
                 'best_fft_img_num': max,
                 'stack_num': self.config.number_to_stack.value()}
        log = logging.LoggerAdapter(log, extra)
        log.info("Stacking " + str(self.config.number_to_stack.value()) + " images " +
                 " First img: " + str(range[0]) + " last img: " + str(range[-1]))

        for s in self.fft_img:
            if s.get_image_number() in range:
                images.append(s.get_image())

        return images

    def find_range(self, max):
        """Function which defines the range of images to stack."""
        n = len(self.fft_img)
        half_to_stack_ceil = self.ceil_when_uneven_number_of_image_passed()
        to_stack_ceil = 2 * half_to_stack_ceil
        if to_stack_ceil >= n: #take all images
            return range(0, n)
        elif max -(half_to_stack_ceil) < 0:
            return range(0, to_stack_ceil)
        elif max + (half_to_stack_ceil) > n:
            return range(n-to_stack_ceil+1, n+1) #last is n
        else:
            return range(max - half_to_stack_ceil, max + half_to_stack_ceil)

    def ceil_when_uneven_number_of_image_passed(self):
        num_to_stuck = self.config.number_to_stack.value()
        half_to_stack_ceil = int(math.ceil(float(num_to_stuck) / 2))  # take one more for uneven

        return  half_to_stack_ceil
