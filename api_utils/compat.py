# coding: utf-8
"""
api_utils.compat
~~~~~~~~~~~~~~~~

The compat module provides support for backwards compatibility with older
versions of packages.

"""


def is_user_authenticated(user):
    """Returns True if Flask-Login's `user` is authenticated.

    Flask-Login extension has changed `current_user.is_authenticated()`
    to bool value.

    """
    if callable(user.is_authenticated):
        return user.is_authenticated()
    else:
        return user.is_authenticated
