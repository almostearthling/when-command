# various utility functions and objects

import sys
import os
import shutil
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

from rich.console import Console

import darkdetect

from .i18n.strings import *
from .repocfg import AppConfig


# the common Tk root
_tkroot = tk.Tk()
_console = Console(force_terminal=True)
_err_console = Console(force_terminal=True, stderr=True)


# return the current Tk root: create one if not already present
def get_tkroot():
    return _tkroot


# return the terminal console handled by the "rich" module
def get_rich_console():
    return _console



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
    if sys.platform.startswith("win"):
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


# find the default whenever executable (might not be in PATH)
def get_default_whenever():
    default_whenever = shutil.which('whenever')
    if default_whenever is None:
        if sys.platform.startswith("win"):
            execname = "whenever.exe"
        else:
            execname = "whenever"
        # try the `pipx` installation path
        p = os.path.expanduser(os.path.join("~", ".local", "bin"))
        execpath = os.path.join(p, execname)
        if os.path.isfile(execpath) and os.access(execpath, os.X_OK):
            return execpath
        else:
            return None
    else:
        return default_whenever



# determine appdata directory and ensure it exists
def get_appdata():
    appdata = AppConfig.get('APPDATA')
    if not os.path.isdir(appdata):
        try:
            os.makedirs(appdata)
        except Exception as e:
            raise OSError(CLI_ERR_DATADIR_UNACCESSIBLE)
    return appdata


# determine scripts directory and ensure that it exists
def get_scriptsdir():
    configdir = AppConfig.get('APPDATA')
    if sys.platform.startswith("win"):
        subdir = "Scripts"
    else:
        subdir = "scripts"
    scriptdir = os.path.join(configdir, subdir)
    if not os.path.isdir(scriptdir):
        try:
            os.makedirs(scriptdir)
        except Exception as e:
            raise OSError(CLI_ERR_SCRIPTSDIR_UNACCESSIBLE)
    return scriptdir


# save a script to the scripts directory and make it executable: possible
# existing files are overwritten without confirmation as the scripts folder
# should be completely managed by When
def save_script(fname, text):
    dest = os.path.join(get_scriptsdir(), fname)
    with open(dest, 'w') as f:
        f.write(text)
    if not sys.platform.startswith("win"):
        os.chmod(dest, 0o700)


# return the output of `whenever --version`
def get_whenever_version():
    whenever_path = AppConfig.get('WHENEVER')
    try:
        result = subprocess.run(
            [whenever_path, '--version'],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            universal_newlines = True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0,
        )
    except Exception:
        return None
    if result:
        return result.stdout.strip()
    else:
        return None


# return the output of `whenever --version`
def retrieve_whenever_options():
    whenever_path = AppConfig.get('WHENEVER')
    try:
        result = subprocess.run(
            [whenever_path, '--options'],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            universal_newlines = True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0,
        )
    except Exception:
        # maybe no executable has been found?
        AppConfig.set('WHENEVER_HAS_DBUS', False)
        AppConfig.set('WHENEVER_HAS_WMI', False)
        # ...other options might appear
        return None
    if result:
        # output has the form: `options: [wmi] [dbus]`, each one might or
        # might not be present in the output, so we check whether the list
        # below contains or not one of them
        if result.returncode == 0:
            opts = result.stdout.strip().split()
            if "dbus" in opts:
                AppConfig.set('WHENEVER_HAS_DBUS', True)
            else:
                AppConfig.set('WHENEVER_HAS_DBUS', False)
            if sys.platform.startswith("win") and "wmi" in opts:
                AppConfig.set('WHENEVER_HAS_WMI', True)
            else:
                AppConfig.set('WHENEVER_HAS_WMI', False)
            # ...other options might appear
        else:
            # this might be an older version, assume DBus is available
            AppConfig.set('WHENEVER_HAS_DBUS', True)
            AppConfig.set('WHENEVER_HAS_WMI', False)
            # ...other options might appear
    else:
        # this might be an older version, assume DBus is available
        AppConfig.set('WHENEVER_HAS_DBUS', True)
        AppConfig.set('WHENEVER_HAS_WMI', False)
        # ...other options might appear


# check whether the scheduler is running
def is_whenever_running():
    whenever_path = AppConfig.get('WHENEVER')
    try:
        result = subprocess.run(
            [whenever_path, '--check-running', '--quiet'],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            universal_newlines = True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except Exception:
        return False
    if result:
        if result.returncode == 0:
            return True
        else:
            return False
    else:
        return None


# a couple of shortcuts for whenever options
def whenever_has_dbus():
    res = AppConfig.get('WHENEVER_HAS_DBUS')
    return res

def whenever_has_wmi():
    res = AppConfig.get('WHENEVER_HAS_WMI')
    return res


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
    _err_console.print(f"[bold yellow]{UI_APP} - warning:[/] {s}", highlight=False)

# write an error to stderr
def write_error(s):
    _err_console.print(f"[bold red]{UI_APP} - ERROR:[/] {s}", highlight=False)

# utility to bail out with a consistent error message
def exit_error(s, code=2):
    write_error(s)
    sys.exit(code)


# get extensions of executable files on Windows
def get_executable_extensions():
    if sys.platform.startswith("win"):
        return os.environ['PATHEXT'].split(';')
    else:
        return None


# ...


# end.
