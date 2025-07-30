# install_lua.py
#
# install a Lua library (as a script or a binary) in APPDATA/Lua

import sys
import os
import shutil
import platform
from zipfile import ZipFile

from ..i18n.strings import *
from ..utility import write_error, get_rich_console, get_luabinlibext, get_luadir

LUA_EXT = ".lua"
LUA_BINEXT = get_luabinlibext()
LUA_ZIPEXT = ".zip"


def install_lua(fname: str) -> bool:
    dest_base = get_luadir()
    if fname.endswith(LUA_EXT):
        if not os.path.isfile(fname):
            return False
        try:
            shutil.copy(fname, dest_base)
        except Exception as e:
            return False
        return True
    elif fname.endswith(LUA_BINEXT):
        if not os.path.isfile(fname):
            return False
        try:
            shutil.copy(fname, dest_base)
        except Exception as e:
            return False
        return True
    elif fname.endswith(LUA_ZIPEXT):
        if not os.path.isfile(fname):
            return False
        zip = ZipFile(fname)
        try:
            dest_dir = os.path.join(
                dest_base, os.path.basename(fname[: -len(LUA_ZIPEXT)])
            )
            os.mkdir(dest_dir)
            zip.extractall(dest_dir)
        except Exception as e:
            return False
        return True
    return False


__all__ = [
    "install_lua",
]


# end.
