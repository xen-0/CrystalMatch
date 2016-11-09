from __future__ import print_function

from unittest import TestCase

from mock.mock import patch, Mock, MagicMock, call, create_autospec
from os.path import abspath

from dls_imagematch.crystal.align.aligned_images import ALIGNED_IMAGE_STATUS_OK, ALIGNED_IMAGE_STATUS_FAIL, \
    AlignedImages
from dls_imagematch.crystal.match.match import CrystalMatch, CRYSTAL_MATCH_STATUS_OK, CRYSTAL_MATCH_STATUS_FAIL
from dls_imagematch.crystal.match.results import CrystalMatcherResults
from dls_imagematch.feature.match.result import FeatureMatcherResult
from dls_imagematch.service.service_result import ServiceResult
from dls_util.shape.point import Point


class TestServiceResult(TestCase):
    @staticmethod
    def get_output(mock_print):
        output = ""
        for method_call in mock_print.call_args_list:
            output += method_call[0][0]
        assert (len(output) > 0)
        return output

    @staticmethod
    def mock_crystal_matcher_results(deltas, mean_transform_errors, new_positions, status_codes):
        assert (len(new_positions) == len(deltas) == len(mean_transform_errors) == len(status_codes))
        match_array = []
        for i in range(len(new_positions)):
            # Mock Feature Match
            mock_feature_match = create_autospec(FeatureMatcherResult, spec_set=True)
            mock_feature_match.mean_transform_error = MagicMock(return_value=mean_transform_errors[i])

            # Mock Crystal Match
            mock_crystal_match = create_autospec(CrystalMatch, spec_set=True)
            mock_crystal_match.get_transformed_poi = MagicMock(return_value=new_positions[i])
            mock_crystal_match.get_delta = MagicMock(return_value=deltas[i])
            mock_crystal_match.feature_match_result = MagicMock(return_value=mock_feature_match)
            mock_crystal_match.get_status = MagicMock(return_value=status_codes[i])

            match_array.append(mock_crystal_match)
        mock_match_results = create_autospec(CrystalMatcherResults, spec_set=True)
        mock_match_results.get_matches = MagicMock(return_value=match_array)
        return mock_match_results

    @staticmethod
    def mock_aligned_images(confidence, status, transform):
        mock_aligned_image = create_autospec(AlignedImages, spec_set=True)
        mock_aligned_image.alignment_status_code = MagicMock(return_value=status)
        mock_aligned_image.overlap_metric = MagicMock(return_value=confidence)
        mock_aligned_image.get_alignment_transform = MagicMock(return_value=transform)
        return mock_aligned_image

    @patch('dls_imagematch.service.service_result.print', create=True)
    def test_job_id_and_image_paths_printed_correctly(self, mock_print):
        result = ServiceResult("test-job-id", "test/file/path/fomulatrix", "test/file/path/beamline")
        result.print_results()

        mock_print.assert_any_call('job_id:"test-job-id"')
        mock_print.assert_any_call('input_image:"' + abspath('test/file/path/fomulatrix') + '"')
        mock_print.assert_any_call('output_image:"' + abspath('test/file/path/beamline') + '"')

    @patch('dls_imagematch.service.service_result.print', create=True)
    def test_job_id_does_not_print_if_blank(self, mock_print):
        result = ServiceResult("", "test/file/path/fomulatrix", "test-file/path/beamline")
        result.print_results()

        output = self.get_output(mock_print)
        self.failIf("job_id" in output)

    @patch('dls_imagematch.service.service_result.print', create=True)
    def test_job_id_does_not_print_and_does_not_cause_exception_if_none(self, mock_print):
        result = ServiceResult(None, "test/file/path/fomulatrix", "test-file/path/beamline")
        result.print_results()

        output = self.get_output(mock_print)
        self.failIf("job_id" in output)

    def test_add_image_alignment_results(self):
        mock_aligned_image = Mock(spec_set=["alignment_status_code", "overlap_metric", "pixel_offset",
                                            "get_alignment_transform"])
        mock_aligned_image.get_alignment_transform = MagicMock(return_value=(1.0, Point(0, 0)))
        result = ServiceResult("job-id", "fomulatrix", "beamline")
        result.set_image_alignment_results(mock_aligned_image)

    @patch('dls_imagematch.service.service_result.print', create=True)
    def test_print_without_alignment_results_shows_default_values(self, mock_print):
        Mock(spec_set=["alignment_status_code", "overlap_metric", "pixel_offset",
                                            "get_alignment_transform"])
        result = ServiceResult("job-id", "fomulatrix", "beamline")
        result.print_results()

        # Test output
        mock_print.assert_has_calls([
            call('align_transform:1.0, (0.00, 0.00)'),
            call('align_status:-1, NOT SET'),
            call('align_error:0.0')
        ])

    @patch('dls_imagematch.service.service_result.print', create=True)
    def test_image_alignment_results_print_for_success_case(self, mock_print):
        # Set up mock for successful image match
        status = ALIGNED_IMAGE_STATUS_OK
        confidence = 9.8
        transform = (1.0, Point(3.0, 4.0))
        mock_aligned_image = self.mock_aligned_images(confidence, status, transform)

        result = ServiceResult("job-id", "fomulatrix", "beamline")
        result.set_image_alignment_results(mock_aligned_image)
        result.print_results()

        # Test output
        mock_print.assert_has_calls([
            call("align_transform:" + str(transform[0]) + ", " + str(transform[1])),
            call("align_status:1, OK"),
            call("align_error:9.8")])

    @patch('dls_imagematch.service.service_result.print', create=True)
    def test_image_alignment_results_print_for_failure_case(self, mock_print):
        # Set up mock for successful image match
        status = ALIGNED_IMAGE_STATUS_FAIL
        confidence = 0.0
        transform = (1.0, Point(0, 0))
        mock_aligned_image = self.mock_aligned_images(confidence, status, transform)

        result = ServiceResult("job-id", "fomulatrix", "beamline")
        result.set_image_alignment_results(mock_aligned_image)
        result.print_results()

        # Test output
        mock_print.assert_has_calls([
            call("align_transform:1.0, (0.00, 0.00)"),
            call("align_status:0, FAIL"),
            call("align_error:0.0")])

    @patch('dls_imagematch.service.service_result.print', create=True)
    def test_output_prints_correctly_with_no_crystal_match_results(self, mock_print):
        result = ServiceResult("job-id", "fomulatrix", "beamline")
        result.print_results()

        # Test for presence of poi: objects in output
        output = self.get_output(mock_print)
        self.failIf("poi:" in output)

    @patch('dls_imagematch.service.service_result.print', create=True)
    def test_append_single_crystal_match_result(self, mock_print):
        # Setup - create mock result
        new_positions = [Point(100, 100)]
        deltas = [Point(3, 4)]
        mean_errors = ["0.45"]
        status_codes = [CRYSTAL_MATCH_STATUS_OK]
        mock_match_results = self.mock_crystal_matcher_results(deltas, mean_errors, new_positions, status_codes)

        # Run
        result = ServiceResult("job-id", "fomulatrix", "beamline")
        result.append_crystal_matching_results(mock_match_results)
        result.print_results()

        # Test
        mock_print.assert_has_calls([
            call("\nlocation ; transform ; status ; mean error"),
            call("poi:(100.00, 100.00) ; (3.00, 4.00) ; 1, OK ; 0.45")
        ])

    @patch('dls_imagematch.service.service_result.print', create=True)
    def test_failed_crystal_match_result_prints_correctly(self, mock_print):
        # Setup - create mock result
        result = ServiceResult("job-id", "fomulatrix", "beamline")
        new_positions = [Point(654, 321)]
        deltas = [Point(7, 8)]
        mean_errors = ["65.4"]
        status_codes = [CRYSTAL_MATCH_STATUS_FAIL]
        mock_match_results = self.mock_crystal_matcher_results(deltas, mean_errors, new_positions, status_codes)
        result.append_crystal_matching_results(mock_match_results)
        result.print_results()

        # Test
        mock_print.assert_has_calls([
            call("\nlocation ; transform ; status ; mean error"),
            call("poi:(654.00, 321.00) ; (7.00, 8.00) ; 0, FAIL ; 65.4"),
        ])

    @patch('dls_imagematch.service.service_result.print', create=True)
    def test_append_multiple_crystal_match_results(self, mock_print):
        # Setup - create mock result
        result = ServiceResult("job-id", "fomulatrix", "beamline")

        # Set 1
        new_positions = [Point(100, 100)]
        deltas = [Point(3, 4)]
        mean_errors = ["0.45"]
        status_codes = [CRYSTAL_MATCH_STATUS_OK]
        mock_match_results = self.mock_crystal_matcher_results(deltas, mean_errors, new_positions, status_codes)
        result.append_crystal_matching_results(mock_match_results)

        # Set 2
        new_positions = [Point(123, 456), Point(654, 321)]
        deltas = [Point(1, 2), Point(7, 8)]
        mean_errors = ["4.56", "65.4"]
        status_codes = [CRYSTAL_MATCH_STATUS_OK, CRYSTAL_MATCH_STATUS_FAIL]
        mock_match_results = self.mock_crystal_matcher_results(deltas, mean_errors, new_positions, status_codes)
        result.append_crystal_matching_results(mock_match_results)
        result.print_results()

        # Test
        mock_print.assert_has_calls([
            call("\nlocation ; transform ; status ; mean error"),
            call("poi:(100.00, 100.00) ; (3.00, 4.00) ; 1, OK ; 0.45"),
            call("poi:(123.00, 456.00) ; (1.00, 2.00) ; 1, OK ; 4.56"),
            call("poi:(654.00, 321.00) ; (7.00, 8.00) ; 0, FAIL ; 65.4"),
        ])
