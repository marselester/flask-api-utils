===============
Flask API Utils
===============

Flask utils which help you to create API.

"Accept" Header based Response
------------------------------

It tries to follow RFC 2616, **Accept** request-header.

.. code-block:: python

    from flask import make_response
    from api_utils import ResponsiveFlask


    app = ResponsiveFlask(__name__)


    @app.route('/')
    def hello_world():
        return {'hello': 'world'}


    def dummy_xml_formatter(dict_items):
        return make_response('<hello>world</hello>')

    xml_mimetype = 'application/vnd.company+xml'

    app.default_mimetype = xml_mimetype
    app.response_formatters[xml_mimetype] = dummy_xml_formatter

    if __name__ == '__main__':
        app.run()

It's assumed that file was saved as ``api.py``:

.. code-block:: console

    $ python api.py
     * Running on http://127.0.0.1:5000/

Here are curl examples:

.. code-block:: console

    $ curl http://127.0.0.1:5000/
    <hello>world</hello>
    $ curl http://127.0.0.1:5000/ -H 'Accept: application/json'
    {
      "hello": "world"
    }

Tests are run by:

.. code-block:: console

    $ pip install -r requirements.txt
    $ nosetest
