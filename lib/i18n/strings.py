# load the strings according to current I18N settings

# non translateable strings: these will be also imported in localized strings
# module in order to get the application name, the circular import works as
# there are no mutual references, and this is imported completely in the UI
UI_APP = "When"
UI_APP_LABEL = "When Automation Tool"
UI_APP_COPYRIGHT = "© 2023-2025 Francesco Garosi"
UI_APP_VERSION = "1.10.7b4"


# TODO: internationalization strategy
# for now: just fall back to base
from lib.i18n.strings_base import *


# end.
