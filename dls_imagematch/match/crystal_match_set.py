from dls_imagematch.util import Rectangle
from .transformation import Transformation
from .aligned_images import AlignedImages


class CrystalMatchSet:
    """ Represents a pair of images with a set of crystal location matches between them. The client
    specifies a list of points in Image 1 which are to be matched in Image 2, and later supplies a
    transformation which calculates the point in Image 2 from that in Image 1. """
    def __init__(self, aligned_images, img1_points):
        """ Initialize a new CrystalMatchSet object.

        Parameters
        ----------
        aligned_images - AlignedImages object, containing the two images to draw crystal matches between
        img1_points - list of Points of crystals in Image 1 coordinates (pixels)
        """
        if not isinstance(aligned_images, AlignedImages):
            raise TypeError("Argument must be instance of {}".format(AlignedImages.__name__))

        self._aligned_images = aligned_images
        self.matches = []

        pixel_size = aligned_images.img1.pixel_size
        for point in img1_points:
            self.matches.append(_CrystalMatch(point, pixel_size))

    def num(self):
        """ The number of crystal matches in the set. """
        return len(self.matches)

    def get_match(self, index):
        """ Get a specific match object by index. """
        return self.matches[index]

    def img1(self):
        """ The first image; contains the user-selected crystal locations. """
        return self._aligned_images.img1

    def img2(self):
        """ The second image. """
        return self._aligned_images.img2

    def pixel_offset(self):
        """ The alignment offset between Image 1 and Image 2 (in pixels). """
        return self._aligned_images.pixel_offset()

    def real_offset(self):
        """ The alignment offset between Image 1 and Image 2 (in um). """
        return self._aligned_images.real_offset()


class _CrystalMatch:
    """  Represents a match between the position of a crystal in two separate images. """
    def __init__(self, start_point, pixel_size):
        """ Initialize a new CrystalMatch object. Note that You must call the set_transformation
        method to set the transformation (and therefore calculate the matching position in Image 2).

        Parameters
        ----------
        start_point - The user selected location of the crystal in image 1 (in pixels)
        pixel_size - The real size of a pixel in the image (in um)
        """
        self._img1_point = start_point
        self._img2_point = None
        self._pixel_size = pixel_size
        self._transformation = None

    def img1_point(self):
        """ The user-specified location of the crystal in Image 1 (in pixels). """
        return self._img1_point

    def img1_point_real(self):
        """ The user-specified location of the crystal in Image 1 (in um). """
        return self._img1_point * self._pixel_size

    def img1_region(self, size):
        """ Return a Rectangle object of specified side length, centered around the Image 1
        point (in pixels). """
        return Rectangle.from_center(self._img1_point, size, size)

    def img2_point(self):
        """ The location of the crystal in Image 2 as determined by the transformation (in
        pixels). Note that the set_transformation method must be called to set this to a valid
        value. """
        return self._img2_point

    def img2_point_real(self):
        """ The location of the crystal in Image 2 as determined by the transformation (in
        um). Note that the set_transformation method must be called to set this to a valid
        value. """
        return self._img2_point * self._pixel_size

    def is_match_found(self):
        """ Returns True if the set_transformation function has been called correctly. """
        return self._img2_point is not None

    def set_transformation(self, transformation):
        """ Set the transformation which maps the crystal location from Image 1 onto the
        same crystal location on Image 2. """
        if not isinstance(transformation, Transformation):
            raise TypeError("Argument must be instance of {}".format(Transformation.__name__))

        self._transformation = transformation
        self._img2_point = transformation.transform_points([self._img1_point])[0]

