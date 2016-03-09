import cv2
import numpy as np

import dls_imagematch.util.transforms as tlib  # Contains `Transform` class.
from dls_imagematch.match.image import Image


class OverlapMetric:

    def __init__(self, img_a, img_b, translation_only):
        self.img_a = img_a
        self.img_b = img_b
        self.crop_amounts = None
        self.translation_only = translation_only

        self.DEBUG = False

    def best_transform(self, trial_transforms, scaled_size, net_transform):
        """ For a TrialTransforms object, return the transform which has the
        minimum metric value.
        """
        net_transforms = trial_transforms.compose_with(net_transform)

        imgs = []
        metrics = []

        for transform in net_transforms:
            tr_matrix = transform(self.img_b.size)
            offset = map(int, get_translation_amounts(tr_matrix))
            metric, absdiff_img = self.calculate_overlap_metric(self.img_a, self.img_b, offset)
            imgs.append(absdiff_img)
            metrics.append(metric)

        best = np.argmin(metrics)
        best_transform = net_transforms[best]
        best_img = imgs[best]

        is_identity = (best == 0)

        # Paste the abs_diff img onto the ref image and highlight the area
        if self.DEBUG:
            ref = self.img_a.copy()
            working_size = self.img_b._size()
            w, h = working_size
            tr_matrix = best_transform(working_size)
            x, y = map(int, get_translation_amounts(tr_matrix))
            roi = (x, y, x+w, y+h)
            overlay = Image(best_img, self.img_b.pixel_size)
            ref.paste(overlay, xOff=max(x,0), yOff=max(y,0))
            ref.draw_rectangle(roi)
            ref.save("rect")

        return best_transform, ref.img, is_identity


    @staticmethod
    def calculate_overlap_metric(imgA, imgB, offset):
        """ For two images, A and B, where B is offset relative to A, calculate the average
        per pixel absolute difference of the region of overlap of the two images.

        Return the value of this metric as well as an image showing the per pixel absolute
        differences. In the returned image, darker areas indicate greater differences in the
        overlap whereas lighter areas indeicate more similarity.
        """
        xOffset, yOffset = offset
        cr1, cr2 = OverlapMetric.get_overlap_regions(imgA, imgB, xOffset, yOffset)

        # DEBUG printouts
        Image(cr1, imgA.pixel_size).save("Comparison_Region_A")
        Image(cr2, imgB.pixel_size).save("Comparison_Region_B")

        absdiff_img = cv2.absdiff(cr1, cr2)
        metric = np.sum(absdiff_img) / absdiff_img.size

        # Invert image so that similarities are light and differences are dark.
        inverted = 255-absdiff_img

        return metric, inverted


    @staticmethod
    def get_overlap_regions(imgA, imgB, xOff, yOff):
        """ For the two images, A and B, where the position of B is offset from that of A,
        return two new images that are the overlapping segments of the original images.

        As a simple example, if image B is smaller than A and it is completely contained
        within the borders of the image A, then we will simply return the whole of image B,
        and the section of image A that it overlaps. e.g., if A is 100x100 pixels, B is
        14x14 pixels, and the offset is (x=20, y=30), then the returned section of A will
        be (20:34, 30:44).

        If image B only partially overlaps image A, only the overlapping sections of each
        are returned.
        """
        # Determine size of images
        width_a, height_a = imgA.size
        width_b, height_b = imgB.size

        # Corners (top-left, bottom-right) of the overlap rectangle for image A
        x1_a = max(xOff, 0)
        y1_a = max(yOff, 0)
        x2_a = min(xOff+width_b, width_a)
        y2_a = min(yOff+height_b, height_a)

        # Corners of the overlap rectangle for image B
        x1_b = x1_a - xOff
        y1_b = y1_a - yOff
        x2_b = x2_a - xOff
        y2_b = y2_a - yOff

        # TODO: if the mov_img is more than X% outside the reference image, fail the trial
        # Error if paste location is totally outside image
        if x1_a > x2_a or y1_a > y2_a:
            raise Exception("mov_img outside ref_img area")

        # Get overlap sections of each image
        overlap_a = imgA.img[y1_a:y2_a, x1_a:x2_a]
        overlap_b = imgB.img[y1_b:y2_b, x1_b:x2_b]

        return overlap_a, overlap_b

def get_translation_amounts(tr_mat):
    return map(lambda i: tr_mat[i, 2], (0, 1))