#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap-wincher",
    version="0.1.0",
    description="Singer.io tap for extracting data",
    author="Yoast",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_wincher"],
    install_requires=[
        # NB: Pin these to a more specific version for tap reliability
        "singer-python",
        "requests",
        "httpx",
        "httpx[http2]",
    ],
    entry_points="""
    [console_scripts]
    tap-wincher=tap_wincher:main
    """,
    packages=["tap_wincher"],
    package_data = {
        "schemas": ["tap_wincher/schemas/*.json"]
    },
    include_package_data=True,
)
