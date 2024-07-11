from os import path

from setuptools import setup

__version__ = "3.0.0"

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="aresponses",
    packages=["aresponses"],
    version=__version__,
    description="""
    Asyncio response mocking. Similar to the responses library used for 'requests'
    """.strip(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bryce Drennan",
    author_email="aresponses@brycedrennan.com   ",
    url="https://github.com/aresponses/aresponses",
    download_url="https://github.com/aresponses/aresponses/tarball/" + __version__,
    keywords=["asyncio", "testing", "responses"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    install_requires=[
        'aiohttp<3.9.0,>=3.1.0; python_version>="3.7" and python_version<"3.8"',
        'aiohttp>=3.6.0; python_version>="3.8" and python_version<"3.10"',
        'aiohttp>=3.7.0; python_version>="3.10" and python_version<"3.12"',
        'aiohttp>=3.7.0,!=3.8.*; python_version>="3.12"',
        'pytest'
    ],
    extras_require={
        'pytest-asyncio': [
            'pytest-asyncio==0.16.0; python_version<"3.7"',
            'pytest-asyncio>=0.17.0; python_version>="3.7"',
        ]
    },
    # the following makes a plugin available to pytest
    entry_points={"pytest11": ["aresponses = aresponses.main"]},
)
