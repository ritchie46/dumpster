from setuptools import find_namespace_packages
from setuptools import setup


setup(
    name="dumpster",
    version="0.1a",
    author="Ritchie Vink",
    author_email="ritchie46@gmail.com",
    url="https://www.ritchievink.com",
    packages=find_namespace_packages(),
    install_requires=[
        "google-cloud-storage>=1.20.0",
    ],
    python_requires=">=3.6",
)