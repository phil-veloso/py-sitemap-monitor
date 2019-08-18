# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='uptime monitor',
    version='0.1.0',
    description='Monitor website uptime via sitemap',
    long_description=readme,
    author='Phil Veloso',
    author_email='phil@inquisitive.solutions',
    url='https://github.com/phil-veloso/py-uptime-monitor',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)