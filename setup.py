#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# When (setup script)
#
# Copyright (c) 2015 Francesco Garosi
# Released under the BSD License (see LICENSE.md)
#
# This script is used to install When in a Debian-compatible way.
#

import os
import os.path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open


# try to keep identifiers as single-sourced as possible
HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'when-command.py')) as f:
    for line in f:
        words = line.strip().split()
        if words:
            if words[0] == 'APPLET_VERSION':
                exec(line)
            elif words[0] == 'APPLET_NAME':
                exec(line)
            elif words[0] == 'APPLET_FULLNAME':
                exec(line)
            elif words[0] == 'APPLET_SHORTNAME':
                exec(line)
            elif words[0] == 'APPLET_COPYRIGHT':
                exec(line)
            elif words[0] == 'APPLET_URL':
                exec(line)
            elif words[0] == 'APPLET_LONGDESC':
                exec(line)


setup(
    name=APPLET_NAME,
    version=APPLET_VERSION,
    description=APPLET_FULLNAME,
    long_description=APPLET_LONGDESC,
    url=APPLET_URL,
    download_url='https://github.com/almostearthling/when-command',
    author='Francesco Garosi',
    author_email='franz.g@no-spam-please.infinito.it',
    license='BSD',
    platform='linux',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],

    classifiers=[
        ('Development Status :: 4 - Beta'
         if '-beta.' in APPLET_VERSION or '.b' in APPLET_VERSION
         else 'Development Status :: 5 - Production/Stable'),
        'Environment :: X11 Applications :: Gnome',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.4',
        'Topic :: Desktop Environment :: Gnome',
        'Topic :: Utilities',
    ],
    keywords='applet desktop gnome task-scheduler ubuntu unity',

    entry_points={
        # 'gui_scripts': 'when-command=when-command:main',
        'console_scripts': 'when-command=when-command:main',
    },

)


# end.
