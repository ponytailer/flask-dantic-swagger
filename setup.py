from os import path, environ
from setuptools import setup, find_packages


if "CI_COMMIT_TAG" in environ:
    __version__ = environ["CI_COMMIT_TAG"].lstrip("v")
elif path.isfile("VERSION"):
    with open("VERSION", "r") as f:
        __version__ = f.read().strip()
else:
    __version__ = "0.0.1-dev"


with open("VERSION", "wt") as f:
    f.write(__version__)
    f.write("\n")


setup(
    name="flask-dantic-swagger",
    version=__version__,
    description="validate, auto swagger",
    url="https://github.com/huangxiaohen2738/flask-dantic-swagger",
    author="Huang Song",
    packages=find_packages(),
    data_files=[
        ("./", ["VERSION"])
    ],
    install_requires=[
        "flask",
        "requests",
        "arrow",
        "pydantic",
    ],
    classifiers=[
        "Development Status :: 4 - Beta"
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Topic :: Utilities"
    ]
)
