# utilities to download assets from GitHub


import os
import sys
import requests
import urllib

from ..i18n.strings import *
from ..utility import write_error, get_default_configdir


# URL definition strings
GITHUB_BASE = "github.com/almostearthling"
GITHUB_PROTOCOL = "https"


# retrieve an asset from an URL
def retrieve_asset(URL, verbose=False):
    try:
        r = requests.get(URL)
        return r.content
    except Exception as e:
        if verbose:
            write_error(CLI_ERR_DOWNLOADING_ASSET_MSG % (URL, e))
        return None


# retrieve text from an URL
def retrieve_text_asset(URL, verbose=False) -> str | None:
    try:
        r = requests.get(URL)
        return r.text
    except Exception as e:
        if verbose:
            write_error(CLI_ERR_DOWNLOADING_ASSET_MSG % (URL, e))
        return None


# download an asset identified by an URL to a provided directory or to
# the TEMP directory if none is specified
def download_asset(URL, local=None, verbose=False) -> None | str:
    sr = urllib.parse.urlsplit(URL)     # type: ignore
    fname = os.path.basename(sr.path)
    if local is None:
        try:
            local = os.environ["TEMP"]
        except KeyError:
            tmpdir = "Temp" if sys.platform == "win32" else "tmp"
            local = os.path.join(get_default_configdir(), tmpdir)
            if not os.path.isdir(local):
                os.makedirs(local)
    else:
        if not os.path.isdir(local):
            if verbose:
                write_error(f"{local} is not a directory")
            return None
    dlname = os.path.join(local, fname)
    b = retrieve_asset(URL)
    if b is not None:
        with open(dlname, "wb") as f:
            f.write(b)
        return dlname
    else:
        return None


# some URL entries
def get_repo_base_url(repo) -> str:
    return f"{GITHUB_PROTOCOL}://{GITHUB_BASE}/{repo}"


def get_repo_latest_releases(repo) -> str:
    base = get_repo_base_url(repo)
    return f"{base}/releases/latest/download"


__all__ = [
    "retrieve_asset",
    "retrieve_text_asset",
    "download_asset",
    "get_repo_base_url",
    "get_repo_latest_releases",
]


# end.
