from numbers import Number
from os.path import realpath

from dls_util.shape.point import Point
from system_test import SystemTest


class TestServiceOutput(SystemTest):
    def setUp(self):
        self.set_directory_paths(realpath(__file__))

    def test_json_output_format_for_valid_run(self):
        cmd_line = "-j 123 --to_json {resources}/A10_1.jpg {resources}/A10_2.jpg 902,435 963,1310"
        self.run_crystal_matching_test(self.test_json_output_format_for_valid_run.__name__, cmd_line)

        # Read the output into a JSON object and test it against expected values
        # Test Global alignment format
        json = self.read_json_object_from_std_out()
        exp_poi_len = 2
        exp_input_image = self.substitute_tokens("{resources}/A10_1.jpg")
        exp_output_image = self.substitute_tokens("{resources}/A10_2.jpg")
        job_id = "123"
        self.failUnlessEqual(1, json['alignment']['status']['value'])
        self._validate_format_of_json_object(json, job_id, exp_input_image, exp_output_image, exp_poi_len)

    def test_json_output_for_failed_image_alignment_without_points(self):
        cmd_line = "--to_json {resources}/A01_1.jpg {resources}/A10_2.jpg"
        self.run_crystal_matching_test(self.test_json_output_for_failed_image_alignment_without_points.__name__,
                                       cmd_line)

        # Read the output into a JSON object and test it against expected values
        # Test Global alignment format
        json = self.read_json_object_from_std_out()
        exp_poi_len = 0
        exp_input_image = self.substitute_tokens("{resources}/A01_1.jpg")
        exp_output_image = self.substitute_tokens("{resources}/A10_2.jpg")
        job_id = None
        self.failUnlessEqual(0, json['alignment']['status']['value'])
        self._validate_format_of_json_object(json, job_id, exp_input_image, exp_output_image, exp_poi_len)

    def test_json_output_for_failed_image_alignment_with_points(self):
        cmd_line = "--to_json {resources}/A01_1.jpg {resources}/A10_2.jpg 902,435 963,1310"
        self.run_crystal_matching_test(self.test_json_output_for_failed_image_alignment_with_points.__name__,
                                       cmd_line)

        # Read the output into a JSON object and test it against expected values
        # Test Global alignment format
        json = self.read_json_object_from_std_out()
        exp_poi_len = 0
        exp_input_image = self.substitute_tokens("{resources}/A01_1.jpg")
        exp_output_image = self.substitute_tokens("{resources}/A10_2.jpg")
        self.failUnlessEqual(0, json['alignment']['status']['value'])
        self._validate_format_of_json_object(json, None, exp_input_image, exp_output_image, exp_poi_len)

    def test_json_format_for_failed_points(self):
        cmd_line = "--to_json {resources}/A10_1.jpg {resources}/A10_2.jpg 473,921"
        self.run_crystal_matching_test(self.test_json_format_for_failed_points.__name__, cmd_line)

        # Read the output into a JSON object and test it against expected values
        # Test Global alignment format
        json = self.read_json_object_from_std_out()
        exp_poi_len = 1
        exp_input_image = self.substitute_tokens("{resources}/A10_1.jpg")
        exp_output_image = self.substitute_tokens("{resources}/A10_2.jpg")
        self.failUnlessEqual(1, json['alignment']['status']['value'])
        self.failUnlessEqual(0, json['poi'][0]['status']['value'])
        self._validate_format_of_json_object(json, None, exp_input_image, exp_output_image, exp_poi_len)

    def test_json_format_of_global_transform_with_scaled_image(self):
        cmd_line = "--to_json --scale_input 0.5 {resources}/A10_2.jpg {resources}/A10_2@0.5.jpg 473,921"
        self.run_crystal_matching_test(self.test_json_format_of_global_transform_with_scaled_image.__name__, cmd_line)

        # Read the output into a JSON object and test it against expected values
        # Test Global alignment format
        json = self.read_json_object_from_std_out()
        exp_poi_len = 1
        exp_input_image = self.substitute_tokens("{resources}/A10_2.jpg")
        exp_output_image = self.substitute_tokens("{resources}/A10_2@0.5.jpg")
        self._validate_format_of_json_object(json, None, exp_input_image, exp_output_image, exp_poi_len, exp_scale=0.5)

    def test_json_output_matches_standard_output_data(self):
        cmd_line = "-j 123 {resources}/A10_1.jpg {resources}/A10_2.jpg 902,435 963,1310"
        test_name = self.test_json_output_matches_standard_output_data.__name__
        self.run_crystal_matching_test(test_name + "-run_json", cmd_line + " --to_json")
        json = self.read_json_object_from_std_out()
        self.run_crystal_matching_test(test_name + "-run_standard", cmd_line)

        # Test output matches json object - check this is a successful run
        json_align_status = json['alignment']['status']
        self.failUnlessEqual(1, json_align_status['value'])
        # Test run info
        self.failUnlessStdOutContains(
            'input_image:"' + json['input_image'] + '"',
            'output_image:"' + json['output_image'] + '"',
            'job_id:"' + json['job_id'] + '"',
        )

        # Test Alignment phase
        scale, x_trans, y_trans = self.get_global_transform_from_std_out()
        self.failUnlessEqual(scale, json['alignment']['transform']['scale'])
        self.failUnlessEqual(x_trans, json['alignment']['transform']['translation']['x'])
        self.failUnlessEqual(y_trans, json['alignment']['transform']['translation']['y'])
        self.failUnlessStdOutContains(
            'align_status:' + str(json_align_status['value']) + ', ' + json_align_status['msg'],
            'align_error:' + str(json['alignment']['mean_error'])
        )

        # Test POI phase
        json_poi_array = []
        for poi in json['poi']:
            loc = Point(poi['location']['x'], poi['location']['y'])
            tran = Point(poi['translation']['x'], poi['translation']['y'])
            stat = poi['status']['value']
            err = poi['mean_error']
            json_poi_array.append([loc, tran, stat, err])
        self.failUnlessPoiAlmostEqual(json_poi_array)

    def _validate_format_of_json_object(self, json, job_id, expected_input_image, expected_output_image,
                                        expected_poi_len, exp_scale=1.0):
        self.failUnlessEqual(expected_input_image, json['input_image'])
        self.failUnlessEqual(expected_output_image, json['output_image'])
        if job_id is None:
            self.failIf('job_id' in json.keys())
        else:
            self.failUnlessEqual(job_id, json['job_id'])
        self.failUnless(json['alignment']['status']['msg'] in "OK;FAIL")
        status_value = json['alignment']['status']['value']
        self.failUnless(status_value == 1 or status_value == 0)
        self.failUnlessEqual(exp_scale, json['alignment']['transform']['scale'])
        self.failUnless(isinstance(json['alignment']['transform']['translation']['x'], Number))
        self.failUnless(isinstance(json['alignment']['transform']['translation']['y'], Number))
        self.failUnless(isinstance(json['alignment']['mean_error'], Number))
        self.failUnlessEqual(expected_poi_len, len(json['poi']))

        # Test POI
        for i in range(len(json['poi'])):
            self.failUnless(isinstance(json['poi'][i]['location']['x'], Number))
            self.failUnless(isinstance(json['poi'][i]['location']['y'], Number))
            self.failUnless(isinstance(json['poi'][i]['translation']['x'], Number))
            self.failUnless(isinstance(json['poi'][i]['translation']['y'], Number))
            self.failUnless(isinstance(json['poi'][i]['mean_error'], Number))
            status_value = json['poi'][i]['status']['value']
            status_msg = json['poi'][i]['status']['msg']
            self.failUnless(status_value == 1 or status_value == 0)
            self.failUnless(status_msg in "OK;FAIL")
