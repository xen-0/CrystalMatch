from dls_imagematch.crystal.align import AlignConfig
from dls_imagematch.crystal.align import ImageAligner
from dls_imagematch.crystal.match import CrystalMatchConfig
from dls_imagematch.crystal.match import CrystalMatcher
from dls_imagematch.feature.detector import DetectorConfig
from dls_imagematch.feature.draw import MatchPainter
from dls_util.image import Image


class CrystalMatchService:
    def __init__(self, config_directory):
        self._config_directory = config_directory

        self._config_detector = DetectorConfig(config_directory)
        self._config_align = AlignConfig(config_directory)
        self._config_crystal = CrystalMatchConfig(config_directory)

    def perform_match(self, formulatrix_image_path, beamline_image_path, selected_points):
        # Create the images
        image1 = Image.from_file(formulatrix_image_path)
        image2 = Image.from_file(beamline_image_path)

        # Perform alignment
        aligned_images = self._perform_alignment(image1, image2)

        # overlay_image = aligned_images.overlay()
        # overlay_image.popup()

        # Perform Crystal Matching
        match_result = self._perform_matching(aligned_images, selected_points)

    def _perform_alignment(self, formulatrix_image, beamline_image):
        """ Perform alignment on the two images, returning an AlignedImages object. """
        aligner = ImageAligner(formulatrix_image, beamline_image, self._config_align, self._config_detector)
        aligned_images = aligner.align()
        self._print_alignment_status(aligned_images)

        return aligned_images

    def _perform_matching(self, aligned_images, selected_points):
        matcher = CrystalMatcher(aligned_images, self._config_detector)
        matcher.set_from_crystal_config(self._config_crystal)

        crystal_match_results = matcher.match(selected_points)
        self._print_match_results(crystal_match_results)
        self._popup_match_results(crystal_match_results)

        return crystal_match_results

    @staticmethod
    def _print_alignment_status(aligned):
        status = "Unknown"

        if aligned.is_alignment_good():
            status = "Good Alignment"
        elif aligned.is_alignment_poor():
            status = "Poor Alignment"
        elif aligned.is_alignment_bad():
            status = "Alignment failed!"

        print("Image Alignment Completed - Status: '{}' (Score={:.2f})".format(status, aligned.overlap_metric()))

        match_result = aligned.feature_match_result
        if match_result is not None:
            print("- Matching Time: {:.4f}".format(match_result.time_match()))
            print("- Transform Time: {:.4f}".format(match_result.time_transform()))

    @staticmethod
    def _print_match_results(crystal_results):
        print("Crystal Matching Complete")

        for i, crystal_match in enumerate(crystal_results.matches):
            print("\n*** Crystal Match {} ***".format(i+1))
            if not crystal_match.is_match_found():
                print("-- Match Failed")
                continue

            # Matching time
            feature_result = crystal_match.feature_match_result()
            print("- Matching Time: {:.4f}".format(feature_result.time_match()))
            print("- Transform Time: {:.4f}".format(feature_result.time_transform()))

            # Beam position and movement
            pixel1, real1 = crystal_match.image1_point(), crystal_match.image1_point_real()
            pixel2, real2 = crystal_match.image2_point(), crystal_match.image2_point_real()

            beam_position = "- Beam Position: x={0:.2f} um, y={1:.2f} um ({2} px, " \
                            "{3} px)".format(real2.x, real2.y, int(round(pixel2.x)), int(round(pixel2.y)))

            delta_pixel = pixel2 - pixel1 + crystal_results.pixel_offset()
            delta_real = real2 - real1 + crystal_results.real_offset()
            delta = "- Crystal Movement: x={0:.2f} um, y={1:.2f} um ({2} px, " \
                    "{3} px)".format(delta_real.x, delta_real.y, int(round(delta_pixel.x)), int(round(delta_pixel.y)))

            print(beam_position)
            print(delta)

    @staticmethod
    def _popup_match_results(results):
        for i in range(results.num()):
            feature_match_result = results.get_crystal_match(i).feature_match_result()

            painter = MatchPainter(feature_match_result.image1(), feature_match_result.image2())

            image = painter.background_image()
            #image = painter.draw_transform_shapes(self._quad1, self._quad2, image)
            image = painter.draw_matches(feature_match_result.good_matches(), [], image)
            #image = painter.draw_transform_points(self._image1_point, self._image2_point, image)
            image.popup()
