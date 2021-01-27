#!/usr/bin/env python
"""The setup script."""
import codecs
import os

from setuptools import find_packages, setup


def _get_tag():
    return os.getenv("TAG", "dev")


with codecs.open("README.md", "r", "utf-8") as readme_file:
    readme = readme_file.read()

# with open("requirements.txt") as reqs:
#     requirements = [line.strip() for line in reqs]

# with open("requirements-dev.txt") as reqs:
#     requirements_dev = [line.strip() for line in reqs if "requirements.txt" not in line.strip()]


setup(
    name="eduzen_bot",
    version=_get_tag(),
    # cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/eduzen/bot",
    description="This is the eduzen_bot for telegram",
    long_description=readme,
    author="eduzen",
    author_email="eduardo.a.enriquez@gmail.com",
    packages=find_packages(include=["eduzen_bot*"]),
    include_package_data=True,
    install_requires=["python-telegram-bot"],
    keywords="eduzen_bot",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: Spanish",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    # tests_require=requirements,
    entry_points={"database_scripts": ["initialize_db = eduzen_bot.scripts.initialize_db:main"]},
)
