#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="open-deep-research",
    version="0.1.0",
    author="Pasquale Minervini",
    author_email="p.minervini@gmail.com",
    description="Open Deep Research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pminervini/open-deep-research",
    project_urls={
        "Bug Reports": "https://github.com/pminervini/open-deep-research/issues",
        "Source": "https://github.com/pminervini/open-deep-research",
        "Blog Post": "https://huggingface.co/blog/open-deep-research",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Text Processing :: Indexing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "ruff>=0.1.0",
            "black>=23.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    # entry_points={
    #     "console_scripts": [
    #         "open-deep-research=cli.research-agent-cli:main",
    #         "open-deep-research-eval=cli.gaia-eval-cli:main",
    #         "open-deep-research-search=cli.search-cli:main",
    #     ],
    # },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "artificial intelligence",
        "machine learning",
        "research",
        "web scraping",
        "multi-agent",
        "openai",
        "gaia",
        "benchmark",
    ],
)