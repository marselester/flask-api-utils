# coding: utf-8
import json
from unittest import TestCase

from flask import Flask
from werkzeug.exceptions import BadRequest, Unauthorized
from api_utils.auth import Hawk
import mohawk

app = Flask(__name__)
hawk = Hawk(app)


@hawk.client_key_loader
def get_client_key(client_id):
    if client_id == 'Alice':
        return 'werxhqb98rpaxn39848xrunpaw3489ruxnpa98w4rxn'
    else:
        raise LookupError()


@app.route('/', methods=['GET', 'POST'])
@hawk.realm
def protected_view():
    return 'hello world'


class HawkAuthBySignature(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        hawk._client_key_loader_func = get_client_key

    def test_runtime_error_when_client_key_loader_was_not_defined(self):
        hawk._client_key_loader_func = None

        with app.test_request_context():
            message = 'Client key loader function was not defined'
            with self.assertRaisesRegexp(RuntimeError, message):
                hawk._auth_by_signature()

    def test_401_when_there_is_no_authorization_header(self):
        with app.test_request_context():
            with self.assertRaises(Unauthorized):
                hawk._auth_by_signature()

    def test_400_when_authorization_header_has_wrong_scheme(self):
        headers = {
            'Authorization': 'blah'
        }
        with app.test_request_context(headers=headers):
            with self.assertRaises(BadRequest) as cm:
                hawk._auth_by_signature()
            self.assertEqual(cm.exception.description, 'Unknown scheme: blah')

    def test_401_when_client_was_not_found(self):
        headers = {
            'Authorization': 'Hawk mac="", hash="", id="Bob", ts="", nonce=""'
        }
        with app.test_request_context(headers=headers):
            with self.assertRaises(Unauthorized) as cm:
                hawk._auth_by_signature()
            message = 'Could not find credentials for ID Bob'
            self.assertEqual(cm.exception.description, message)

    def test_401_response_doesnt_contain_computed_mac(self):
        headers = {
            'Authorization': 'Hawk mac="", hash="", id="Alice", ts="", nonce=""'
        }
        with app.test_request_context(headers=headers):
            with self.assertRaises(Unauthorized) as cm:
                hawk._auth_by_signature()
            message = 'MACs do not match; ours:'
            self.assertNotIn(message, cm.exception.description)

    def test_400_when_mohawk_cant_find_mac_and_raises_key_error(self):
        headers = {
            'Authorization': 'Hawk hash="", id="Alice", ts="", nonce=""'
        }
        with app.test_request_context(headers=headers):
            with self.assertRaises(BadRequest):
                hawk._auth_by_signature()

    def test_successfull_auth_when_http_method_is_get(self):
        data = {}
        credentials = {
            'id': 'Alice',
            'key': 'werxhqb98rpaxn39848xrunpaw3489ruxnpa98w4rxn',
            'algorithm': 'sha256'
        }
        url = 'http://localhost/?hello=world'
        method = 'GET'
        content = json.dumps(data)
        content_type = 'application/json'

        sender = mohawk.Sender(
            credentials,
            url,
            method,
            content,
            content_type
        )

        r = self.app.get(
            '/',
            headers={
                'Authorization': sender.request_header
            },
            query_string={
                'hello': 'world'
            },
            data=content,
            content_type=content_type
        )
        expected_status_code = 200
        self.assertEqual(r.status_code, expected_status_code)

    def test_successfull_auth_when_http_method_is_post(self):
        data = {
            'fizz': 'buzz',
            'blah': '1111'
        }
        credentials = {
            'id': 'Alice',
            'key': 'werxhqb98rpaxn39848xrunpaw3489ruxnpa98w4rxn',
            'algorithm': 'sha256'
        }
        url = 'http://localhost/?hello=world'
        method = 'POST'
        content = json.dumps(data)
        content_type = 'application/json'

        sender = mohawk.Sender(
            credentials,
            url,
            method,
            content,
            content_type
        )

        r = self.app.post(
            '/',
            headers={
                'Authorization': sender.request_header
            },
            query_string={
                'hello': 'world'
            },
            data=content,
            content_type=content_type
        )
        expected_status_code = 200
        self.assertEqual(r.status_code, expected_status_code)
