# coding: utf-8
"""
api_utils.formatters
~~~~~~~~~~~~~~~~~~~~

The aim of formatter is to convert dict to needed string representation.

"""
from flask import request, current_app, json as flask_json


def json(*args, **kwargs):
    indent = None
    if (current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and
            not request.is_xhr):
        indent = 2
    return flask_json.dumps(dict(*args, **kwargs), indent=indent)
