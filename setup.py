#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools.command.test import test as TestCommand
import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'WTForms>=2.0.2',
    'six>=1.9.0',
]

test_requirements = [
    'tox>=2.1.1',
]

setup(
    name='minform',
    version='0.1.2',
    description="WTForms/struct integration to validate and serialize to packed buffers of binary data.",
    long_description=readme + '\n\n' + history,
    author="David Donna",
    author_email='davidadonna@gmail.com',
    url='https://github.com/daviddonna/minform',
    packages=[
        'minform',
    ],
    package_dir={'minform':
                 'minform'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='minform wtforms struct binary',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass={'test': Tox},
)
