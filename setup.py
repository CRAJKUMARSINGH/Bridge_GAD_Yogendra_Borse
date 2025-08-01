"""
Setup script for the Bridge GAD Generator package.

This script allows the package to be installed in development mode using pip.
"""

from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="bridge-gad",
    version="0.1.0",
    author="Bridge GAD Team",
    author_email="your.email@example.com",
    description="A tool for generating bridge general arrangement drawings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bridge-gad",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bridge-gad=bridge_gad.__main__:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Engineers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: CAD",
    ],
    python_requires=">=3.8",
    keywords="bridge cad engineering drawing dxf",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/bridge-gad/issues",
        "Source": "https://github.com/yourusername/bridge-gad",
    },
)
