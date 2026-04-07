# Lua library static source files

import os
import sys

def lua_library_path() -> str:
    f = sys.modules[__name__].__file__
    assert(isinstance(f, str))
    return os.path.dirname(os.path.abspath(f))

# end.
