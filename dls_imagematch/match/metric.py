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
            img = self.get_absdiff_metric_image(transform)

            imgs.append(img)
            # avg abs diff per pixel
            metrics.append(np.sum(img) / img.size)

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
            #ref.paste(overlay, xOff=x+(w-overlay.size[0]), yOff=y+(h-overlay.size[1]))
            ref.paste(overlay, xOff=max(x,0), yOff=max(y,0))
            ref.draw_rectangle(roi)
            ref.save("rect")

        #return best_transform, best_img, is_identity
        return best_transform, ref.img, is_identity



    def get_absdiff_metric_image(self, transformation):
        #cr1, cr2 = self._get_comparison_regions(transformation)
        cr1, cr2 = self._get_comparison_regions_NEW(transformation)

        if self.DEBUG:
            Image(cr1, self.img_a.real_size[0]).save("Comparison_Region_A")
            Image(cr2, self.img_a.real_size[0]).save("Comparison_Region_B")

        return cv2.absdiff(cr1, cr2)


    def _get_comparison_regions_NEW(self, transform):
        """ Assumes that the region shown in the 'mov_img' is completely contained within the reference image
        """
        ref_img = self.img_a.img
        mov_img = self.img_b.img

        r_width, r_height = self.img_a._size()
        m_width, m_height = self.img_b._size()

        if not self.translation_only:
            raise NotImplementedError

        else:
            tr_matrix = transform(self.img_b._size())
            xOff, yOff = map(int, get_translation_amounts(tr_matrix))

            rx1 = max(xOff, 0)
            ry1 = max(yOff, 0)
            rx2 = min(xOff+m_width, r_width)
            ry2 = min(yOff+m_height, r_height)

            # Paste location is totally outside image
            if rx1 > rx2 or ry1 > ry2:
                raise Exception("mov_img outside ref_img area")

            # Overlap rectangle in source image coordinates
            sx1 = rx1 - xOff
            sy1 = ry1 - yOff
            sx2 = rx2 - xOff
            sy2 = ry2 - yOff

            ref_img = ref_img[ry1:ry2, rx1:rx2]
            mov_img = mov_img[sy1:sy2, sx1:sx2]

            #ref_img = ref_img[y:h+y, x:w+x]

        # TODO: if the move image is more than X% outside the reference image, fail the trial
        return ref_img, mov_img


    def _get_comparison_regions(self, transform):
        """Return cropped images, a transform having been applied to the latter.

        `crop` is a list of proportions to discard from the top, bottom, left and
        right (respectively) of both images before returning.

        If `px_translation` is `True` then only translational components of the
        transform are applied, which is a very cheap operation. Otherwise a full
        affine transform is applied.
        """
        ref_img = self.img_a.img
        mov_img = self.img_b.img

        t, b, l, r = self.crop_amounts
        working_size = self.img_b._size()
        w, h = working_size

        # Turn proportions into absolute amounts.
        t, b, l, r = map(int, [t*h, b*h, l*w, r*w])

        ref_img = ref_img[t:-b, l:-r]  # Crop the reference.
        # (Slicing numpy arrays like this is cheap.)

        tr_matrix = transform(working_size)

        if not self.translation_only:  # We must do a "proper" affine transform.
            if self.DEBUG:
                Image(apply_tr(tr_matrix, mov_img), self.img_b.real_size[0]).save("mov_trans")

            mov_img = apply_tr(tr_matrix, mov_img)[t:-b, l:-r]

        else:  # Work with img in-place (no deep copy).
            # Extract translation distances from the matrix.
            x, y = map(int, get_translation_amounts(tr_matrix))

            # Find the desired overlap region.
            # TODO: Document this better.
            #krw: the double slice notation: arr[a:b, c:d][e:f, g:h] is equivalent to (arr[a:b, c:d])[e:f, g:h].
            # i.e. we are taking a slice of the 2D array and then taking a slice of the array that results
            if x >= 0 and y >= 0:
                x = min(x, l);  y = min(y, t)  # img must cover region of interest!
                mov_img = mov_img[:h-y, :w-x][t-y:h-y-b, l-x:w-x-r]
            elif y >= 0:
                x = max(x, -r);  y = min(y, t)
                mov_img = mov_img[:h-y, -x:][t-y:h-y-b, l:w-r]
            elif x >= 0:
                x = min(x, l);  y = max(y, -b)
                mov_img = mov_img[-y:, :w-x][t:h-b, l-x:w-x-r]
            else:
                x = max(x, -r);  y = max(y, -b)
                mov_img = mov_img[-y:, -x:][t:h-b, l:w-r]

        return ref_img, mov_img


def get_translation_amounts(tr_mat):
    return map(lambda i: tr_mat[i, 2], (0, 1))

def apply_tr(transform, img):
    """Apply an affine transform to an image and return the result.

    `transform` can be an affine transform matrix or a Transform object.
    `img` can be colour or greyscale.

    This function is expensive and its use should be avoided if possible.
    """
    working_size = get_size(img.img)

    if hasattr(transform, '__call__'):  # We need a matrix.
        transform = transform(working_size)

    return cv2.warpAffine(img.img, transform, working_size)

def get_size(img):
    """Return the size of an image in pixels in the format [width, height]."""
    if img.ndim == 3:  # Colour
        working_size = img.shape[::-1][1:3]
    else:
        assert img.ndim == 2  # Greyscale
        working_size = img.shape[::-1]
    return working_size
