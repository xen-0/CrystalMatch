import cv2

from dls_imagematch.util import Point, Image, Color


class FeaturePainter:
    @staticmethod
    def draw_matches(img1, img2, matches):
        """ Implementation of a function that is available in OpenCV 3 but not in OpenCV 2.
        Makes an image that is a side-by-side of the two images, with detected features highlighted and lines
        drawn between matching features in the two images.
        """
        # Create a new output image that concatenates the two images together
        w1, h1 = img1.size
        w2, h2 = img2.size
        img1_pos, img2_pos = Point(0, 0), Point(w1, 0)
        out = Image.blank(w1+w2, max(h1, h2))
        out.paste(img1, img1_pos)
        out.paste(img2, img2_pos)

        # For each pair of points we have between both images draw circles, then connect a line between them
        for match in matches:
            point1 = match.point1()
            point2 = match.point2() + img2_pos
            # Draw a small circle at both co-ordinates
            out.draw_circle(point=point1, radius=4, color=Color.Blue(), thickness=1)
            out.draw_circle(point=point2, radius=4, color=Color.Blue(), thickness=1)

            # Draw a line between the two points
            out.draw_line(point1, point2, color=Color.Blue(), thickness=1)

        # Resize so that it fits on the screen
        factor = 1000 / out.width
        out = out.rescale(factor)
        out.popup("Matches")

    @staticmethod
    def _draw_keypoints(img, keypoints):
        """ Draw the list of keypoints to the specified image and display it as a popup window. """
        marked_img = cv2.drawKeypoints(img.img, keypoints, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        Image(marked_img).popup("Keypoints")