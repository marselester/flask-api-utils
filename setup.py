# coding: utf-8
from distutils.core import setup


setup(
    name='Flask-API-Utils',
    version='0.2.0',
    packages=['api_utils'],
    author='Marsel Mavletkulov',
    author_email='marselester@ya.ru',
    url='https://github.com/marselester/flask-api-utils',
    description='Flask utils which help you to create API.',
    long_description=open('README.rst').read(),
    install_requires=['Flask>=0.10'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
