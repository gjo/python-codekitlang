#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


setup(
    name='CodeKitLang',
    version='0.2',
    description='CodeKit Language Compiler, Python implementation',
    long_description='\n\n'.join([
        open('README.rst').read(),
        open('CHANGES.txt').read(),
    ]),
    author='OCHIAI, Gouji',
    author_email='gjo.ext@gmail.com',
    url='https://github.com/gjo/python-codekitlang',
    license='BSD',
    packages=find_packages(exclude=["*.tests"]),
    include_package_data=False,
    zip_safe=False,
    install_requires=('setuptools',),
    tests_require=('pytest-cov', 'pytest-pep8', 'pytest-flakes', 'mock',),
    cmdclass={'test': PyTest},
    test_suite = 'codekitlang.tests',
    entry_points={
        'console_scripts': (
            'pykitlangc = codekitlang.command:main',
        ),
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
)
