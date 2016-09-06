from dls_imagematch.util import Rectangle


class CrystalMatch:
    """  Represents a match between the position of a crystal in two separate images. """
    def __init__(self, start_point, pixel_size):
        """ Initialize a new CrystalMatch object. Note that You must call the set_transformation
        method to set the transformation (and therefore calculate the matching position in Image 2).

        Parameters
        ----------
        start_point - The user selected location of the crystal in image 1 (in pixels)
        pixel_size - The real size of a pixel in the image (in um)
        """
        self._image1_point = start_point
        self._image2_point = None
        self._pixel_size = pixel_size
        self._feature_match_result = None

    def is_success(self):
        return self._image2_point is not None

    def pixel_size(self):
        return self._pixel_size

    def feature_match_result(self):
        return self._feature_match_result

    def image1_point(self):
        """ The user-specified location of the crystal in Image 1 (in pixels). """
        return self._image1_point

    def image1_point_real(self):
        """ The user-specified location of the crystal in Image 1 (in um). """
        return self._image1_point * self._pixel_size

    def image1_region(self, size):
        """ Return a Rectangle object of specified side length, centered around the Image 1
        point (in pixels). """
        return Rectangle.from_center(self._image1_point, size, size)

    def image2_point(self):
        """ The location of the crystal in Image 2 as determined by the transformation (in
        pixels). Note that the set_transformation method must be called to set this to a valid
        value. """
        return self._image2_point

    def image2_point_real(self):
        """ The location of the crystal in Image 2 as determined by the transformation (in
        um). Note that the set_transformation method must be called to set this to a valid
        value. """
        return self._image2_point * self._pixel_size

    def is_match_found(self):
        """ Returns True if the set_transformation function has been called correctly. """
        return self._image2_point is not None

    def set_feature_match_result(self, feature_result):
        """ Set the transformation which maps the crystal location from Image 1 onto the
        same crystal location on Image 2. """
        self._feature_match_result = feature_result
        trans = feature_result.transform()
        if trans is not None:
            self._image2_point = trans.transform_points([self._image1_point])[0]
