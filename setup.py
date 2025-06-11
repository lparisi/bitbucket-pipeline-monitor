"""
Setup script for the Bitbucket Pipeline Monitor CLI.
"""
from typing import List
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements: List[str] = fh.read().splitlines()

setup(
    name="bitbucket-pipeline-monitor",
    version="0.1.0",
    author="Lucas Parisi",
    author_email="your.email@example.com",
    description="A CLI tool for monitoring Bitbucket pipeline executions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lparisi/bitbucket-pipeline-monitor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bitbucket-pipeline=bitbucket_monitor.cli:main",
        ],
    },
)
