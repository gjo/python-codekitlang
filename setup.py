#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='CodeKitLang',
    version='0.1.2',
    description='CodeKit Language Compiler, Python implementation',
    long_description='\n\n'.join([
        open('README.rst').read(),
        open('CHANGES.txt').read(),
    ]),
    author='OCHIAI, Goji',
    author_email='gjo.ext@gmail.com',
    url='https://github.com/gjo/python-codekitlang',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
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
