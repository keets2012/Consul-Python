# encoding: utf-8
from setuptools import setup, find_packages
from consul import __version__ as version

setup(
    name = 'consul-python',
    version = version,
    description = 'A python interface for consul',
    author = u'keets',
    author_email = 'keets001@gmail.com',
    zip_safe=False,
    include_package_data = True,
    packages = find_packages(exclude=[]),
    install_requires=[
        'dnspython'
    ],
)