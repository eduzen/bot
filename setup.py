#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import sys
import codecs

from setuptools import setup, find_packages
import versioneer

with codecs.open("README.md", "r", "utf-8") as readme_file:
    readme = readme_file.read()

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported")

requirements_urls = {}

requirements = []

requirements.extend(requirements_urls.keys())

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

dependency_links = list(requirements_urls.values())


package_name = "eduzen_bot"


setup(
    name=package_name,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/eduzen/bot",
    description="This is the eduzen_bot for telegram",
    long_description=readme,
    author="eduzen",
    author_email="eduardo.a.enriquez@gmail.com",
    packages=find_packages(include=["eduzen_bot*"]),
    include_package_data=True,
    install_requires=requirements,
    dependency_links=dependency_links,
    zip_safe=False,
    keywords="eduzen_bot",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: Spanish",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    entry_points={
        "database_scripts": ["initialize_db = eduzen_bot.scripts.initialize_db:main"]
    },
)
