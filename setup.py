from os import path

from setuptools import setup

__version__ = "2.1.4"

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
    author="Bryce Drennan, CircleUp",
    author_email="aresponses@brycedrennan.com   ",
    url="https://github.com/circleup/aresponses",
    download_url="https://github.com/circleup/aresponses/tarball/" + __version__,
    keywords=["asyncio", "testing", "responses"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
    install_requires=["aiohttp==3.*,>=3.1.0", "pytest-asyncio"],
    # the following makes a plugin available to pytest
    entry_points={"pytest11": ["name_of_plugin = aresponses.main"]},
)
