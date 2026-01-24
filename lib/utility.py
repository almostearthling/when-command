# various utility functions and objects

import sys
import os
import shutil
import subprocess
from base64 import b64decode
import re

from PIL.ImageFile import ImageFile
from tomlkit import (
    inline_table,
    array,
    string,
    items,
    exceptions,
    )
from hashlib import blake2s
from base64 import decodebytes as b64_decodeb
from io import BytesIO
from PIL import Image, ImageTk
from time import time

import tkinter as tk

from rich.console import Console

import darkdetect
from semver import Version

from .i18n.strings import *
from .repocfg import AppConfig
from .runner.logger import Logger
from .platform import is_windows, is_linux, is_mac


# lowest whenever version supported
_MIN_WHENEVER_SUPPORTED = Version.parse("0.4.7")


# a regular expression to check whether an user-given name is valid
_RE_VALID_ITEM_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


# private item name prefix
_PRIVATE_ITEM_PREFIX = "__When__private__"


# Lua initialization script
_LUA_INIT_SCRIPT = """\
-- lua initialization script
package.path = LUA_PATH
"""
_LUA_INIT_NAME = "init.lua"


# WARNING: this is hard to support, at least on Windows: phase out for now
# # luarocks initialization script: the unusual brackets and their replacement
# # are there in order to allow for a further application of str.format(...)
# _LUAROCKS_INIT_SCRIPT_TEMPL = """\
# -- luarocks initialization script
# rocks_trees = [
#     root = "{base}",
#     bin_dir = "{base}{sep}bin",
#     lib_dir = "{base}{sep}lib",
#     lua_dir = "{base}{sep}lua",
# ]
# """.format(sep=os.path.sep, base="{base}").replace("[", "{{").replace("]", "}}")
# _LUAROCKS_INIT_NAME = "rocks.lua"


# the common Tk root
_tkroot = tk.Tk()

# consoles for stdio and stderr
_console = Console(force_terminal=True)
_err_console = Console(force_terminal=True, stderr=True)

# the common logger
_logger = None

# the current whenever version
_current_whenever_version = None

# operators allowed in WMI and DBus result/parameter checks
_WMI_RESULT_CHECK_OPERATORS = ("eq", "neq", "gt", "ge", "lt", "le", "match")
_DBUS_PARAM_CHECK_OPERATORS = ("eq", "neq", "gt", "ge", "lt", "le", "match", "contains", "ncontains")


# check that an operator is correct for either DBus or WMI result checks
def is_wmi_operator(s: str) -> bool:
    return s in _WMI_RESULT_CHECK_OPERATORS

def is_dbus_operator(s: str) -> bool:
    return s in _DBUS_PARAM_CHECK_OPERATORS


# return the current Tk root: create one if not already present
def get_tkroot() -> tk.Tk:
    return _tkroot


# return the terminal console handled by the "rich" module
def get_rich_console() -> Console:
    return _console


# return the current logger
def get_logger() -> Logger:
    assert _logger is not None
    return _logger


# return the prefix for private item names
def get_private_item_name_prefix() -> str:
    return _PRIVATE_ITEM_PREFIX


# check whether a name indicates that an item is private
def is_private_item_name(s: str) -> bool:
    return s.startswith(_PRIVATE_ITEM_PREFIX)


# check whether an user-provided name is valid
def is_valid_item_name(s: str) -> bool:
    return bool(_RE_VALID_ITEM_NAME.match(s)) and not is_private_item_name(s)


# check that all passed arguments are not None
def check_not_none(*l) -> bool:
    for x in l:
        if x is None:
            return False
    return True


# append an item to a TOML table if it is not none
def append_not_none(table: items.Table, key: str, value) -> items.Table:
    if value is not None:
        table.append(key, value)
    return table


# try to guess the type of a string from the text that it contains
def guess_typed_value(s: str) -> bool | int | float | str:
    t = s.lower()
    if t in ("true", "false"):
        return t == "true"
    else:
        try:
            return int(t)
        except ValueError:
            try:
                return float(t)
            except ValueError:
                return s


# find an unique-ish name for an item
def generate_item_name(o=None) -> str:
    if o is None:
        base = "Item"
    else:
        base = o.__class__.__name__
    d = blake2s(digest_size=5)
    d.update(str(time()).encode("utf-8"))
    return "%s_%s" % (base, d.hexdigest().upper())


# get an image from a stored icon
def get_image(data: bytes) -> ImageFile:
    bio = BytesIO(b64_decodeb(data))
    bio.seek(0)
    return Image.open(bio)


# get an UI suitable image
def get_ui_image(data: bytes) -> ImageTk.PhotoImage:
    return ImageTk.PhotoImage(get_image(data))


# convert an image in string format to a resized tkinter-compatible PhotoImage:
# this must be used **after** a Tk root has been created
def get_icon(image: bytes) -> ImageTk.PhotoImage:
    return ImageTk.PhotoImage(Image.open(BytesIO(b64decode(image))).resize((24, 24)))


def get_appicon(image: bytes) -> ImageTk.PhotoImage:
    return ImageTk.PhotoImage(Image.open(BytesIO(b64decode(image))).resize((32, 32)))


# determine where configuration is stored by default
def get_default_configdir() -> str:
    if is_windows():
        appdata = os.environ["APPDATA"]
        cfgname: str = AppConfig.get("CFGNAME") # type: ignore
        if AppConfig.get("DEBUG"):
            cfgname += "_DEBUG"
        return os.path.join(appdata, cfgname)
    else:
        s: str = AppConfig.get("CFGNAME")   # type: ignore
        cfgname = "." + s.lower()
        if AppConfig.get("DEBUG"):
            cfgname += "_DEBUG"
        home = os.path.expanduser("~")
        if sys.platform == "darwin":
            return os.path.join(home, "Library", "Application Support", cfgname)
        elif is_linux():
            return os.path.join(home, cfgname)
        else:
            raise OSError("Unsupported platform: %s" % sys.platform)


# find the default whenever executable (might not be in PATH)
def get_default_whenever() -> str | None:
    default_whenever = shutil.which("whenever")
    if default_whenever is None:
        if is_windows():
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
def get_appdata() -> str:
    appdata: str = AppConfig.get("APPDATA") # type: ignore
    if not os.path.isdir(appdata):
        try:
            os.makedirs(appdata)
        except Exception:
            raise OSError(CLI_ERR_DATADIR_UNACCESSIBLE)
    return appdata


# determine scripts directory and ensure that it exists
def get_scriptsdir() -> str:
    configdir: str = AppConfig.get("APPDATA") # type: ignore
    if is_windows():
        subdir = "Scripts"
    else:
        subdir = "scripts"
    scriptdir = os.path.join(configdir, subdir)
    if not os.path.isdir(scriptdir):
        try:
            os.makedirs(scriptdir)
        except Exception:
            raise OSError(CLI_ERR_SPECIFICDIR_UNACCESSIBLE % scriptdir)
    return scriptdir


# determine lua library directory and ensure that it exists
def get_luadir() -> str:
    configdir: str = AppConfig.get("APPDATA") # type: ignore
    if is_windows():
        subdir = "Lua"
    else:
        subdir = "lua"
    luadir = os.path.join(configdir, subdir)
    if not os.path.isdir(luadir):
        try:
            os.makedirs(luadir)
        except Exception:
            raise OSError(CLI_ERR_SPECIFICDIR_UNACCESSIBLE % luadir)
    return luadir


# the following cannot be used, because the embedded Lua interpreter cannot
# load Lua binary modules due to its safe setup, which disallows it
# # determine binary lib extension depending on operating system
# def get_luabinlibext() -> str:
#     if is_windows():
#         return "dll"
#     else:
#         return "so"


# get the Lua initialization script file name, and ensure that it exists
def get_lua_initscript() -> str:
    init = os.path.join(get_scriptsdir(), _LUA_INIT_NAME)
    if not os.path.exists(init):
        with open(init, 'w') as f:
            f.write(_LUA_INIT_SCRIPT)
    return init


# save a script to the scripts directory and make it executable: possible
# existing files are overwritten without confirmation as the scripts folder
# should be completely managed by When
def save_script(fname, text) -> None:
    dest = os.path.join(get_scriptsdir(), fname)
    with open(dest, "w") as f:
        f.write(text)
    if not is_windows():
        os.chmod(dest, 0o700)


# return the output of `whenever --version`
def get_whenever_version() -> None | str:
    global _current_whenever_version
    whenever_path: str = AppConfig.get("WHENEVER")  # type: ignore
    if _current_whenever_version is None:
        try:
            result = subprocess.run(
                [whenever_path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                text=True,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
                ),
            )
            if result:
                _current_whenever_version = result.stdout.strip()
            else:
                _current_whenever_version = None
        except Exception:
            _current_whenever_version = None
    return _current_whenever_version


def check_whenever_version() -> bool:
    ver = get_whenever_version()
    if ver is None:
        return False
    else:
        return _MIN_WHENEVER_SUPPORTED <= Version.parse(ver.split()[1])


# return the output of `whenever --options`
def retrieve_whenever_options() -> None:
    whenever_path: str = AppConfig.get("WHENEVER")  # type: ignore
    try:
        result = subprocess.run(
            [whenever_path, "--options"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            text=True,
            creationflags=(
                subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
            ),
        )
    except Exception:
        # maybe no executable has been found?
        AppConfig.set("WHENEVER_HAS_DBUS", False)
        AppConfig.set("WHENEVER_HAS_WMI", False)
        # ...other options might appear
        return None
    if result:
        # output has the form: `options: [wmi] [dbus]`, each one might or
        # might not be present in the output, so we check whether the list
        # below contains or not one of them
        if result.returncode == 0:
            opts = result.stdout.strip().split()
            if "dbus" in opts:
                AppConfig.set("WHENEVER_HAS_DBUS", True)
            else:
                AppConfig.set("WHENEVER_HAS_DBUS", False)
            if sys.platform.startswith("win") and "wmi" in opts:
                AppConfig.set("WHENEVER_HAS_WMI", True)
            else:
                AppConfig.set("WHENEVER_HAS_WMI", False)
            # ...other options might appear
        else:
            # this might be an older version, assume DBus is available
            AppConfig.set("WHENEVER_HAS_DBUS", True)
            AppConfig.set("WHENEVER_HAS_WMI", False)
            # ...other options might appear
    else:
        # this might be an older version, assume DBus is available
        AppConfig.set("WHENEVER_HAS_DBUS", True)
        AppConfig.set("WHENEVER_HAS_WMI", False)
        # ...other options might appear


# check whether the scheduler is running
def is_whenever_running() -> None | bool:
    whenever_path: str = AppConfig.get("WHENEVER")  # type: ignore
    try:
        result = subprocess.run(
            [whenever_path, "--check-running", "--quiet"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
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
    except Exception:
        return False


# a couple of shortcuts for whenever options
def whenever_has_dbus() -> bool:
    res = bool(AppConfig.get("WHENEVER_HAS_DBUS"))
    return res


def whenever_has_wmi() -> bool:
    res = bool(AppConfig.get("WHENEVER_HAS_WMI"))
    return res


# return the configuration file path
def get_configfile() -> str:
    s: str = AppConfig.get("CFGNAME")   # type: ignore
    d: str = AppConfig.get("APPDATA")   # type: ignore
    basename = "%s.toml" % s.lower()
    return os.path.join(d, basename)


# return the log file path
def get_logfile() -> str:
    s: str = AppConfig.get("CFGNAME")   # type: ignore
    d: str = AppConfig.get("APPDATA")   # type: ignore
    basename = "%s.log" % s.lower()
    return os.path.join(d, basename)


# get the GUI theme according to system theme or DEBUG mode
def get_UI_theme():
    if AppConfig.get("DEBUG"):
        return AppConfig.get("DEFAULT_THEME_DEBUG")
    else:
        if darkdetect.isDark():
            return AppConfig.get("DEFAULT_THEME_DARK")
        else:
            return AppConfig.get("DEFAULT_THEME_LIGHT")


# get the editor theme according to system theme or DEBUG mode
def get_editor_theme():
    if AppConfig.get("DEBUG"):
        return AppConfig.get("EDITOR_THEME_DEBUG")
    else:
        if darkdetect.isDark():
            return AppConfig.get("EDITOR_THEME_DARK")
        else:
            return AppConfig.get("EDITOR_THEME_LIGHT")


# write a warning to stderr
def write_warning(s) -> None:
    _err_console.print(f"[bold yellow]{UI_APP} - warning:[/] {s}", highlight=False)


# write an error to stderr
def write_error(s) -> None:
    _err_console.print(f"[bold red]{UI_APP} - ERROR:[/] {s}", highlight=False)


# utility to bail out with a consistent error message
def exit_error(s, code=2, verbose=True):
    if verbose:
        write_error(s)
    sys.exit(code)


# get extensions of executable files on Windows
def get_executable_extensions() -> list[str] | None:
    if is_windows():
        return os.environ["PATHEXT"].split(";")
    else:
        return None


# TOML: try to render a string as literal
def toml_try_literal(s) -> items.String:
    try:
        return string(s, literal=True)
    except (exceptions.InvalidStringError, exceptions.InvalidCharInStringError):
        return string(s, literal=False)


# TOML: try to render a string as multiline literal
def toml_try_ml_literal(s) -> items.String:
    try:
        return string(s, multiline=True, literal=True)
    except (exceptions.InvalidStringError, exceptions.InvalidCharInStringError):
        return string(s, multiline=True, literal=False)


# TOML: create an array of inline tables from a list of dicts
def toml_list_of_tables(lot) -> items.Array | None:
    if lot is not None:
        r = array()
        for x in lot:
            elem = inline_table()
            elem.update(x)
            r.add_line(elem)
        if len(r) > 0:
            r.add_line()
        return r


# TOML: convert to a script (multiline literal) string
def toml_script_string(s) -> items.String | None:
    if s is not None:
        return toml_try_ml_literal(s)


# TOML: a list of items
def toml_list_of_items(loi) -> items.Array | None:
    if loi is not None:
        r = array()
        for x in loi:
            r.add_line(x)
        if len(r) > 0:
            r.add_line()
        return r


# TOML: create an array of literal strings
def toml_list_of_literals(los) -> items.Array | None:
    if los is not None:
        r = array()
        for s in los:
            r.add_line(toml_try_literal(s))
        if len(r) > 0:
            r.add_line()
        return r


# TOML: list of literals specific for command arguments: tries to put arguments
# beginning with a dash, a double dash, or a slash (on Windows) on a new line
# in the array, possibly followed by the first non-dashed argument
def toml_list_of_command_args(los) -> items.Array | None:
    if los is not None:
        switch_start = ['-', '--']
        if is_windows():
            switch_start.append('/')
        cur_line = []
        r = array()
        for s in los:
            if any(s.startswith(x) for x in switch_start):
                if len(cur_line) > 0:
                    r.add_line(*cur_line)
                    cur_line = []
                cur_line.append(toml_try_literal(s))
            elif len(cur_line) > 1:
                r.add_line(*cur_line)
                cur_line = []
                r.add_line(toml_try_literal(s))
            else:
                cur_line.append(toml_try_literal(s))
        if len(cur_line) > 0:
            r.add_line(*cur_line)
        if len(r) > 0:
            r.add_line()
        return r


# TOML: quickly convert a string to literal (preserving None)
def toml_literal(s) -> items.String | None:
    if s is not None:
        return toml_try_literal(s)



# clean a caption from non-alphanumeric characters at the end
def clean_caption(s) -> str:
    s = " ".join(s.split())
    alnum = "abcdefghijklmnopqrstuvwxyz0123456789"
    while len(s) > 0 and s[-1].lower() not in alnum:
        s = s[:-1]
    return s


# initialize the logger
def init_logger(filename, level, app=None) -> None:
    global _logger
    _logger = Logger(filename, level, app)


# ...


# end.
