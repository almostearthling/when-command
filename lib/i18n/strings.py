# load the strings according to current I18N settings

import os


# this is the name of the environment variable that is used to inhibit use
# of the current locale and just fall back to the default (base) one
ENV_WHEN_APP_USELOCALE = "WHEN_APP_USELOCALE"


# non translateable strings: these will be also imported in localized strings
# module in order to get the application name, the circular import works as
# there are no mutual references, and this is imported completely in the UI
UI_APP = "When"
CLI_APP = "when"
UI_APP_LABEL = "When Automation Tool"
UI_APP_COPYRIGHT = "© 2023-2025 Francesco Garosi"
UI_APP_VERSION = "1.10.11b5"

# other strings that should not be translated
UI_WHENEVER = "Whenever"
CLI_WHENEVER = "whenever"

UI_ENVVARS = "WHENEVER"

UI_TIMEFORMAT_ANY_YEAR = "ANY_YEAR"
UI_TIMEFORMAT_ANY_MONTH = "ANY_MONTH"
UI_TIMEFORMAT_ANY_DAY = "ANY_DAY"
UI_TIMEFORMAT_ANY_WEEKDAY = "ANY_WEEKDAY"
UI_TIMEFORMAT_ANY_HOUR = "ANY_HOUR"
UI_TIMEFORMAT_ANY_MINUTE = "ANY_MINUTE"
UI_TIMEFORMAT_ANY_SECOND = "ANY_SECOND"

# symbols
SYM_OK = "✓"
SYM_FAIL = "✕"
SYM_UNKNOWN = "∅"


# first: import all fallback strings
from .strings_base import *
from .localizer import get_locale as _get_locale


# decide current locale according to OS and variable WHEN_APP_USELOCALE
def which_locale() -> str | None:
    use_locale = os.environ.get(ENV_WHEN_APP_USELOCALE)
    if isinstance(use_locale, str):
        use_locale = use_locale.lower()
        if use_locale != "no":
            if use_locale.startswith("yes:"):
                return _get_locale(use_locale.split(":", 1)[1])
            else:
                return _get_locale()
        else:
            return None
    else:
        return None


# if any exception occurs during this process, fallback strings remain valid
# otherwise the new ones, if found, overwrite the fallback strings: this also
# allows for string that do not exist in a translation to be still present,
# although not translated
_short_locale = which_locale()
if _short_locale is not None:
    try:
        exec(f"from .strings_{_short_locale} import *")
    except:
        pass


# end.
