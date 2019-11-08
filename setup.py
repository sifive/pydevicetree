# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
        name="pydevicetree",
        version="0.0.4",
        author="Nathaniel Graff",
        author_email="nathaniel.graff@sifive.com",
        description="A library for parsing Devicetree Source v1",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/sifive/pydevicetree",
        packages=setuptools.find_packages(),
	classifiers=[
	    "Programming Language :: Python :: 3",
	    "License :: OSI Approved :: Apache Software License",
	    "Operating System :: OS Independent",
	],
	python_requires=">=3.5",
        install_requires=[
            "mypy",
            "pyparsing",
        ],
)
