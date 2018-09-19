import unittest
from os.path import join

from mock import MagicMock, Mock, patch

from dls_imagematch.service import readable_config_dir, parser_manager
from dls_imagematch.service.parser_manager import ParserManager
from dls_util.imaging import Image


class TestParserManager(unittest.TestCase):

    def setUp(self):
        self.pm = ParserManager()
        self.pm.build_parser()

    def test_build_parer_creates_parser_object(self):
        self.assertIsNotNone(self.pm.parser)

    def test_get_config_returns_default_config_directory_when_config_directory_is_not_specified(self):
        self.pm.get_args = Mock(return_value=Mock(config=None)) #!! return value has to be a mock with particular parameters
        self.assertEquals(self.pm.get_config_dir(), readable_config_dir.CONFIG_DIR)

    # is it really a useful test?
    def test_get_config_returns_whatever_is_specified_as_config(self):
        test_string = 'ble'
        self.pm.get_args = Mock(return_value=Mock(config=test_string))
        self.assertEquals(self.pm.get_config_dir(), test_string)

    def test_get_scale_override_returns_None_if_not_set(self):
        self.pm.get_args = Mock(return_value=Mock(scale=None))
        self.assertIsNone(self.pm.get_scale_override())

    def test_get_scale_override_returns_scale_when_set_correctly(self):
        correct_scale = "2.0:3.0"
        self.pm.get_args = Mock(return_value=Mock(scale=correct_scale))
        self.assertEquals(self.pm.get_scale_override(), (float(2),float(3)))

    def test_get_scale_override_raises_assertion_error_when_scale_element_divided_by_coma(self):
        bad_scale = "20,3"
        self.pm.get_args = Mock(return_value=Mock(scale=bad_scale))

        with (self.assertRaises(AssertionError)):
            self.pm.get_scale_override()

    def test_get_scale_override_raises_assertion_error_when_only_one_element(self):
        bad_scale = ":3"
        self.pm.get_args = Mock(return_value=Mock(scale=bad_scale))

        with (self.assertRaises(ValueError)):
            self.pm.get_scale_override()

    def test_parse_selected_point_returns_empty_array_when_no_points_specified(self):
        self.pm.get_args = Mock(return_value=Mock(selected_points=None))
        self.assertEquals(self.pm.parse_selected_points_from_args(), [])

    def test_parse_selected_point_ignores_point_with_invalid_format(self):
        points_invalid_format = "2:4 4:5"
        self.pm.get_args = Mock(return_value=Mock(selected_points=points_invalid_format))
        self.assertEquals(self.pm.parse_selected_points_from_args(),[])

    def test_parse_selected_points_creates_list_of_points_when_the_format_is_valid(self):
        valid_format = ['1800,1690']
        self.pm.get_args = Mock(return_value=Mock(selected_points=valid_format))
        points = self.pm.parse_selected_points_from_args()
        self.assertEquals(len(points), 1)

    def test_get_focused_image_returns_an_instance_of_image_when_single_image_path_is_passed(self):
        path = '../../../system-tests/resources/stacking/ideal.tif'
        self.pm.get_args = Mock(return_value=Mock(beamline_stack_path=path))
        im = self.pm.get_focused_image()
        self.assertIsInstance(im, Image)
        self.assertGreater(im.size(), 0)

    def test_get_focused_image_returns_an_instance_of_image_when_directory_path_is_passed(self):
        path = '../../../system-tests/resources/stacking/levels'
        pm = ParserManager()
        pm.build_parser()
        pm.get_args = Mock(return_value=Mock(beamline_stack_path=path, config=readable_config_dir.CONFIG_DIR))
        im = pm.get_focused_image()
        self.assertIsInstance(im, Image)
        self.assertGreater(im.size(), 0)

    def test_sorting_files_puts_the_oldest_first_in_the_list(self):
        path = '../../../system-tests/resources/stacking/levels'
        files = ParserManager._sort_files_according_to_creation_time(path)
        self.assertIn('FL9', files[0].name) # FL9 created first (used to be FL4)


    def test_get_focused_image_path_when_beamline_image_path_point_to_dictionary(self):
        path = '../../../system-tests/resources/stacking/levels'
        self.pm.get_args = Mock(return_value=Mock(beamline_stack_path=path, output=None, log=None, config=readable_config_dir.CONFIG_DIR))
        result_path = self.pm.get_focused_image_path()
        self.assertIn('processed.tif', result_path)#defoult as output and log are none

    def test_get_focused_image_path_when_beamline_image_path_points_to_file(self):
        path = '../../../system-tests/resources/stacking/ideal.tif'
        self.pm.get_args = Mock(return_value=Mock(beamline_stack_path=path))
        result_path = self.pm.get_focused_image_path()
        self.assertIn('ideal.tif', result_path)
#!!!!!SAVE IMAGE















