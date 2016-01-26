from random import uniform

import numpy as np
import cv2


class Transform(object):
    """A coordinate-independent representation of a transformation in a plane.

    This is in contrast to an affine transformation matrix, which is defined
    for a particular image size.

    A `Transform` object should be called with a single argument,
    `working_size = (width, height)`, whereupon it returns an affine
    transformation matrix for the given working size.

    `Transform`s have four degrees of freedom: (left/right), (up/down),
    (zoom-in/zoom-out), (anticlockwise/clockwise), and obey a convention that
    translations are applied before other transformations. That is:
    `Transform(x, y, zoom, rot)` is equivalent to
    `Transform(0, 0, zoom, rot) * Transform(x, y, 0, 0)`, but not to
    `Transform(x, y, 0, 0) * Transform(0, 0, zoom, rot)`.
    """
    def __init__(self, horiz, vert, zoom, rot):
        """Define the scale-independent parameters for the transform.

        `horiz` and `vert` are translations as a proportion of image width and
        height respectively; `zoom` is a scale factor; and `rot` is an
        anticlockwise rotation, in degrees.
        """
        self.horiz = horiz
        self.vert = vert
        self.zoom = zoom
        self.rot = rot

    def __str__(self):
        return "Horizontal: {:.4f}; Vertical: {:.4f}; Zoom: {:.4f}; Rotation: {:.4f}"\
            .format(self.horiz, self.vert, self.zoom, self.rot)

    # Alternative constructors...
    @classmethod
    def identity(cls):
        return cls(0, 0, 1, 0)

    @classmethod
    def translation(cls, horiz, vert):
        return cls(horiz, vert, 1, 0)

    # Implementation...
    @staticmethod
    def __horiz_tr(working_size, distance):
        return np.float32([[1, 0, distance*working_size[0]],
                           [0, 1, 0]])

    @staticmethod
    def __vert_tr(working_size, distance):
        return np.float32([[1, 0, 0],
                           [0, 1, -distance*working_size[1]]])

    @staticmethod
    def __zoom_tr(working_size, factor):
        return np.float32([[factor, 0, working_size[0]*(1-factor)/2.0],
                           [0, factor, working_size[1]*(1-factor)/2.0]])

    @staticmethod
    def __rot_tr(working_size, angle):
        return cv2.getRotationMatrix2D(
            tuple([x/2 for x in working_size[::-1]]), angle, 1)

    @staticmethod
    def _compose_matrix_forms(b, a):
        second = np.append(b, [[0, 0, 1]], axis=0)
        first = np.append(a, [[0, 0, 1]], axis=0)
        return np.dot(second, first)[0:2, :]

    @staticmethod
    def _invert_matrix_form(tr_matrix):
        return np.linalg.inv(
            np.append(tr_matrix, [[0, 0, 1]], axis=0)
        )[0:2, :]

    def __call__(self, working_size):
        """Get a matrix representation.
        """
        return self._compose_matrix_forms(
            self.__rot_tr(working_size, self.rot),
            self._compose_matrix_forms(
                self.__zoom_tr(working_size, self.zoom),
                self._compose_matrix_forms(
                    self.__vert_tr(working_size, self.vert),
                    self.__horiz_tr(working_size, self.horiz)
                )
            )
        )

    def __mul__(self, other):
        """Compose one transform with another.
        """
        def __result(working_size):
            return self._compose_matrix_forms(
                self.__call__(working_size),
                other.__call__(working_size))
        # This implementation is bad for performance because it will result in
        # many nested calls to _compose_matrix_forms.
        return __result

    def __invert__(self):
        """Get the inverse transform.
        """
        def __result(working_size):
            return self._invert_matrix_form(self.__call__(working_size))
        return __result


# Some generators of random transforms, currently unused...
class RandomTransformer(object):
    def __init__(self, randomness):
        self.r = randomness

    def __call__(self):
        zoom = uniform(1-.07*self.r, 1+.07*self.r)
        rot = uniform(-3*self.r, 3*self.r)
        horiz = uniform(-0.01*self.r, 0.01*self.r)
        vert = uniform(-0.01*self.r, 0.01*self.r)
        return Transform(horiz, vert, zoom, rot)


class RandomRotator(RandomTransformer):
    def __call__(self):
        rot = uniform(-3*self.r, 3*self.r)
        return Transform(0, 0, 1, rot)


class RandomTranslator(RandomTransformer):
    def __call__(self):
        horiz = uniform(-0.01*self.r, 0.01*self.r)
        vert = uniform(-0.01*self.r, 0.01*self.r)
        return Transform(horiz, vert, 1, 0)
