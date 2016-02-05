import cv2
import numpy as np

import dls_imagematch.util.transforms as tlib  # Contains `Transform` class.


class OverlapMetric:

    def __init__(self, img_a, img_b, crop_amounts, translation_only):
        self.img_a = img_a
        self.img_b = img_b
        self.crop_amounts = crop_amounts
        self.translation_only = translation_only
        pass


    def best_transform(self, trial_transforms, new_size, net_transform):
        """ For a TrialTransforms object, return the transform which has the
        minimum metric value.
        """
        net_transforms = trial_transforms.compose_with(net_transform)

        imgs = []
        metrics = []

        for tr in net_transforms:
            matrix = tr(new_size)
            img = self.get_absdiff_metric_image(matrix)

            imgs.append(img)
            metrics.append(np.sum(img))

        best = np.argmin(metrics)
        best_transform = net_transforms[best]
        best_img = imgs[best]

        is_identity = best == 0

        return best_transform, best_img, is_identity


    def get_absdiff_metric_image(self, transformation):
        cr1, cr2 = self._get_comparison_regions(transformation)
        return cv2.absdiff(cr1, cr2)


    def _get_comparison_regions(self, transform):
        """Return cropped images, a transform having been applied to the latter.

        `crop` is a list of proportions to discard from the top, bottom, left and
        right (respectively) of both images before returning.

        If `px_translation` is `True` then only translational components of the
        transform are applied, which is a very cheap operation. Otherwise a full
        affine transform is applied.
        """
        ref_img = self.img_a.img
        img = self.img_b.img

        t, b, l, r = self.crop_amounts
        working_size = self.img_b.size()
        w, h = working_size

        # Turn proportions into absolute amounts.
        t, b, l, r = map(int, [t*h, b*h, l*w, r*w])

        ref_img = ref_img[t:-b, l:-r]  # Crop the reference.
        # (Slicing numpy arrays like this is cheap.)


        if not self.translation_only:  # We must do a "proper" affine transform.
            img = apply_tr(transform, img)[t:-b, l:-r]

        else:  # Work with img in-place (no deep copy).
            if isinstance(transform, tlib.Transform):  # We need a matrix.
                transform = transform(working_size)

            # Extract translation distances from the matrix.
            x, y = map(int, get_translation_amounts(transform))

            # Find the desired overlap region.
            # TODO: Document this better.
            if x >= 0 and y >= 0:
                x = min(x, l);  y = min(y, t)  # img must cover region of interest!
                img = img[:h-y, :w-x][t-y:h-y-b, l-x:w-x-r]
            elif y >= 0:
                x = max(x, -r);  y = min(y, t)
                img = img[:h-y, -x:][t-y:h-y-b, l:w-r]
            elif x >= 0:
                x = min(x, l);  y = max(y, -b)
                img = img[-y:, :w-x][t:h-b, l-x:w-x-r]
            else:
                x = max(x, -r);  y = max(y, -b)
                img = img[-y:, -x:][t:h-b, l:w-r]

        return ref_img, img


def get_translation_amounts(tr_mat):
    return map(lambda i: tr_mat[i, 2], (0, 1))

def apply_tr(transform, img):
    """Apply an affine transform to an image and return the result.

    `transform` can be an affine transform matrix or a Transform object.
    `img` can be colour or greyscale.

    This function is expensive and its use should be avoided if possible.
    """
    working_size = get_size(img)

    if hasattr(transform, '__call__'):  # We need a matrix.
        transform = transform(working_size)

    return cv2.warpAffine(img, transform, working_size)

def get_size(img):
    """Return the size of an image in pixels in the format [width, height]."""
    if img.ndim == 3:  # Colour
        working_size = img.shape[::-1][1:3]
    else:
        assert img.ndim == 2  # Greyscale
        working_size = img.shape[::-1]
    return working_size
