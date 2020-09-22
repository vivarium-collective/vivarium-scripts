import os
import glob
import setuptools
from distutils.core import setup

with open("README.md", 'r') as readme:
    long_description = readme.read()

setup(
    name='vivarium-scripts',
    version='0.0.1',
    packages=[
        'scripts',
    ],
    author='Eran Agmon',
    author_email='eagmon@stanford.edu',
    url='https://github.com/vivarium-collective/vivarium-scripts',
    license='MIT',
    entry_points={
        'console_scripts': [
            'scripts.access_db:access'
        ]
    },
    short_description='',  # TODO: Describe your project briefly.
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data={},
    include_package_data=True,
    install_requires=[
        'vivarium-core',
        # TODO: Add other dependencies.
    ],
)
