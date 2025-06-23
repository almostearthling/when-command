# get localized versions of strings for extra items UIs


import os
from importlib import import_module

from ...i18n.localizer import get_locale
from ...i18n.strings import ENV_WHEN_APP_USELOCALE


# this returns a module with localized constants, or None if said module is not
# found (that is, fall back to strings defined in the original module); other
# errors (like ImportError) are not caught, because they can be useful for
# debugging purposes; note that we need the last part of the mod name
def localized_strings(modname):
    _use_locale = os.environ.get(ENV_WHEN_APP_USELOCALE)
    loc = None
    if isinstance(_use_locale, str):
        _use_locale = _use_locale.lower()
        if _use_locale != "no":
            if _use_locale.startswith("yes:"):
                loc = get_locale(_use_locale.split(":", 1)[1])
            else:
                loc = get_locale()
    if loc is not None:
        try:
            modname = modname.split('.')[-1]
            loc_modname = f"{modname}_{loc}"
            loc_mod = import_module(f".{loc_modname}", "lib.extra.i18n")
            return loc_mod
        except ModuleNotFoundError:
            return None


__all__ = ["localized_strings"]


# end.