=========
Changelog
=========

Version 1.0.1
-------------

- fix `__all__` tuple issue, thanks @attila
- fix Flask-Login `user.is_authenticated` compatibility issue

Version 1.0.0
-------------

Release contains interface changes.

- Hawk extension was added. It supports Hawk HTTP authentication scheme
  and Flask-Login extension.
- Default HTTP error handler was removed from **ResponsiveFlask**.
  You have to manually set your own one by using
  **@app.default_errorhandler** decorator.

Version 0.2.0
-------------

- Http error handling was added.

Version 0.1.0
-------------

- Initial release.
