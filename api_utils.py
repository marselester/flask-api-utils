# coding: utf-8
"""
api_utils
~~~~~~~~~

Flask utils which help you to create API.

"""
from flask import Flask, jsonify, request, abort

__all__ = ('ResponsiveFlask',)


class ResponsiveFlask(Flask):
    """Changes Flask behavior to respond in requested format.

    .. code-block:: python

        app = ResponsiveFlask(__name__)


        @app.route('/')
        def hello_world():
            return {'hello': 'world'}


        def dummy_xml_formatter(dict_items):
            return make_response('<hello>world</hello>')

        xml_mimetype = 'application/vnd.company+xml'

        app.default_mimetype = xml_mimetype
        app.response_formatters[xml_mimetype] = dummy_xml_formatter

    """

    default_mimetype = 'application/json'
    response_formatters = {
        'application/json': jsonify,
    }

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
            else:
                abort(406)

        formatter = self.response_formatters.get(response_mimetype)
        if isinstance(rv, dict):
            response = formatter(rv)
            response.headers['Content-Type'] = response_mimetype
            return response

        return super(ResponsiveFlask, self).make_response(rv)
