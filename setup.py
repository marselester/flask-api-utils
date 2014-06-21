# coding: utf-8
from distutils.core import setup

setup(
    name='Flask-API-Utils',
    version='1.0.0',
    packages=['api_utils'],
    author='Marsel Mavletkulov',
    author_email='marselester@ya.ru',
    url='https://github.com/marselester/flask-api-utils',
    description='Flask-API-Utils helps you to create APIs.',
    long_description=open('README.rst').read(),
    install_requires=['Flask>=0.10'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
