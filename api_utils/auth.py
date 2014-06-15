# coding: utf-8
from functools import wraps

from flask import request, current_app
from werkzeug.exceptions import BadRequest, Unauthorized
import mohawk


class Hawk(object):
    """HTTP authentication scheme using a message authentication code
    (MAC) algorithm.

    Instances are *not* bound to specific apps.

    """
    def __init__(self, app=None):
        self.lookup_client_key_func = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('HAWK_ALGORITHM', 'sha256')

    def client_key_loader(self, f):
        """Registers a function to be called to find a client key.

        Function you set has to take a client id and return a client key::

            @hawk.client_key_loader
            def lookup_client_key(client_id):
                if client_id == 'Steve':
                    return 'werxhqb98rpaxn39848xrunpaw3489ruxnpa98w4rxn'

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

        self.lookup_client_key_func = wrapped_f
        return wrapped_f

    def verify(self, view_func):
        """Decorator that verifies HTTP requests."""
        @wraps(view_func)
        def wrapped_view_func(*args, **kwargs):
            if 'Authorization' not in request.headers:
                raise Unauthorized()
            if 'Content-Type' not in request.headers:
                raise BadRequest('Content-Type header is required')

            try:
                mohawk.Receiver(
                    credentials_map=self.lookup_client_key_func,
                    request_header=request.headers['Authorization'],
                    url=request.url,
                    method=request.method,
                    content=request.data,
                    content_type=request.headers['Content-Type']
                )
            except (
                mohawk.exc.AlreadyProcessed,
                mohawk.exc.MacMismatch,
                mohawk.exc.MisComputedContentHash,
                mohawk.exc.TokenExpired
            ) as e:
                raise Unauthorized(e)
            except mohawk.exc.HawkFail as e:
                raise BadRequest(e)
            else:
                return view_func(*args, **kwargs)

        return wrapped_view_func
