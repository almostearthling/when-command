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

DATA_FILES = """
LICENSE
README.md
share/when-command/when-command.py
share/doc/when-command/CHANGELOG.md
share/doc/when-command/ROADMAP.md
share/doc/when-command/TRANSLATE.md
share/doc/when-command/PACKAGE.md
share/doc/when-command/copyright
share/icons/hicolor/128x128/apps/when-command.png
share/icons/hicolor/256x256/apps/when-command.png
share/icons/hicolor/32x32/apps/when-command.png
share/icons/hicolor/64x64/apps/when-command.png
share/locale/es/LC_MESSAGES/when-command.mo
share/locale/it/LC_MESSAGES/when-command.mo
share/when-command/when-command-about.glade
share/when-command/when-command-edit-condition.glade
share/when-command/when-command-edit-dbus-signal.glade
share/when-command/when-command-edit-task.glade
share/when-command/when-command-settings.glade
share/when-command/when-command-task-history.glade
share/when-command/icons/alarmclock-128.png
share/when-command/icons/alarmclock.png
share/when-command/icons/color/alarm-add.png
share/when-command/icons/color/alarm-off.png
share/when-command/icons/color/alarm.png
share/when-command/icons/color/warning.png
share/when-command/icons/dark/alarm-add.png
share/when-command/icons/dark/alarm-off.png
share/when-command/icons/dark/alarm.png
share/when-command/icons/dark/warning.png
share/when-command/icons/emblems/failure.png
share/when-command/icons/emblems/success.png
share/when-command/icons/light/alarm-add.png
share/when-command/icons/light/alarm-off.png
share/when-command/icons/light/alarm.png
share/when-command/icons/light/warning.png
""".strip().split("\n")

DATA_DIC = {}
DATA_TUPLES = []
for x in DATA_FILES:
    dirname = os.path.dirname(x)
    basename = os.path.basename(x)
    if dirname not in DATA_DIC:
        DATA_DIC[dirname] = []
    DATA_DIC[dirname].append(basename)
for key in DATA_DIC:
    if key:
        DATA_TUPLES.append(
            (key, [os.path.join(key, s) for s in DATA_DIC[key]]))
DATA_TUPLES.append(('share/doc/when-command', ['LICENSE', 'README.md']))

# try to keep identifiers as single-sourced as possible
HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'share/when-command/when-command.py')) as f:
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


# this and the MANIFEST.in file should be enough for a suitable sdist
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
    platforms=['Linux'],
    include_package_data=True,

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

    # package_data={'': DATA_FILES},
    data_files=DATA_TUPLES,
    scripts=[
        'when-command',
    ],
)


# end.
