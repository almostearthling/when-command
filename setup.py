#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# When (setup script)
#
# Copyright (c) 2015 Francesco Garosi
# Released under the BSD License (see LICENSE file)
#
# This script is used to install When in a Debian-compatible way.


import os
import os.path
import glob

# always prefer setuptools over distutils
from setuptools import setup

# build a complete list of package files
LOCALE_FILES = glob.glob('share/locale/*/LC_MESSAGES/when-command.mo')
DTICON_FILES = glob.glob('share/icons/hicolor/*/apps/when-command.png')
DATA_FILES = """
README.md
share/when-command/when-command.py
share/man/man1/when-command.1
share/doc/when-command/copyright
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
""".strip().split("\n") + LOCALE_FILES + DTICON_FILES

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
DATA_TUPLES.append(('share/doc/when-command', ['README.md']))

# try to keep identifiers as single-sourced as possible
HERE = os.path.abspath(os.path.dirname(__file__))
METADATA = """
    APPLET_VERSION
    APPLET_NAME
    APPLET_FULLNAME
    APPLET_SHORTNAME
    APPLET_COPYRIGHT
    APPLET_URL
    APPLET_LONGDESC
""".strip().split()
with open(os.path.join(HERE, 'share/when-command/when-command.py')) as f:
    for line in f:
        words = line.strip().split()
        if words and words[0] in METADATA:
            exec(line)


# extract packaging author metadata from environment if present, so that it
# becomes easier to correctly sign the source packages
AUTHOR = (os.environ['DEBFULLNAME'] if 'DEBFULLNAME' in os.environ
          else "Francesco Garosi (AlmostEarthling)")
AUTHOR_EMAIL = (os.environ['DEBEMAIL'] if 'DEBEMAIL' in os.environ
                else "franz.g@no-spam-please.infinito.it")


# this and the MANIFEST.in file should be enough for a suitable sdist
setup(
    name=APPLET_NAME,
    version=APPLET_VERSION,
    description=APPLET_FULLNAME,
    long_description=APPLET_LONGDESC,
    url=APPLET_URL,
    download_url='https://github.com/almostearthling/when-command',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license='BSD',
    platforms=['Linux'],
    include_package_data=True,

    classifiers=[
        ('Development Status :: 4 - Beta'
         if 'beta.' in APPLET_VERSION or '.b' in APPLET_VERSION
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

    data_files=DATA_TUPLES,
    scripts=[
        'scripts/when-command',
    ],
)


# end.
