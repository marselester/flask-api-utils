=========
Changelog
=========

Version 1.0.2
-------------

- **HAWK_ENABLED** config was added. It can be convenient to globally turn off
  authentication when unit testing.

Version 1.0.1
-------------

- Fix **__all__** tuple issue, thanks @attila
- Fix Flask-Login **user.is_authenticated** compatibility issue

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
