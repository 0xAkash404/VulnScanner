#!/usr/bin/env python3
"""
Setup script for Vulnerability Scanner package.
Enables installation via: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="vulnscanner",
    version="2.0.0",
    author="Security Team",
    description="Production-ready vulnerability scanner for network security assessment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "flask>=2.3.0",
        "reportlab>=4.0.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "vulnscanner=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking",
        "Topic :: Security",
    ],
    keywords="vulnerability scanner network security assessment",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/vulnscanner/issues",
        "Source": "https://github.com/yourusername/vulnscanner",
    },
)
