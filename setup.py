from setuptools import find_packages
from setuptools import setup


setup(
    name="dumpster",
    version="0.1",
    author="Ritchie Vink",
    author_email="ritchie46@gmail.com",
    url="https://www.ritchievink.com",
    packages=find_packages(),
    install_requires=[
        "google-cloud-storage>=1.20.0",
    ],
    python_requires=">=3.6",
)