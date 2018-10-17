from setuptools import setup

__version__ = "1.1.1"

setup(
    name="aresponses",
    packages=["aresponses"],
    version=__version__,
    description="Asyncio testing server. Similar to the responses library used for 'requests'",
    author="Bryce Drennan, CircleUp",
    author_email="aresponses@brycedrennan.com   ",
    url="https://github.com/circleup/aresponses",
    download_url="https://github.com/circleup/aresponses/tarball/" + __version__,
    keywords=["asyncio", "testing", "responses"],
    classifiers=["Programming Language :: Python :: 3.6"],
    python_requires=">=3.6",
    install_requires=["aiohttp==3.*,>=3.1.0", "pytest-asyncio"],
    # the following makes a plugin available to pytest
    entry_points={"pytest11": ["name_of_plugin = aresponses.main"]},
)
