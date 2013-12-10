# coding: utf-8
from unittest import TestCase

from flask import json, request
from api_utils import ResponsiveFlask, formatters


app = ResponsiveFlask(__name__)


@app.route('/')
def hello_world():
    return {'hello': 'world'}

expected_json = {'hello': 'world'}


def dummy_xml_formatter(*args, **kwargs):
    return '<hello>world</hello>'

expected_xml = b'<hello>world</hello>'


class ResponsiveFlaskTest(TestCase):

    def setUp(self):
        app.default_mimetype = 'application/json'
        app.response_formatters = {'application/json': formatters.json}

        self.app = app.test_client()

    def test_json_response_when_accept_header_is_not_given(self):
        headers = {}
        r = self.app.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_json_response_when_accept_header_means_all_media_types(self):
        headers = {
            'Accept': '*/*',
        }
        r = self.app.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_406_when_accept_header_is_given_but_format_is_unknown(self):
        headers = {
            'Accept': 'application/vnd.company.myapp.product-v2+xml',
        }
        r = self.app.get('/', headers=headers)
        not_acceptable_status_code = 406

        self.assertEqual(r.status_code, not_acceptable_status_code)
        self.assertEqual(r.mimetype, 'application/json')

    def test_list_of_mimetypes_is_in_json_when_format_is_unknown(self):
        headers = {
            'Accept': 'blah/*',
        }
        r = self.app.get('/', headers=headers)
        r_json = json.loads(r.data)
        expected_json = {
            'mimetypes': ['application/json'],
        }

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_json_is_used_because_xml_formatter_is_not_set(self):
        headers = {
            'Accept': 'application/xml,application/json',
        }
        r = self.app.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_xml_is_used_because_xml_formatter_is_set_manually(self):
        app.response_formatters['application/xml'] = dummy_xml_formatter

        headers = {
            'Accept': 'application/xml,application/json',
        }
        r = self.app.get('/', headers=headers)

        self.assertEqual(r.data, expected_xml)
        self.assertEqual(r.mimetype, 'application/xml')

    def test_xml_is_used_because_default_mimetype_is_set_manually(self):
        app.default_mimetype = 'application/xml'
        app.response_formatters['application/xml'] = dummy_xml_formatter

        headers = {
            'Accept': '*/*',
        }
        r = self.app.get('/', headers=headers)

        self.assertEqual(r.data, expected_xml)
        self.assertEqual(r.mimetype, 'application/xml')

    def test_json_response_is_returned_due_to_quality_factor(self):
        app.response_formatters['application/xml'] = dummy_xml_formatter

        headers = {
            'Accept': 'application/xml;q=0.5,application/json',
        }
        r = self.app.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_rv_as_dict_response_and_status_code(self):
        @app.route('/201')
        def hello_world_201_status():
            return {'hello': 'world'}, 201

        r = self.app.get('/201')
        r_json = json.loads(r.data)
        expected_status_code = 201

        self.assertEqual(r.status_code, expected_status_code)
        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')


class ErrorHandlingByResponsiveFlaskTest(TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_400_error_is_json_formatted_when_view_raises_key_error(self):
        @app.route('/400')
        def hello_bad_request():
            request.args['bad-key']

        r = self.app.get('/400')
        r_json = json.loads(r.data)
        expected_status_code = 400

        self.assertEqual(r.status_code, expected_status_code)
        self.assertEqual(r_json['code'], expected_status_code)
        self.assertEqual(r.mimetype, 'application/json')
