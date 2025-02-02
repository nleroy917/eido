#! /usr/bin/env python

import os
import sys

from setuptools import setup

# Additional keyword arguments for setup().
extra = {}

# Ordinary dependencies
DEPENDENCIES = []
with open("requirements/requirements-all.txt", "r") as reqs_file:
    for line in reqs_file:
        if not line.strip():
            continue
        # DEPENDENCIES.append(line.split("=")[0].rstrip("<>"))
        DEPENDENCIES.append(line)

extra["install_requires"] = DEPENDENCIES

# Additional files to include with package
def get_static(name, condition=None):
    static = [
        os.path.join(name, f)
        for f in os.listdir(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), name)
        )
    ]
    if condition is None:
        return static
    else:
        return [i for i in filter(lambda x: eval(condition), static)]


# scripts to be added to the $PATH
# scripts = get_static("scripts", condition="'.' in x")
# scripts removed (TO remove this)
scripts = None

with open("eido/_version.py", "r") as versionfile:
    version = versionfile.readline().split()[-1].strip("\"'\n")

with open("README.md") as f:
    long_description = f.read()

setup(
    name="eido",
    packages=["eido"],
    version=version,
    description="A project metadata validator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    keywords="project, metadata, bioinformatics, sequencing, ngs, workflow",
    url="https://github.com/pepkit/eido/",
    author="Michal Stolarczyk, Nathan Sheffield",
    license="BSD2",
    entry_points={
        "console_scripts": ["eido = eido.__main__:main"],
        "pep.filters": [
            "basic=eido.conversion_plugins:basic_pep_filter",
            "yaml=eido.conversion_plugins:yaml_pep_filter",
            "csv=eido.conversion_plugins:csv_pep_filter",
            "yaml-samples=eido.conversion_plugins:yaml_samples_pep_filter",
        ],
    },
    scripts=scripts,
    include_package_data=True,
    test_suite="tests",
    tests_require=(["mock", "pytest"]),
    setup_requires=(
        ["pytest-runner"] if {"test", "pytest", "ptr"} & set(sys.argv) else []
    ),
    **extra
)
