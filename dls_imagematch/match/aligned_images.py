from .overlay import Overlayer
from .metric_overlap import OverlapMetric


class AlignedImages:
    def __init__(self, img_a, img_b, transform):
        self.img_a = img_a
        self.img_b = img_b
        self.transform = transform

        self._real_offset = None
        self._pixel_offset = None
        self._overlay = None
        self._metric = None

    def pixel_offset(self):
        if self._pixel_offset is None:
            self._pixel_offset = (int(round(self.transform.x, 0)), int(round(self.transform.y, 0)))

        return self._pixel_offset

    def real_offset(self):
        if self._real_offset is None:
            x, y = self.transform.x, self.transform.y
            pixel_size = self.img_a.pixel_size
            self._real_offset = (x * pixel_size, y * pixel_size)

        return self._real_offset

    def overlay(self):
        if self._overlay is None:
            self._overlay = Overlayer.create_overlay_image(self.img_a, self.img_b, self.transform)

        return self._overlay

    def overlap_metric(self):
        if self._metric is None:
            metric_calc = OverlapMetric(self.img_a, self.img_b, None)
            offset = (int(self.transform.x), int(self.transform.y))
            self._metric = metric_calc.calculate_overlap_metric(offset)

        return self._metric
