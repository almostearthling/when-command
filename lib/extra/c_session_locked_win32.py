# Module for creating conditions that determine that the session is locked,
# specific for Windows platforms:
#
# - uses the new powershell and the Get-CimInstance utility/command
# - exploits the new feature of only triggering the condition once when
#   the actual parameters are met
# - gives the opportunity to perform the check often (every minute), at
#   a normal pace (every second minute) and seldomly (every 5 minutes)
#
#  A module achieving the same goal on Linux is (being made) available.

# this header is common to all extra modules
from tomlkit import items, table

import tkinter as tk
import ttkbootstrap as ttk

from ..i18n.strings import *
from ..utility import whenever_has_wmi

from ..forms.ui import *


# since a condition is defined, the base form is the one for conditions
from ..forms.cond import form_Condition

# import item to derive from
from ..items.cond_wmi import WMICondition


# imports specific to this module
import sys



# resource strings (not internationalized for the moment)
ITEM_COND_SESSION_LOCKED = "Session Locked Condition"

_UI_FORM_TITLE = "%s: Session Locked Condition Editor" % UI_APP

_UI_FORM_CHECKFREQ_SC = "Session lock check frequency:"
_UI_FORM_RB_CHECKFREQ_PEDANTIC = "Pedantic"
_UI_FORM_RB_CHECKFREQ_NORMAL = "Normal"
_UI_FORM_RB_CHECKFREQ_RELAXED = "Relaxed"


# values for check styles
_CHECK_EXTRA_DELAY = {
    'pedantic': 60,
    'normal': 120,
    'relaxed': 300,
}


# check for availability: this version of the check is only for Windows, the
# one for Linux is in a separate file, and availability is in fact mutually
# exclusive: with this check we assume that this module is only run on Windows
def _available():
    if sys.platform.startswith("win"):
        if whenever_has_wmi():
            return True
    return False


# the specific item is derived from the actual parent item
class SessionLockedCondition(WMICondition):

    # availability at class level: these variables *MUST* be set for all items
    item_type = 'wmi'
    item_subtype = 'session_locked'
    item_hrtype = ITEM_COND_SESSION_LOCKED
    available = _available()

    def __init__(self, t: items.Table=None) -> None:
        # first initialize the base class (mandatory)
        WMICondition.__init__(self, t)

        # then set type (same as base), subtype and human readable name: this
        # is mandatory in order to correctly display the item in all forms
        self.type = self.item_type
        self.subtype = self.item_subtype
        self.hrtype = self.item_hrtype

        # initializing from a table should always have this form:
        if t:
            assert(t.get('type') == self.type)
            self.tags = t.get('tags')
            assert(isinstance(self.tags, items.Table))
            assert(self.tags.get('subtype') == self.subtype)

        # while creating a new item must always initialize specific parameters
        else:
            self.tags = table()
            self.tags.append('subtype', self.subtype)
            self.tags.append('check_frequency', 'normal')
        self.updateitem()

    def updateitem(self):
        # set base item properties according to specific parameters in `tags`
        check_frequency = self.tags.get('check_frequency', 'normal')

        # everything I found on the subject is about finding a process running
        # whose executable is 'LogonUI.exe'; maybe a better solution is here:
        # https://stackoverflow.com/a/48785428/5138770
        self.query = "SELECT CreationClassName FROM Win32_Process WHERE Name='LogonUI.exe'"
        self.check_after = _CHECK_EXTRA_DELAY[check_frequency]
        self.recur_after_failed_check = True


# dedicated form definition derived directly from one of the base forms
class form_SessionLockedCondition(form_Condition):

    def __init__(self, tasks_available, item=None):

        # check that item is the expected one for safety, build one by default
        if item:
            assert(isinstance(item, SessionLockedCondition))
        else:
            item = SessionLockedCondition()
        super().__init__(_UI_FORM_TITLE, tasks_available, item)

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # build the UI elements as needed and configure the layout
        l_checkFreq = ttk.Label(area, text=_UI_FORM_CHECKFREQ_SC)
        rb_checkFreqPedantic = ttk.Radiobutton(area, text=_UI_FORM_RB_CHECKFREQ_PEDANTIC, value='pedantic')
        rb_checkFreqNormal = ttk.Radiobutton(area, text=_UI_FORM_RB_CHECKFREQ_NORMAL, value='normal')
        rb_checkFreqRelaxed = ttk.Radiobutton(area, text=_UI_FORM_RB_CHECKFREQ_RELAXED, value='relaxed')
        self.data_bind('check_frequency', (rb_checkFreqPedantic, rb_checkFreqNormal, rb_checkFreqRelaxed), TYPE_STRING)

        l_checkFreq.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        rb_checkFreqPedantic.grid(row=0, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)
        rb_checkFreqNormal.grid(row=1, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)
        rb_checkFreqRelaxed.grid(row=2, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)

        area.columnconfigure(1, weight=1)

        # always update the form at the end of initialization
        self._updateform()

    # update the form with the specific parameters (usually in the `tags`)
    def _updateform(self):
        self.data_set('check_frequency', self._item.tags.get('check_frequency'))
        return super()._updateform()

    # update the item from the form elements (usually update `tags`)
    def _updatedata(self):
        self._item.tags['check_frequency'] = self.data_get('check_frequency')
        self._item.updateitem()
        return super()._updatedata()



# function common to all extra modules to declare class items as factories
def factories():
    return (SessionLockedCondition, form_SessionLockedCondition)


# end.
