# various utility functions and objects

# import all other modules
import sys
import os
import subprocess

from tomlkit.items import Table
from hashlib import blake2s
from base64 import decodebytes as b64_decodeb
from io import BytesIO
from PIL import Image
from time import time

import darkdetect

from lib.repocfg import AppConfig

from lib.sgmod import sg


# check that all passed arguments are not None
def check_not_none(*l) -> bool:
    for x in l:
        if x is None:
            return False
    return True


# append an item to a TOML table if it is not none
def append_not_none(table: Table, key: str, value) -> Table:
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


# return the configuration file path
def get_configfile():
    basename = "%s.toml" % AppConfig.get('CFGNAME').lower()
    return os.path.join(AppConfig.get('APPDATA'), basename)

# return the log file path
def get_logfile():
    basename = "%s.log" % AppConfig.get('CFGNAME').lower()
    return os.path.join(AppConfig.get('APPDATA'), basename)


# set the GUI theme according to system theme or DEBUG mode
def set_UI_theme(new_theme=None):
    if not new_theme:
        if AppConfig.get('DEBUG'):
            sg.theme(sg.DEFAULT_THEME_DEBUG)
        else:
            if darkdetect.isDark():
                sg.theme(sg.DEFAULT_THEME_DARK)
            else:
                sg.theme(sg.DEFAULT_THEME_LIGHT)
    else:
        sg.theme(new_theme)


# ...


# end.
