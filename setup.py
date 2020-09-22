import os
import glob
import setuptools
from distutils.core import setup

with open("README.md", 'r') as readme:
    long_description = readme.read()

setup(
    name='vivarium-scripts',
    version='0.0.2',
    packages=[
        'scripts',
    ],
    author='Eran Agmon',
    author_email='eagmon@stanford.edu',
    url='https://github.com/vivarium-collective/vivarium-scripts',
    license='MIT',
    entry_points={
        'console_scripts': [
            'access_db=scripts.access_db:access'
        ]
    },
    short_description='miscellaneous scripts for vivarium projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data={},
    include_package_data=True,
    install_requires=[
        # 'vivarium-core',
    ],
)
