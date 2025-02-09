#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Testing",
]

setup(
    name="pure-python-adb",
    version="0.3.0-dev",
    description="Pure python implementation of the adb client, forked and maintained",
    long_description=readme + "\n\n" + history,
    author="Sergio Martins",
    author_email="",
    url="https://github.com/spm5065/pure-python-adb",
    license="MIT license",
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    install_requires=[],
    extras_require={"async": ["aiofiles>=0.4.0"]},
    keywords="adb",
    classifiers=classifiers,
)
