# coding: utf-8
"""
api_utils.error_handlers
~~~~~~~~~~~~~~~~~~~~~~~~

The aim of HTTP error handler is to make response value from given
Werkzeug's default exception.

"""


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
