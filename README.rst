===============
Flask API Utils
===============

Flask utils which help you to create API.

"Accept" Header based Response
------------------------------

It tries to follow RFC 2616, **Accept** request-header.

.. code-block:: python

    from api_utils import ResponsiveFlask


    app = ResponsiveFlask(__name__)


    @app.route('/')
    def hello_world():
        return {'hello': 'world'}


    def dummy_xml_formatter(*args, **kwargs):
        return '<hello>world</hello>'

    xml_mimetype = 'application/vnd.company+xml'
    app.response_formatters[xml_mimetype] = dummy_xml_formatter

    if __name__ == '__main__':
        app.run()


It's assumed that file was saved as ``api.py``:

.. code-block:: console

    $ python api.py
     * Running on http://127.0.0.1:5000/

Here are curl examples:

.. code-block:: console

    $ curl http://127.0.0.1:5000/ -i
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 22
    Server: Werkzeug/0.9.4 Python/2.7.5
    Date: Sat, 07 Dec 2013 14:01:14 GMT

    {
      "hello": "world"
    }
    $ curl http://127.0.0.1:5000/ -H 'Accept: application/vnd.company+xml' -i
    HTTP/1.0 200 OK
    Content-Type: application/vnd.company+xml; charset=utf-8
    Content-Length: 20
    Server: Werkzeug/0.9.4 Python/2.7.5
    Date: Sat, 07 Dec 2013 14:01:50 GMT

    <hello>world</hello>
    $ curl http://127.0.0.1:5000/ -H 'Accept: blah/*' -i
    HTTP/1.0 406 NOT ACCEPTABLE
    Content-Type: application/json
    Content-Length: 83
    Server: Werkzeug/0.9.4 Python/2.7.5
    Date: Sat, 07 Dec 2013 14:02:23 GMT

    {
      "mimetypes": [
        "application/json",
        "application/vnd.company+xml"
      ]
    }

Tests are run by:

.. code-block:: console

    $ pip install -r requirements.txt
    $ tox
