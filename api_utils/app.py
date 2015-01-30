# coding: utf-8
"""
api_utils.app
~~~~~~~~~~~~~

This module helps to make responses in appropriate formats.

"""
from werkzeug.exceptions import default_exceptions
from flask import Flask, request

from . import formatters

__all__ = ('ResponsiveFlask',)


class ResponsiveFlask(Flask):
    """Changes Flask behavior to respond in requested format.

    .. code-block:: python

        app = ResponsiveFlask(__name__)


        @app.route('/')
        def hello_world():
            return {'hello': 'world'}


        def dummy_xml_formatter(*args, **kwargs):
            return '<hello>world</hello>'

        xml_mimetype = 'application/vnd.company+xml'

        app.default_mimetype = xml_mimetype
        app.response_formatters[xml_mimetype] = dummy_xml_formatter

    """
    def __init__(self, *args, **kwargs):
        super(ResponsiveFlask, self).__init__(*args, **kwargs)
        self.default_mimetype = 'application/json'
        self.response_formatters = {
            'application/json': formatters.json
        }

    def default_errorhandler(self, f):
        """Decorator that registers handler of default (Werkzeug) HTTP errors.

        Note that it might override already defined error handlers.

        """
        for http_code in default_exceptions:
            self.error_handler_spec[None][http_code] = f
        return f

    def _response_mimetype_based_on_accept_header(self):
        """Determines mimetype to response based on Accept header.

        If mimetype is not found, it returns ``None``.

        """
        response_mimetype = None

        if not request.accept_mimetypes:
            response_mimetype = self.default_mimetype
        else:
            all_media_types_wildcard = '*/*'

            for mimetype, q in request.accept_mimetypes:
                if mimetype == all_media_types_wildcard:
                    response_mimetype = self.default_mimetype
                    break
                if mimetype in self.response_formatters:
                    response_mimetype = mimetype
                    break

        return response_mimetype

    def make_response(self, rv):
        """Returns response based on Accept header.

        If no Accept header field is present, then it is assumed that
        the client accepts all media types. This way JSON format will
        be used.

        If an Accept header field is present, and if the server cannot
        send a response which is acceptable according to the combined
        Accept field value, then a 406 (not acceptable) response will
        be sent.

        """
        status = headers = None
        if isinstance(rv, tuple):
            rv, status, headers = rv + (None,) * (3 - len(rv))

        response_mimetype = self._response_mimetype_based_on_accept_header()
        if response_mimetype is None:
            # Return 406, list of available mimetypes in default format.
            default_formatter = self.response_formatters.get(
                self.default_mimetype
            )
            available_mimetypes = default_formatter(
                mimetypes=list(self.response_formatters)
            )

            rv = self.response_class(
                response=available_mimetypes,
                status=406,
                mimetype=self.default_mimetype,
            )
        elif isinstance(rv, dict):
            formatter = self.response_formatters.get(response_mimetype)
            rv = self.response_class(
                response=formatter(**rv),
                mimetype=response_mimetype,
            )

        return super(ResponsiveFlask, self).make_response(
            rv=(rv, status, headers)
        )
