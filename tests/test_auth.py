# coding: utf-8
import mock
from unittest import TestCase

from flask import Flask
from werkzeug.exceptions import BadRequest, Unauthorized
from api_utils import Hawk
from flask.ext.login import LoginManager

from .utils import HawkTestMixin

app = Flask(__name__)
hawk = Hawk(app)
login_manager = LoginManager(app)

CREDENTIALS = {
    'id': 'Alice',
    'key': 'werxhqb98rpaxn39848xrunpaw3489ruxnpa98w4rxn',
    'algorithm': 'sha256'
}


@hawk.client_key_loader
def get_client_key(client_id):
    if client_id == CREDENTIALS['id']:
        return CREDENTIALS['key']
    else:
        raise LookupError()


@app.route('/', methods=['GET', 'POST'])
@hawk.realm
def protected_view():
    return 'hello world'


class HawkAuthBySignatureTest(TestCase, HawkTestMixin):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        hawk._client_key_loader_func = get_client_key

    def test_successful_auth_when_http_method_is_get(self):
        r = self.signed_request(CREDENTIALS, path='/?hello=world')
        self.assertEqual(r.status_code, 200)

    def test_successful_auth_when_http_method_is_post(self):
        r = self.signed_request(
            CREDENTIALS,
            method='POST',
            path='/?hello=world&fields=id,title',
            data={
                'fizz': 'buzz',
                'blah': '1111'
            }
        )
        self.assertEqual(r.status_code, 200)

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


class HawkAuthByCookieTest(TestCase):
    def setUp(self):
        app.config['SECRET_KEY'] = 'secret'

    def test_401_when_current_user_is_not_authenticated(self):
        with app.test_request_context():
            with self.assertRaises(Unauthorized):
                hawk._auth_by_cookie()

    @mock.patch('api_utils.auth.current_user')
    def test_successful_authentication(self, current_user_):
        current_user_.is_authenticated.return_value = True

        with app.test_request_context():
                hawk._auth_by_cookie()


class HawkSignResponseTest(TestCase, HawkTestMixin):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        app.config['HAWK_SIGN_RESPONSE'] = False

    def test_responses_are_signed_when_hawk_was_configured_to_sign(self):
        app.config['HAWK_SIGN_RESPONSE'] = True
        hawk.init_app(app)

        r = self.signed_request(CREDENTIALS)
        self.assertEqual(r.status_code, 200)
        self.assertIn('Server-Authorization', r.headers)

    def test_responses_are_not_signed_by_default(self):
        r = self.signed_request(CREDENTIALS)
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('Server-Authorization', r.headers)
