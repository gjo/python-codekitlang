#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='CodeKitLang',
    version='0.1dev',
    author='gjo',
    author_email='gjo.ext@gmail.com',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [console_scripts]
    pykitlangc = codekitlang.command:main
    """,
)
