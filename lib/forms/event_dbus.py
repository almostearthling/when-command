# DBus event form 
# this form is here only for completeness and **must never** be displayed

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import APP_ICON32 as APP_ICON

from lib.forms.event import form_Event
from lib.items.event_dbus import DBusEvent


# (extra) layout generator
def _form_layout():
    return [
        [ sg.Frame(UI_FORM_SPECIFIC_PARAMS, [[
            sg.T(UI_CAPTION_NOTSUPPORTED),
        ]], expand_x=True, expand_y=True) ]
    ]


# specialized subform
class form_DBusEvent(form_Event):
    def __init__(self, conditions_available, item=None):
        if item:
            assert(isinstance(item, DBusEvent))
        else:
            item = DBusEvent()
        extra_layout = _form_layout()
        form_Event.__init__(self, UI_TITLE_CLIEVENT, conditions_available, extra_layout, item)

    def _updatedata(self):
        form_Event._updatedata(self)

    def _updateitem(self):
        form_Event._updateitem(self)

    def process_event(self, event, values):
        return super().process_event(event, values)


# end.