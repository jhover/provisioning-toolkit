#!/usr/bin/env python
#
# Setup prog for Certify certificate management utility

import sys
from distutils.core import setup

setup(
    name="provisioning-toolkit",
    version='0.9.0',
    description='Utilities for automating VM management.',
    long_description='''Utilities for automating VM management.''',
    license='GPL',
    author='John Hover',
    author_email='jhover@bnl.gov',
    url='https://www.racf.bnl.gov/experiments/usatlas/griddev/',
    packages=[ 'provisioning',
              ],
    classifiers=[
          'Development Status :: 3 - Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GPL',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: System Administration :: Management',
    ],
    data_files=[ ('share/provisioning', ['README.txt', 'LGPL.txt', ] ) ],
)

