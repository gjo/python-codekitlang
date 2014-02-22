#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='CodeKitLang',
    version='0.2dev',
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
    test_suite = 'codekitlang.tests',
    install_requires=('setuptools', 'mock',),
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
