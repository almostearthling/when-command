# DBus condition form (unsupported)
# this form is here only for completeness and **must never** be displayed

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import APP_ICON32 as APP_ICON

from lib.forms.cond import form_Condition
from lib.items.cond_dbus import DBusCondition


# (extra) layout generator
def _form_layout():
    return [
        [ sg.Frame(UI_FORM_EVENT, [[
            sg.T(UI_CAPTION_NOSPECIFICPARAMS),
        ]], expand_x=True, expand_y=True) ]
    ]


# specialized subform
class form_DBusCondition(form_Condition):
    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, DBusCondition))
        else:
            item = DBusCondition()
        extra_layout = _form_layout()
        form_Condition.__init__(self, UI_TITLE_DBUSCOND, tasks_available, extra_layout, item)

    def _updatedata(self):
        form_Condition._updatedata(self)

    def _updateitem(self):
        form_Condition._updateitem(self)

    def process_event(self, event, values):
        return super().process_event(event, values)


# end.