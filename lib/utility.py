# various utility functions and objects

import sys
import os
import subprocess

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
from .icons import APP_ICON32 as APP_ICON

from .repocfg import AppConfig


# main root window, to be withdrawn
_root = None


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


# return the output of `whenever --version`
def get_whenever_version():
    whenever_path = AppConfig.get('WHENEVER')
    result = subprocess.run(
        [whenever_path, '--version'],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        universal_newlines = True,
        text=True,
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



# create an invisible toplevel, so that none of the following is main/root
def setup_windows():
    global _root
    _root = tk.Tk()
    _root.withdraw()
    style = ttk.Style()
    style.theme_use(get_UI_theme())


# cleanup the root window: only to be called at exit
def cleanup_windows():
    global _root
    _root.destroy()
    del _root

# write a warning to stderr
def write_warning(s):
    sys.stderr.write("%s warning: %s" % (UI_APP, s))

# write an error to stderr
def write_error(s):
    sys.stderr.write("%s error: %s" % (UI_APP, s))


# ...


# end.
