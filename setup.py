#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()

setup(
    name='datavault',
    version='0.0.0',
    description="Datavault will guard your data and give it to you if you need it.",
    long_description=readme + '\n\n' + history,
    author="Aniket Panse",
    author_email='aniket-panse@tamu.edu',
    url='https://github.com/aniket-panse/datavault',
    packages=find_packages(include=['datavault']),
    entry_points={
        'console_scripts': [
            'datavault=datavault.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='datavault',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7'
    ],
    test_suite='tests',
    tests_require=[],
    setup_requires=[],
)
