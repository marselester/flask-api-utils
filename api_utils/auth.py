# coding: utf-8
"""
api_utils.auth
~~~~~~~~~~~~~~

This module provides API authentication based on Hawk scheme and
Flask-Login extension.

"""
from functools import wraps

from flask import request, session, current_app
from werkzeug.exceptions import BadRequest, Unauthorized
try:
    import mohawk
    from flask.ext.login import current_user
except ImportError:
    pass

from . import compat

__all__ = ('Hawk',)


class Hawk(object):
    """HTTP authentication scheme using a message authentication code
    (MAC) algorithm.

    Instances are *not* bound to specific apps.

    """
    def __init__(self, app=None):
        self._client_key_loader_func = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('HAWK_ENABLED', True)
        app.config.setdefault('HAWK_SIGN_RESPONSE', False)
        app.config.setdefault('HAWK_ALLOW_COOKIE_AUTH', False)
        app.config.setdefault('HAWK_ALGORITHM', 'sha256')
        app.config.setdefault('HAWK_ACCEPT_UNTRUSTED_CONTENT', False)
        app.config.setdefault('HAWK_LOCALTIME_OFFSET_IN_SECONDS', 0)
        app.config.setdefault('HAWK_TIMESTAMP_SKEW_IN_SECONDS', 60)

        if app.config['HAWK_SIGN_RESPONSE']:
            app.after_request(self._sign_response)

    def client_key_loader(self, f):
        """Registers a function to be called to find a client key.

        Function you set has to take a client id and return a client key::

            @hawk.client_key_loader
            def get_client_key(client_id):
                if client_id == 'Alice':
                    return 'werxhqb98rpaxn39848xrunpaw3489ruxnpa98w4rxn'
                else:
                    raise LookupError()

        :param f: The callback for retrieving a client key.

        """
        @wraps(f)
        def wrapped_f(client_id):
            client_key = f(client_id)
            return {
                'id': client_id,
                'key': client_key,
                'algorithm': current_app.config['HAWK_ALGORITHM']
            }

        self._client_key_loader_func = wrapped_f
        return wrapped_f

    def auth_required(self, view_func):
        """Decorator that provides an access to view function for
        authenticated users only.

        Note that we don't run authentication when `HAWK_ENABLED` is `False`.

        """
        @wraps(view_func)
        def wrapped_view_func(*args, **kwargs):
            if current_app.config['HAWK_ENABLED']:
                if current_app.config['HAWK_ALLOW_COOKIE_AUTH'] and session:
                    self._auth_by_cookie()
                else:
                    self._auth_by_signature()
            return view_func(*args, **kwargs)

        return wrapped_view_func

    def _auth_by_cookie(self):
        if not compat.is_user_authenticated(current_user):
            raise Unauthorized()

    def _auth_by_signature(self):
        if self._client_key_loader_func is None:
            raise RuntimeError('Client key loader function was not defined')
        if 'Authorization' not in request.headers:
            raise Unauthorized()

        try:
            mohawk.Receiver(
                credentials_map=self._client_key_loader_func,
                request_header=request.headers['Authorization'],
                url=request.url,
                method=request.method,
                content=request.get_data(),
                content_type=request.mimetype,
                accept_untrusted_content=current_app.config['HAWK_ACCEPT_UNTRUSTED_CONTENT'],
                localtime_offset_in_seconds=current_app.config['HAWK_LOCALTIME_OFFSET_IN_SECONDS'],
                timestamp_skew_in_seconds=current_app.config['HAWK_TIMESTAMP_SKEW_IN_SECONDS']
            )
        except mohawk.exc.MacMismatch:
            # mohawk exception contains computed MAC.
            # We should not expose it in response.
            raise Unauthorized()
        except (
            mohawk.exc.CredentialsLookupError,
            mohawk.exc.AlreadyProcessed,
            mohawk.exc.MisComputedContentHash,
            mohawk.exc.TokenExpired
        ) as e:
            raise Unauthorized(str(e))
        except mohawk.exc.HawkFail as e:
            raise BadRequest(str(e))
        except KeyError:
            raise BadRequest()

    def _sign_response(self, response):
        """Signs a response if it's possible."""
        if 'Authorization' not in request.headers:
            return response

        try:
            mohawk_receiver = mohawk.Receiver(
                credentials_map=self._client_key_loader_func,
                request_header=request.headers['Authorization'],
                url=request.url,
                method=request.method,
                content=request.get_data(),
                content_type=request.mimetype,
                accept_untrusted_content=current_app.config['HAWK_ACCEPT_UNTRUSTED_CONTENT'],
                localtime_offset_in_seconds=current_app.config['HAWK_LOCALTIME_OFFSET_IN_SECONDS'],
                timestamp_skew_in_seconds=current_app.config['HAWK_TIMESTAMP_SKEW_IN_SECONDS']
            )
        except mohawk.exc.HawkFail:
            return response

        response.headers['Server-Authorization'] = mohawk_receiver.respond(
            content=response.data,
            content_type=response.mimetype
        )
        return response
