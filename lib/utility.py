# various utility functions and objects

import sys
import os
import subprocess
from base64 import b64decode

from tomlkit import table
from hashlib import blake2s
from base64 import decodebytes as b64_decodeb
from io import BytesIO
from PIL import Image, ImageTk
from time import time

import tkinter as tk
import ttkbootstrap as ttk

import darkdetect

from .i18n.strings import *
from .repocfg import AppConfig


# check that all passed arguments are not None
def check_not_none(*l) -> bool:
    for x in l:
        if x is None:
            return False
    return True


# append an item to a TOML table if it is not none
def append_not_none(table: table, key: str, value) -> table:
    if value is not None:
        table.append(key, value)
    return table


# try to guess the type of a string from the text that it contains
def guess_typed_value(s: str):
    t = s.lower()
    if t in ('true', 'false'):
        return t == 'true'
    else:
        try:
            return int(t)
        except ValueError:
            try:
                return float(t)
            except ValueError:
                return s
        finally:
            return s


# find an unique-ish name for an item
def generate_item_name(o=None):
    if o is None:
        base = "Item"
    else:
        base = o.__class__.__name__
    d = blake2s(digest_size=5)
    d.update(str(time()).encode('utf-8'))
    return "%s_%s" % (base, d.hexdigest().upper())


# get an image from a stored icon
def get_image(data: bytes):
    bio = BytesIO(b64_decodeb(data))
    bio.seek(0)
    return Image.open(bio)


# get an UI suitable image
def get_ui_image(data: bytes):
    return ImageTk.PhotoImage(get_image(data))


# convert an image in string format to a resized tkinter-compatible PhotoImage:
# this must be used **after** a Tk root has been created
def get_icon(image: bytes):
    return ImageTk.PhotoImage(
        Image.open(BytesIO(b64decode(image))).resize((24, 24)))

def get_appicon(image: bytes):
    return ImageTk.PhotoImage(
        Image.open(BytesIO(b64decode(image))).resize((32, 32)))


# determine where configuration is stored by default
def get_default_configdir():
    if sys.platform == 'win32':
        appdata = os.environ['APPDATA']
        cfgname = AppConfig.get('CFGNAME')
        if AppConfig.get('DEBUG'):
            cfgname += "_DEBUG"
        return os.path.join(appdata, cfgname)
    else:
        cfgname = "." + AppConfig.get('CFGNAME').lower()
        if AppConfig.get('DEBUG'):
            cfgname += "_DEBUG"
        home = os.path.expanduser("~")
        if sys.platform == 'darwin':
            return os.path.join(home, "Library", "Application Support", cfgname)
        elif sys.platform == 'linux':
            return os.path.join(home, cfgname)
        else:
            raise OSError("Unsupported platform: %s" % sys.platform)


# determine scripts directory and ensure that it exists
def get_scriptsdir():
    configdir = AppConfig.get('APPDATA')
    if sys.platform == 'win32':
        subdir = "Scripts"
    else:
        subdir = "scripts"
    scriptdir = os.path.join(configdir, subdir)
    if not os.path.isdir(scriptdir):
        try:
            os.makedirs(scriptdir)
        except Exception as e:
            return None
    return scriptdir


# save a script to the scripts directory and make it executable: possible
# existing files are overwritten without confirmation as the scripts folder
# should be completely managed by When
def save_script(fname, text):
    dest = os.path.join(get_scriptsdir(), fname)
    with open(dest, 'w') as f:
        f.write(text)
    if sys.platform != 'win32':
        os.chmod(dest, 0o700)


# return the output of `whenever --version`
def get_whenever_version():
    whenever_path = AppConfig.get('WHENEVER')
    result = subprocess.run(
        [whenever_path, '--version'],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        universal_newlines = True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    if result:
        return result.stdout.strip()
    else:
        return None


# check whether the scheduler is running
def is_whenever_running():
    whenever_path = AppConfig.get('WHENEVER')
    result = subprocess.run(
        [whenever_path, '--check-running', '--quiet'],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        universal_newlines = True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    if result:
        if result.returncode == 0:
            return True
        else:
            return False
    else:
        return None


# return the configuration file path
def get_configfile():
    basename = "%s.toml" % AppConfig.get('CFGNAME').lower()
    return os.path.join(AppConfig.get('APPDATA'), basename)

# return the log file path
def get_logfile():
    basename = "%s.log" % AppConfig.get('CFGNAME').lower()
    return os.path.join(AppConfig.get('APPDATA'), basename)


# get the GUI theme according to system theme or DEBUG mode
def get_UI_theme():
    if AppConfig.get('DEBUG'):
        return AppConfig.get('DEFAULT_THEME_DEBUG')
    else:
        if darkdetect.isDark():
            return AppConfig.get('DEFAULT_THEME_DARK')
        else:
            return AppConfig.get('DEFAULT_THEME_LIGHT')

# get the editor theme according to system theme or DEBUG mode
def get_editor_theme():
    if AppConfig.get('DEBUG'):
        return AppConfig.get('EDITOR_THEME_DEBUG')
    else:
        if darkdetect.isDark():
            return AppConfig.get('EDITOR_THEME_DARK')
        else:
            return AppConfig.get('EDITOR_THEME_LIGHT')


# write a warning to stderr
def write_warning(s):
    sys.stderr.write("%s warning: %s" % (UI_APP, s))

# write an error to stderr
def write_error(s):
    sys.stderr.write("%s error: %s" % (UI_APP, s))


# get extensions of executable files on Windows
def get_executable_extensions():
    if sys.platform.startswith('win'):
        return os.environ['PATHEXT'].split(';')
    else:
        return None


# ...


# end.
