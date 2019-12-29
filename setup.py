#!/usr/bin/env python
"""The setup script."""
import codecs
import subprocess

from setuptools import setup, find_packages


def _get_git_tag():
    label = subprocess.check_output(["git", "describe"]).strip().decode("utf8")
    return str(label)


with codecs.open("README.md", "r", "utf-8") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as reqs:
    requirements = [line.strip() for line in reqs]

with open("requirements-dev.txt") as reqs:
    requirements_dev = [line.strip() for line in reqs if "requirements.txt" not in line.strip()]


setup(
    name="eduzen_bot",
    version=_get_git_tag(),
    # cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/eduzen/bot",
    description="This is the eduzen_bot for telegram",
    long_description=readme,
    author="eduzen",
    author_email="eduardo.a.enriquez@gmail.com",
    packages=find_packages(include=["eduzen_bot*"]),
    include_package_data=True,
    install_requires=requirements,
    keywords="eduzen_bot",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: Spanish",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    tests_require=requirements + requirements_dev,
    entry_points={"database_scripts": ["initialize_db = eduzen_bot.scripts.initialize_db:main"]},
)
