# about form

from lib.i18n.strings import *

from lib.utility import sg, get_whenever_version
from lib.icons import APP_ICON32 as APP_ICON
from lib.icons import APP_ICON64 as APP_BITMAP


# display a simple about box
def show_about_box():
    # TODO: well, this is actually too simple, provide a better alternative
    version = get_whenever_version()
    if version:
        text = "%s\n\n%s %s" % (UI_ABOUT_TEXT, UI_ABOUT_WHENEVER_VERSION, version)
    else:
        text = UI_ABOUT_TEXT
    sg.PopupOK(text, title=UI_ABOUT_TITLE, icon=APP_ICON, image=APP_BITMAP)


# end.
