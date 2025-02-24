# install_whenever.py
#
# download whenever's latest release from GitHub, verify its SHA1 sum and, if
# its version is greater than the one currently installed in ~/.local/bin, then
# install it in its place. Of course this can only happen if it's not already
# running.


import sys
import platform
import os.path
import re
import hashlib
from zipfile import ZipFile



# URL definition strings
REPO_WHENEVER = "whenever"
REPO_WHEN = "when-command"
CHECKSUM_FILE = "CHECKSUM.txt"

from ..i18n.strings import *
from ..utility import write_error, get_rich_console

from .dlutils import *



# installation path
def get_install_path():
    p = os.path.expanduser(os.path.join("~", ".local", "bin"))
    if os.path.exists(p):
        return p
    else:
        return None


# specific release file names
def get_whenever_release_pattern(verbose=False):
    if sys.platform == "win32":
        osname = "windows"
    elif sys.platform == "linux":
        osname = "linux"
    else:
        if verbose:
            write_error(f"platform not supported: {sys.platform}")
        return None
    arch = platform.uname().machine
    if arch == "AMD64":
        archstr = "x86_64"
    # elif arch == "XXXXX":
    #     archstr = "yyyyyy"
    else:
        if verbose:
            write_error(f"architecture not supported: {arch}")
        return None
    pattern = f"^whenever\\-([0-9][.0-9]+)\\+whenever_tray\\-[0-9][.0-9]+_{osname}\\-{archstr}\\.zip$"
    return pattern


# returns a tuple containing:
# - the download file name
# - the version number as a string
# - the checksum of the zip file to be downloaded
# or None if the checksum file could not be retrieved: only works with
# releases equal or above '0.2.8' (the first to sport a checksum file)
def get_whenever_download_metadata(verbose=False):
    releases_whenever = get_repo_latest_releases(REPO_WHENEVER)
    console = get_rich_console()
    checksums_url = f"{releases_whenever}/{CHECKSUM_FILE}"
    if verbose:
        console.print(CLI_MSG_DOWNLOADING_ASSET % CHECKSUM_FILE, highlight=False)
    checksums = retrieve_text_asset(checksums_url, verbose)
    pattern_matcher = re.compile(get_whenever_release_pattern(verbose))
    if checksums is None:
        if verbose:
            write_error(CLI_ERR_DOWNLOADING_ASSET % CHECKSUM_FILE)
        return None
    try:
        for line in checksums.split("\n"):
            line = line.strip()
            if not line:
                continue
            sha1_csum, dfname = line.split()
            if dfname.startswith("*"):
                dfname = dfname[1:]
            m = pattern_matcher.match(dfname)
            if m is not None:
                version = m.group(1)
                return (dfname, version, sha1_csum.lower())
        # if we are here no suitable version was found
        if verbose:
            write_error(CLI_ERR_NO_SUITABLE_BINARY)
        return None
    except ValueError as e:     # too many values to unpack
        if verbose:
            write_error(f"malformed `{CHECKSUM_FILE}` file")
        return None


# download a suitable release to the local workstation, check its checksum,
# and keep it if the checksum matches the one found in CHECKSUMS.txt: in this
# case return the full path to the archive, otherwise remove the archive and
# return None
def download_and_check_whenever(verbose=False):
    releases_whenever = get_repo_latest_releases(REPO_WHENEVER)
    console = get_rich_console()
    t = get_whenever_download_metadata(verbose)
    if t is None:
        return None
    fname, version, sha1_csum = t
    if verbose:
        console.print(CLI_MSG_DOWNLOADING_ASSET % fname, highlight=False)
    archive_url = f"{releases_whenever}/{fname}"
    dl_path = download_asset(archive_url, verbose=verbose)
    if dl_path is None:
        return None
    check = ""
    if verbose:
        console.print(CLI_MSG_VERIFYING_CHECKSUM, highlight=False)
    with open(dl_path, 'rb') as f:
        check = hashlib.sha1(f.read()).hexdigest().lower()
    if check != sha1_csum:
        if verbose:
            write_error(CLI_ERR_INVALID_CHECKSUM % fname)
        os.unlink(dl_path)
        return None
    return dl_path


# unzip the archive in the provided directory
def unzip_binaries_to_directory(archive, folder=None, verbose=False):
    console = get_rich_console()
    with ZipFile(archive, 'r') as z:
        bins = z.namelist()
        bins.remove("INSTRUCTIONS.md")
        if folder is None:
            folder = get_install_path()
        if folder is None:
            write_error(CLI_ERR_BINPATH_NOT_FOUND)
        else:
            if verbose:
                console.print(CLI_MSG_EXTRACTING_BINARIES % folder, highlight=False)
            try:
                z.extractall(folder, bins)
            except Exception as e:
                write_error(CLI_ERR_UNEXPECTED_EXCEPTION % e)


# use the two above-defined utilities to install the binaries
def install(folder=None, verbose=False):
    archive = download_and_check_whenever(verbose)
    unzip_binaries_to_directory(archive, folder, verbose)


# end.
