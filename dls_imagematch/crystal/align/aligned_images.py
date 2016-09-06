from dls_imagematch.util import Color, Point
from .metric_overlap import OverlapMetric
from .overlay import Overlayer


class AlignedImages:
    """ Represents a pair of images on which an alignment operation has been performed. The images should
    have the same real size per pixel. The translate is the distance (in pixels) that the top-left corner
    of image B should be offset from the top-left corner of image A, in order to properly align the images.
    """
    def __init__(self, image1, image2, translate, align_config, method="Unknown"):
        self.image1 = image1
        self.image2 = image2
        self.translate = translate
        self.method = method

        self._limit_low = align_config.metric_limit_low.value()
        self._limit_high = align_config.metric_limit_high.value()

        self._real_offset = None
        self._pixel_offset = None
        self._real_center = None
        self._pixel_center = None
        self._overlay = None
        self._metric = None
        self._overlap_images = None

    def is_alignment_good(self):
        """ If True the alignment metric is less than the low limit and the alignment is considered to
        be a good fit. """
        metric = self.overlap_metric()
        return metric <= self._limit_low

    def is_alignment_poor(self):
        """ If True the alignment metric is between the 2 limits and the alignment is considered to be poor. """
        metric = self.overlap_metric()
        return self._limit_low < metric <= self._limit_high

    def is_alignment_bad(self):
        """ If True, the alignment quality metric exceeds the top limit and the alignment is considered
        to have failed. """
        metric = self.overlap_metric()
        return metric > self._limit_high

    def pixel_offset(self):
        """ The transform (offset) in pixels - nearest whole number. """
        if self._pixel_offset is None:
            self._pixel_offset = Point(int(round(self.translate.x, 0)), int(round(self.translate.y, 0)))

        return self._pixel_offset

    def real_offset(self):
        """ The transform in real units (um) with no rounding. """
        if self._real_offset is None:
            x, y = self.translate.x, self.translate.y
            pixel_size = self.image1.pixel_size()
            self._real_offset = Point(x * pixel_size, y * pixel_size)

        return self._real_offset

    def pixel_center(self):
        """ The position of the center of image B (in image A coordinates) - in pixels. """
        if self._pixel_center is None:
            width, height = self.image2.size()
            x, y = self.translate.x + width / 2, self.translate.y + height / 2
            x, y = int(round(x)), int(round(y))
            self._pixel_center = Point(x, y)

        return self._pixel_center

    def real_center(self):
        """ The position of the center of image B (in image A coordinates) - in pixels. """
        if self._real_center is None:
            width, height = self.image2.size()
            x, y = self.translate.x + width / 2, self.translate.y + height / 2
            self._real_center = Point(x, y)

        return self._real_center

    def overlay(self, rect_color=Color.Black()):
        """ An image which consists of Image A with the overlapping regions of Image B in a 50:50 blend. """
        if self._overlay is None:
            self._overlay = Overlayer.create_overlay_image(self.image1, self.image2, self.translate, rect_color)

        return self._overlay

    def overlap_metric(self):
        """ Metric which gives an indication of the quality of the alignment (lower is better). """
        if self._metric is None:
            metric_calc = OverlapMetric(self.image1, self.image2, None)
            self._metric = metric_calc.calculate_overlap_metric(self.translate)

        return self._metric

    def overlap_images(self):
        """ Two images which are the sub-regions of Images A and B which overlap. """
        if self._overlap_images is None:
            region_a, region_b = Overlayer.get_overlap_regions(self.image1, self.image2, self.pixel_offset())
            self._overlap_images = (region_a, region_b)

        return self._overlap_images
