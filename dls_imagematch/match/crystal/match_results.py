from dls_imagematch.util import Rectangle
from dls_imagematch.match.transformation import Transformation
from dls_imagematch.match.aligned_images import AlignedImages


class CrystalMatchResults:
    """ Represents a pair of images with a set of crystal location matches between them. The client
    specifies a list of points in Image 1 which are to be matched in Image 2, and later supplies a
    transformation which calculates the point in Image 2 from that in Image 1. """
    def __init__(self, aligned_images):
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
