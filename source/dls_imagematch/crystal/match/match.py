from dls_util.shape import Rectangle


class CrystalMatchStatus:
    def __init__(self, code, status):
        self.code = code
        self.status = status

    def __str__(self):
        return str(self.code) + ", " + self.status

# Status values
CRYSTAL_MATCH_STATUS_STATUS_NOT_SET = CrystalMatchStatus(-1, "NOT SET")
CRYSTAL_MATCH_STATUS_OK = CrystalMatchStatus(1, "OK")
CRYSTAL_MATCH_STATUS_FAIL = CrystalMatchStatus(0, "FAIL")


class CrystalMatch:
    """  Represents a match between the position of a crystal in two separate images. """
    def __init__(self, start_point, aligned_images):
        """
        Initialize a new CrystalMatch object. Note that You must call the set_transformation
        method to set the transformation (and therefore calculate the matching position in Image 2).
        :param start_point: The user selected location of the crystal in image 1 (in pixels)
        :param aligned_images: AlignedImages object from ImageAligner
        """
        self._aligned_images = aligned_images
        self._poi_image_1 = start_point
        self._poi_image_2_pre_match = start_point + self._aligned_images.pixel_offset()
        self._poi_image_2_matched = None
        self._feature_match_result = None
        self._status = CRYSTAL_MATCH_STATUS_STATUS_NOT_SET

    def is_success(self):
        return self._poi_image_2_matched is not None

    def feature_match_result(self):
        return self._feature_match_result

    def get_poi_image_1(self):
        """ The user-specified location of the crystal in Image 1 (in pixels). """
        return self._poi_image_1

    def get_poi_image_1_real(self):
        """ The user-specified location of the crystal in Image 1 (in um). """
        return self._poi_image_1 * self._aligned_images.get_working_resolution()

    def get_poi_image_2_pre_match(self):
        """
        The location of the POI on image 2 before matching (ie: the POI on image 1 with the alignment transform applied.
        """
        return self._poi_image_2_pre_match

    def get_poi_image_2_matched(self):
        """ The location of the crystal in Image 2 as determined by the transformation (in
        pixels). Note that the set_feature_match_result method must be called to set this to a valid
        value. """
        return self._poi_image_2_matched

    def get_poi_image_2_matched_real(self):
        """ The location of the crystal in Image 2 as determined by the transformation (in
        um). Note that the set_transformation method must be called to set this to a valid
        value. """
        return self._poi_image_2_matched * self._aligned_images.get_working_resolution()

    def get_delta(self):
        """
        Returns the offset which maps the pre-match POI in image 2 to the final point in image 2.
        """
        return self.get_transformed_poi() - self._poi_image_2_pre_match

    def get_transformed_poi(self):
        """
        If the match is a success this returns the final point in image B, if not then it should return the
        offset POI from Image a (ie: the original POI with the Alignment transform applied to map it to image 2).
        """
        if self.is_success():
            return self._poi_image_2_matched
        else:
            return self._poi_image_2_pre_match

    def get_status(self):
        return self._status

    def set_feature_match_result(self, feature_result):
        """ Set the transformation which maps the crystal location from Image 1 onto the
        same crystal location on Image 2. """
        self._feature_match_result = feature_result
        trans = feature_result.transform()
        if trans is not None:
            self._status = CRYSTAL_MATCH_STATUS_OK
            self._poi_image_2_matched = trans.transform_points([self._poi_image_2_pre_match])[0]
        else:
            self._status = CRYSTAL_MATCH_STATUS_FAIL
