#!/usr/bin/env python3
"""
Setup script for SendApi Desktop Application
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sendapi",
    version="1.0.0",
    author="SendApi Team",
    author_email="support@sendapi.com",
    description="A powerful desktop API testing application built with PySide6",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/yourusername/sendapi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "sendapi=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        '': ['data/*.json', 'docs/*.md'],
    },
    keywords="api testing http requests desktop application",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/sendapi/issues",
        "Source": "https://github.com/yourusername/sendapi",
        "Documentation": "https://github.com/yourusername/sendapi/blob/main/README.md",
    },
) 