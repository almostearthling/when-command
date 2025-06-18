# get localized versions of strings for extra items UIs


from ...i18n.localizer import get_locale
from importlib import import_module


# this returns a module with localized constants, or None if said module is not
# found (that is, fall back to strings defined in the original module); other
# errors (like ImportError) are not caught, because they can be useful for
# debugging purposes; note that we need the last part of the mod name
def localized_strings(modname):
    try:
        loc = get_locale()
        if loc is not None:
            modname = modname.split('.')[-1]
            loc_modname = f"{modname}_{loc}"
            loc_mod = import_module(f".{loc_modname}", "lib.extra.i18n")
            return loc_mod
        else:
            return None
    except ModuleNotFoundError:
        return None


__all__ = ["localized_strings"]


# end.