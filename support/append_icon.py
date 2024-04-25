#!/usr/bin/env python
#
# This small utility is used to append graphics/icons to the `lib/icons.py`
# resource file, as base64 encoded binary strings. To use it, just launch
#
# $ python support/append_icon.py VARNAME path/to/iconfile.png
#
# from the project base directory to update the resource file automatically.

import os
import sys
import shutil
import base64

import re


RE_VARNAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

ICON_PLACEHOLDER = "# APPEND_ICONS_HERE"
ICON_SOURCE = "lib/icons.py"


# verbose output shortcut
def oerr(s, verbose=True):
    if verbose:
        sys.stderr.write("append_icon: %s\n" % s)



if __name__ == '__main__':
    if len(sys.argv) != 3:
        oerr("invalid number of arguments")
        sys.exit(1)
    if not  RE_VARNAME.match(sys.argv[1]):
        oerr("argument `%s` not suitable as variable name" % sys.argv[1])
        sys.exit(1)
    try:
        with open(sys.argv[2], 'rb') as f:
            bytes = f.read()
    except Exception as e:
        oerr("could not open `%s`" % sys.argv[2])
        sys.exit(2)
    txt = "%s = %s" % (sys.argv[1], base64.b64encode(bytes))
    mfile = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), "..", ICON_SOURCE))
    try:
        with open(mfile) as f:
            src = f.read()
        shutil.copy(mfile, "%s~" % mfile)
    except Exception as e:
        oerr("could not open `%s`" % mfile)
        sys.exit(2)
    src = src.replace(ICON_PLACEHOLDER, "%s\n%s" % (txt, ICON_PLACEHOLDER))
    try:
        with open(mfile, 'w') as f:
            f.write(src)
    except Exception as e:
        oerr("could not write to `%s`" % mfile)
        sys.exit(2)


#end.
