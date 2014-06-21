# coding: utf-8
from flask.testsuite import FlaskTestCase
from flask import json, request
from api_utils import ResponsiveFlask


def hello_world():
    return {'hello': 'world'}
expected_json = {'hello': 'world'}


def dummy_xml_formatter(*args, **kwargs):
    return '<hello>world</hello>'
expected_xml = b'<hello>world</hello>'


class ResponsiveFlaskTest(FlaskTestCase):
    def setUp(self):
        self.app = ResponsiveFlask(__name__)
        self.client = self.app.test_client()

    def test_json_response_when_accept_header_is_not_given(self):
        self.app.add_url_rule('/', view_func=hello_world)

        headers = {}
        r = self.client.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_json_response_when_accept_header_means_all_media_types(self):
        self.app.add_url_rule('/', view_func=hello_world)

        headers = {
            'Accept': '*/*',
        }
        r = self.client.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_406_when_accept_header_is_given_but_format_is_unknown(self):
        self.app.add_url_rule('/', view_func=hello_world)

        headers = {
            'Accept': 'application/vnd.company.myapp.product-v2+xml',
        }
        r = self.client.get('/', headers=headers)
        not_acceptable_status_code = 406

        self.assertEqual(r.status_code, not_acceptable_status_code)
        self.assertEqual(r.mimetype, 'application/json')

    def test_list_of_mimetypes_is_in_json_when_format_is_unknown(self):
        self.app.add_url_rule('/', view_func=hello_world)

        headers = {
            'Accept': 'blah/*',
        }
        r = self.client.get('/', headers=headers)
        r_json = json.loads(r.data)
        expected_json = {
            'mimetypes': ['application/json'],
        }

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_json_is_used_because_xml_formatter_is_not_set(self):
        self.app.add_url_rule('/', view_func=hello_world)

        headers = {
            'Accept': 'application/xml,application/json',
        }
        r = self.client.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_xml_is_used_because_xml_formatter_is_set_manually(self):
        self.app.add_url_rule('/', view_func=hello_world)
        self.app.response_formatters['application/xml'] = dummy_xml_formatter

        headers = {
            'Accept': 'application/xml,application/json',
        }
        r = self.client.get('/', headers=headers)

        self.assertEqual(r.data, expected_xml)
        self.assertEqual(r.mimetype, 'application/xml')

    def test_xml_is_used_because_default_mimetype_is_set_manually(self):
        self.app.add_url_rule('/', view_func=hello_world)
        self.app.default_mimetype = 'application/xml'
        self.app.response_formatters['application/xml'] = dummy_xml_formatter

        headers = {
            'Accept': '*/*',
        }
        r = self.client.get('/', headers=headers)

        self.assertEqual(r.data, expected_xml)
        self.assertEqual(r.mimetype, 'application/xml')

    def test_json_response_is_returned_due_to_quality_factor(self):
        self.app.add_url_rule('/', view_func=hello_world)
        self.app.response_formatters['application/xml'] = dummy_xml_formatter

        headers = {
            'Accept': 'application/xml;q=0.5,application/json',
        }
        r = self.client.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_rv_as_dict_response_and_status_code(self):
        def hello_world_201_status():
            return {'hello': 'world'}, 201
        self.app.add_url_rule('/', view_func=hello_world_201_status)

        r = self.client.get('/')
        r_json = json.loads(r.data)
        expected_status_code = 201

        self.assertEqual(r.status_code, expected_status_code)
        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.mimetype, 'application/json')

    def test_mimetype_is_text_html_when_view_returns_non_dict(self):
        def index():
            return 'hello world'
        self.app.add_url_rule('/', view_func=index)

        r = self.client.get('/')

        self.assertEqual(r.data, b'hello world')
        self.assertEqual(r.mimetype, 'text/html')


def hello_bad_request():
    request.args['bad-key']


def code_and_message(error):
    """Makes dict response from given Werkzeug's default exception.

    It assumes that ``Flask.make_response()`` can understand dict format
    and make appropriate response.

    The format is:

    .. code-block:: python

        {
            'code': 400,
            'message': '400: Bad Request',
        }

    """
    response = {
        'code': error.code,
        'message': str(error),
    }
    return response, error.code


class ErrorHandlingByResponsiveFlaskTest(FlaskTestCase):
    def setUp(self):
        self.app = ResponsiveFlask(__name__)
        self.client = self.app.test_client()

    def test_error_was_is_formatted_as_text_html_by_default(self):
        self.app.add_url_rule('/', view_func=hello_bad_request)

        r = self.client.get('/')
        expected_status_code = 400

        self.assertEqual(r.status_code, expected_status_code)
        self.assertEqual(r.mimetype, 'text/html')

    def test_400_error_is_json_formatted_when_view_raises_key_error(self):
        self.app.add_url_rule('/', view_func=hello_bad_request)
        self.app.default_errorhandler(code_and_message)

        r = self.client.get('/')
        r_json = json.loads(r.data)
        expected_status_code = 400

        self.assertEqual(r.status_code, expected_status_code)
        self.assertEqual(r_json['code'], expected_status_code)
        self.assertEqual(r.mimetype, 'application/json')

    def test_error_response_contains_code_and_message_fields(self):
        self.app.add_url_rule('/', view_func=hello_bad_request)
        self.app.default_errorhandler(code_and_message)

        r = self.client.get('/')
        r_json = json.loads(r.data)

        self.assertIn('code', r_json)
        self.assertIn('message', r_json)
