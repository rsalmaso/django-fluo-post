#!/usr/bin/env python3

import io

import posts
from setuptools import find_packages, setup

with io.open("README.md", "rt", encoding="utf-8") as fp:
    long_description = fp.read()


setup(
    packages=find_packages(),
    include_package_data=True,
    name="django-fluo-post",
    version=posts.__version__,
    description="Integrate posts with django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=posts.__author__,
    author_email=posts.__email__,
    url="https://bitbucket.org/rsalmaso/django-fluo-posts",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=["django-fluo"],
    zip_safe=False,
)
