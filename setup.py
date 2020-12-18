from os.path import isfile
from setuptools import setup, find_packages

setup(
    name = "zoomzt2",
    version = "0.4.0",
    author = "Simon Wood",
    author_email = "simon@mungewell.org",
    description = 'Script for Upload Effects/Configuration to ZOOM G Series Pedals',
    license = "GPLv3",
    keywords = "Zoom Pedal",
    url = "https://github.com/mungewell/zoom-zt2",
    py_modules=["zoomzt2"],
    long_description=open("README.rst").read() if isfile("README.rst") else "",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3"
    ],
)
