# utilities to determine platform capabilities

import sys
import os
import shutil


_PLATFORM = None

_COMMANDS_AVAILABLE = []
_COMMANDS_UNAVAILABLE = []



def is_linux() -> bool:
    global _PLATFORM
    if _PLATFORM is None:
        platform = sys.platform
        if platform.startswith("linux"):
            _PLATFORM = "linux"
            return True
        else:
            return False
    else:
        return bool(_PLATFORM == "linux")

def is_windows() -> bool:
    global _PLATFORM
    if _PLATFORM is None:
        platform = sys.platform
        if platform.startswith("win"):
            _PLATFORM = "windows"
            return True
        else:
            return False
    else:
        return bool(_PLATFORM == "windows")

def is_mac() -> bool:
    global _PLATFORM
    if _PLATFORM is None:
        platform = sys.platform
        if platform.startswith("darwin"):
            _PLATFORM = "mac"
            return True
        else:
            return False
    else:
        return bool(_PLATFORM == "mac")

def has_command(cmd: str) -> bool:
    global _COMMANDS_AVAILABLE, _COMMANDS_UNAVAILABLE
    if cmd in _COMMANDS_UNAVAILABLE:
        return False
    elif cmd in _COMMANDS_AVAILABLE:
        return True
    else:
        if shutil.which(cmd) is None:
            _COMMANDS_UNAVAILABLE.append(cmd)
            return False
        else:
            _COMMANDS_AVAILABLE.append(cmd)
            return True

def is_command(path):
    if os.path.exists(path) and os.access(path, os.X_OK):
        return True
    elif shutil.which(path):
        return True
    else:
        return False

def is_dir(path):
    if os.path.exists(os.path.join(path, ".")):
        return True
    else:
        return False


__all__ = [
    "is_linux",
    "is_windows",
    "is_mac",
    "is_command",
    "is_dir",
    "has_command",
]

# end.
