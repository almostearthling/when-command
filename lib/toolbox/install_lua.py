# install_lua.py
#
# install a Lua library (as a script or a binary) in APPDATA/Lua: for now a
# very simple version is provided, that only installs a Lua file, a shared
# library, or extracts a ZIP file in the above mentioned folder; in the future
# more useful cases could be handled, in case a suitable package manager can
# be found

import os
import shutil
from zipfile import ZipFile, BadZipFile, LargeZipFile

from ..i18n.strings import *
from ..utility import write_error, get_rich_console, get_luadir


# at the moment only these cases are handled
LUA_EXT = ".lua"
LUA_ZIPEXT = ".zip"


# the following is a list of modules used by When, that cannot be upgraded
RESERVED = [
    "_.lua",  # placeholder for files
    "_",  # placeholder for directories
]


# the actual installation utility, there is no uninstall utility for the
# moment; this will install simple scripts or unpack ZIP files: it may happen
# that a ZIP file contains a binary module, but the Lua interpreter provided
# by whenever will just refuse to load it due to safety problems
def install_lua(fname: str, verbose: bool = True) -> bool:
    dest_base = get_luadir()
    console = get_rich_console()
    fname_base = os.path.basename(fname)
    # single Lua files are installed directly in the main folder: if the
    # module already exists, installation is skipped and an error is shown
    if fname.endswith(LUA_EXT):
        # fail if the origin is not accessible
        if not os.path.isfile(fname):
            if verbose:
                write_error(CLI_ERR_FILE_NOT_FOUND % fname)
            return False
        if fname_base in RESERVED:
            if verbose:
                write_error(CLI_ERR_NOT_PERMITTED)
            return False
        dest_file = os.path.join(dest_base, fname_base)
        # fail if the destination is already present
        if os.path.exists(dest_file):
            if verbose:
                write_error(CLI_ERR_FILE_EXISTS % dest_file)
            return False
        try:
            console.print(CLI_MSG_INSTALL_TO_FOLDER % (fname_base, dest_base))
            shutil.copy(fname, dest_base)
        # fail on operation native failure
        except shutil.Error:
            if verbose:
                dest_file = os.path.join(dest_base, fname_base)
                write_error(CLI_ERR_CANNOT_CREATE_FILE % dest_file)
            return False
        # in this case show the exception text, may be useful for debugging
        except Exception as e:
            if verbose:
                write_error(CLI_ERR_UNEXPECTED_EXCEPTION % e)
            return False
        return True
    # the tests differ a little, because the destination here is a directory
    # that has the same base name as the ZIP archive: in this case too, the
    # installation tool will fail when the library exists, that is, a directory
    # with the expected name is already there
    elif fname.endswith(LUA_ZIPEXT):
        # fail if the origin is not accessible
        if not os.path.isfile(fname):
            if verbose:
                write_error(CLI_ERR_FILE_NOT_FOUND % fname)
            return False
        dest_dir_base = os.path.basename(fname[: -len(LUA_ZIPEXT)])
        dest_dir = os.path.join(dest_base, dest_dir_base)
        # fail if the destination is already present
        if os.path.exists(dest_dir):
            if verbose:
                write_error(CLI_ERR_DIR_EXISTS % dest_dir)
            return False
        if dest_dir_base in RESERVED:
            if verbose:
                write_error(CLI_ERR_NOT_PERMITTED)
            return False
        console.print(CLI_MSG_INSTALL_TO_FOLDER % (fname_base, dest_dir))
        try:
            with ZipFile(fname) as zip:
                nl = zip.namelist()
                # handle the special case of a zipped directory: this will
                # probably be the most common case for ZIP files
                singledir = True
                zipdir = dest_dir_base + "/"
                for x in nl:
                    if not x.startswith(zipdir):
                        singledir = False
                        break
                if singledir:
                    zip.extractall(dest_base)
                else:
                    os.mkdir(dest_dir)
                    zip.extractall(dest_dir)
        # fail on operation native failure
        except OSError:
            if verbose:
                write_error(CLI_ERR_CANNOT_CREATE_DIR % dest_dir)
            return False
        # fail on ZIP extraction failure
        except (ValueError, RuntimeError, BadZipFile, LargeZipFile):
            if verbose:
                write_error(CLI_ERR_CANNOT_EXTRACT_ARCHIVE % fname)
            return False
        # in this case show the exception text, may be useful for debugging
        except Exception as e:
            if verbose:
                write_error(CLI_ERR_UNEXPECTED_EXCEPTION % e)
            return False
        return True
    # only support: .lua, .so/.dll, .zip; anything else is rejected
    else:
        if verbose:
            write_error(CLI_ERR_UNSUPPORTED_FILETYPE)
        return False


# the upgrade utility: it removes an existing installation and invokes the
# installation utility to reinstall the specified extension
def upgrade_lua(fname: str, verbose: bool = True) -> bool:
    dest_base = get_luadir()
    fname_base = os.path.basename(fname)
    if fname.endswith(LUA_EXT):
        dest_file = os.path.join(dest_base, fname_base)
        if not os.path.exists(dest_file):
            if verbose:
                write_error(CLI_ERR_FILE_NOT_FOUND % fname)
            return False
        dest = dest_file
        if fname_base in RESERVED:
            if verbose:
                write_error(CLI_ERR_NOT_PERMITTED)
            return False
    elif fname.endswith(LUA_ZIPEXT):
        dest_dir_base = os.path.basename(fname[: -len(LUA_ZIPEXT)])
        dest_dir = os.path.join(dest_base, dest_dir_base)
        if not os.path.exists(dest_dir):
            if verbose:
                write_error(CLI_ERR_DIR_NOT_FOUND % dest_dir)
            return False
        if dest_dir_base in RESERVED:
            if verbose:
                write_error(CLI_ERR_NOT_PERMITTED)
            return False
        dest = dest_dir
    else:
        if verbose:
            write_error(CLI_ERR_UNSUPPORTED_FILETYPE)
        return False
    try:
        shutil.rmtree(dest)
    except Exception:
        if verbose:
            write_error(CLI_ERR_ERROR_GENERIC)
        return False
    # call the installation utility
    return install_lua(fname, verbose)


# add a name to the list of reserved files and directories: this is used
# internally upon initialization of services by When itself, so we assume
# that the name is correct
def reserve_lua(fname: str):
    if fname not in RESERVED:
        RESERVED.append(fname)


__all__ = [
    "install_lua",
    "upgrade_lua",
    "reserve_lua",
]


# end.
