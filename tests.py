# coding: utf-8
import json
from unittest import TestCase

from flask import make_response
from werkzeug.exceptions import NotAcceptable

from api_utils import ResponsiveFlask


app = ResponsiveFlask('test_app')


@app.route('/')
def hello_world():
    return {'hello': 'world'}

expected_json = {'hello': 'world'}


def dummy_xml_formatter(dict_items):
    return make_response('<hello>world</hello>')

expected_xml = '<hello>world</hello>'


class ResponsiveFlaskTest(TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_json_response_when_accept_header_is_not_given(self):
        headers = {}
        r = self.app.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.headers['Content-Type'], 'application/json')

    def test_json_response_when_accept_header_means_all_media_types(self):
        headers = {
            'Accept': '*/*',
        }
        r = self.app.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.headers['Content-Type'], 'application/json')

    def test_406_when_accept_header_is_given_but_format_is_unknown(self):
        with self.assertRaises(NotAcceptable):
            headers = {
                'Accept': 'application/vnd.company.myapp.product-v2+xml',
            }
            self.app.get('/', headers=headers)

    def test_json_is_used_because_xml_formatter_is_not_set(self):
        headers = {
            'Accept': 'application/xml,application/json',
        }
        r = self.app.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.headers['Content-Type'], 'application/json')

    def test_xml_is_used_because_xml_formatter_is_set_manually(self):
        app.response_formatters['application/xml'] = dummy_xml_formatter

        headers = {
            'Accept': 'application/xml,application/json',
        }
        r = self.app.get('/', headers=headers)

        self.assertEqual(r.data, expected_xml)
        self.assertEqual(r.headers['Content-Type'], 'application/xml')

    def test_xml_is_used_because_default_mimetype_is_set_manually(self):
        app.default_mimetype = 'application/xml'
        app.response_formatters['application/xml'] = dummy_xml_formatter

        headers = {
            'Accept': '*/*',
        }
        r = self.app.get('/', headers=headers)

        self.assertEqual(r.data, expected_xml)
        self.assertEqual(r.headers['Content-Type'], 'application/xml')

    def test_json_response_is_returned_due_to_quality_factor(self):
        app.response_formatters['application/xml'] = dummy_xml_formatter

        headers = {
            'Accept': 'application/xml;q=0.5,application/json',
        }
        r = self.app.get('/', headers=headers)
        r_json = json.loads(r.data)

        self.assertEqual(r_json, expected_json)
        self.assertEqual(r.headers['Content-Type'], 'application/json')
