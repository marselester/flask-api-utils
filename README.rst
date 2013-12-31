===============
Flask API Utils
===============

.. image:: https://travis-ci.org/marselester/flask-api-utils.png
   :target: https://travis-ci.org/marselester/flask-api-utils

Flask utils which help you to create API.

"Accept" Header based Response
------------------------------

It tries to follow RFC 2616, **Accept** request-header.

.. code-block:: python

    from flask import request
    from api_utils import ResponsiveFlask


    app = ResponsiveFlask(__name__)


    @app.route('/')
    def hello_world():
        return {'hello': 'world'}


    @app.route('/yarr')
    def hello_bad_request():
        request.args['bad-key']


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

Here are curl examples with different **Accept** headers:

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

Error Handling
--------------

``ResponsiveFlask`` even formats built in Werkzeug HTTP exceptions.

.. code-block:: console

    $ curl http://127.0.0.1:5000/yarr -i
    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json
    Content-Length: 51
    Server: Werkzeug/0.9.4 Python/2.7.5
    Date: Tue, 10 Dec 2013 04:55:40 GMT

    {
      "code": 400,
      "message": "400: Bad Request"
    }

You can set your own HTTP error handler by using ``app.default_errorhandler``
decorator. Note that it might override already defined error handlers,
so you should declare it before them.

.. code-block:: python

    from flask import request
    from api_utils import ResponsiveFlask


    app = ResponsiveFlask(__name__)


    @app.default_errorhandler
    def werkzeug_default_exceptions_handler(error):
        error_info_url = (
            'http://developer.example.com/errors.html#error-code-{}'
        ).format(error.code)

        response = {
            'code': error.code,
            'message': str(error),
            'info_url': error_info_url,
        }
        return response, error.code


    @app.errorhandler(404)
    def page_not_found(error):
        return {'error': 'This page does not exist'}, 404


    class MyException(Exception):
        pass


    @app.errorhandler(MyException)
    def special_exception_handler(error):
        return {'error': str(error)}


    @app.route('/my-exc')
    def hello_my_exception():
        raise MyException('Krivens!')


    @app.route('/yarr')
    def hello_bad_request():
        request.args['bad-key']


    if __name__ == '__main__':
        app.run()


Let's try to curl this example. First response shows that we redefined
default ``{'code': 400, 'message': '400: Bad Request'}`` error format.
Next ones show that you can handle specific errors as usual.

.. code-block:: console

    $ curl http://127.0.0.1:5000/yarr -i
    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json
    Content-Length: 125
    Server: Werkzeug/0.9.4 Python/2.7.5
    Date: Sun, 29 Dec 2013 14:26:30 GMT

    {
      "code": 400,
      "info_url": "http://developer.example.com/errors.html#error-code-400",
      "message": "400: Bad Request"
    }
    $ curl http://127.0.0.1:5000/ -i
    HTTP/1.0 404 NOT FOUND
    Content-Type: application/json
    Content-Length: 41
    Server: Werkzeug/0.9.4 Python/2.7.5
    Date: Sun, 29 Dec 2013 14:28:46 GMT

    {
      "error": "This page does not exist"
    }
    $ curl http://127.0.0.1:5000/my-exc -i
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 25
    Server: Werkzeug/0.9.4 Python/2.7.5
    Date: Sun, 29 Dec 2013 14:27:33 GMT

    {
      "error": "Krivens!"
    }

Tests
-----

Tests are run by:

.. code-block:: console

    $ pip install -r requirements.txt
    $ tox
