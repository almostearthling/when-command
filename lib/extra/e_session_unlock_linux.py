# Module to create a session unlocked event for linux systems
#
# On Linux this is implemented via DBus, so it actually does not check
# continuously for the current state, it waits for a specific event with
# specific message parameters instead, being lighter and more reactive
# than its Windows counterpart (which is directly a condition).
#
# WARNING: this module has not been tested, it is in the development
#          branch in order to be tested on linux machines.

# this header is common to all extra modules
from tomlkit import items, table

import tkinter as tk
import ttkbootstrap as ttk

from ..i18n.strings import *
from ..utility import whenever_has_dbus

from ..forms.ui import *


# import form to derive from
from ..forms.event import form_Event

# import item to derive from
from ..items.event_dbus import DBusEvent


# imports specific to this module
import sys


# resource strings (not internationalized for the moment)
ITEM_HR_NAME = "Session Unlocked Event"

_UI_FORM_TITLE = "%s: Session Unlocked Event Editor" % UI_APP


# check for availability: include all needed checks in this function, may
# or may not include actually checking the hosting platform
# check for availability
def _available():
    if sys.platform == "linux":
        return whenever_has_dbus()
    else:
        return False


# the DBus filter
_DBUS_FILTER_EXPRESSION = "".join(
    (
        """
        type='signal',
        sender='org.freedesktop.login1',
        interface='org.freedesktop.DBus.Properties',
        member='PropertiesChanged'
        """
    )
    .strip()
    .split()
)

# the DBus message parameters check
_DBUS_PARAMETER_CHECK = (
    { 'index': [1, "LockedHint"], 'operator': "eq", 'value': False },
)


# the specific item is derived from the actual parent item
class SessionUnlockEvent(DBusEvent):

    # availability at class level: these variables *MUST* be set for all items
    item_type = "dbus"
    item_subtype = "session_unlock"
    item_hrtype = ITEM_HR_NAME
    available = _available()

    def __init__(self, t: items.Table = None) -> None:
        # first initialize the base class (mandatory)
        super().__init__(t)

        # then set type (same as base), subtype and human readable name: this
        # is mandatory in order to correctly display the item in all forms
        self.type = self.item_type
        self.subtype = self.item_subtype
        self.hrtype = self.item_hrtype

        # initializing from a table should always have this form:
        if t:
            assert t.get("type") == self.type
            self.tags = t.get("tags")
            assert isinstance(self.tags, items.Table)
            assert self.tags.get("subtype") == self.subtype

        # while creating a new item must always initialize specific parameters
        else:
            self.tags = table()
            self.tags.append("subtype", self.subtype)

        self.updateitem()

    def updateitem(self):
        # set base item properties according to specific parameters in `tags`
        self.bus = ":system"
        self.rule = _DBUS_FILTER_EXPRESSION
        self.parameter_check = _DBUS_PARAMETER_CHECK


# dedicated form definition derived directly from one of the base forms
class form_SessionUnlockEvent(form_Event):

    def __init__(self, conditions_available, item=None):

        # check that item is the expected one for safety, build one by default
        if item:
            assert isinstance(item, SessionUnlockEvent)
        else:
            item = SessionUnlockEvent()
        super().__init__(_UI_FORM_TITLE, conditions_available, item)

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # build the UI elements as needed and configure the layout
        l_parameter1 = ttk.Label(area, text=UI_CAPTION_NOSPECIFICPARAMS)
        l_parameter1.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        # always update the form at the end of initialization
        self._updateform()

    # update the form with the specific parameters (usually in the `tags`)
    def _updateform(self):
        return super()._updateform()

    # update the item from the form elements (usually update `tags`)
    def _updatedata(self):
        self._item.updateitem()
        return super()._updatedata()


# function common to all extra modules to declare class items as factories
def factories():
    return (SessionUnlockEvent, form_SessionUnlockEvent)


# end.
