# Module for creating conditions that determine that a battery is charging
# or attached to AC and above a certain threshold, specific for Windows
# platforms:
#
# - uses a WMI query to detect battery status
# - exploits the new feature of only triggering the condition once when
#   the actual parameters are met
# - normally the condition is only tested every minute (change the
#   CHECK_EXTRA_DELAY constant to specify a different number of seconds)
#
#  A module achieving the same goal on Linux is available.

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
ITEM_HR_NAME = "Charging Battery Condition"

UI_FORM_TITLE = f"{UI_APP}: Charging Battery Condition Editor"
UI_FORM_THRESHOLD_SC = "Battery charge is above:"


# default values
DEFAULT_THRESHOLD_VALUE = 80
CHECK_EXTRA_DELAY = 60


# localize the aforementioned constants: this pattern is the same in every
# extra module
from .i18n.extra_locale import localized_strings

m = localized_strings(__name__)
if m is not None:
    ITEM_HR_NAME = m.ITEM_HR_NAME
    UI_FORM_TITLE = m.UI_FORM_TITLE
    UI_FORM_THRESHOLD_SC = m.UI_FORM_THRESHOLD_SC


# check for availability: this version of the check is only for Windows, the
# one for Linux is in a separate file, and availability is in fact mutually
# exclusive: with this check we assume that this module is only run on Windows
def _available():
    if sys.platform.startswith("win"):
        if whenever_has_wmi():
            return True
    return False


# the specific item is derived from the actual parent item
class ChargingBatteryCondition(WMICondition):

    # availability at class level: these variables *MUST* be set for all items
    item_type = "wmi"
    item_subtype = "battery_charging"
    item_hrtype = ITEM_HR_NAME
    available = _available()

    def __init__(self, t: items.Table = None) -> None:
        # first initialize the base class (mandatory)
        WMICondition.__init__(self, t)

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
            self.tags.append("threshold", DEFAULT_THRESHOLD_VALUE)
        self.updateitem()

    def updateitem(self):
        # set base item properties according to specific parameters in `tags`
        threshold = self.tags.get("threshold", DEFAULT_THRESHOLD_VALUE)

        # see interpretation of BatteryStatus -in 2,6,7,8,9 here:
        # https://learn.microsoft.com/it-it/windows/win32/cimwin32prov/win32-battery
        self.query = (
            "SELECT * FROM Win32_Battery "
            + "WHERE BatteryStatus = 2 OR OR (BatteryStatus >= 6 AND BatteryStatus<= 9)"
        )
        self.result_check = [
            {
                "index": 0,
                "field": "EstimatedChargeRemaining",
                "operator": "gt",
                "value": threshold,
            },
        ]
        self.result_check_all = True
        self.check_after = CHECK_EXTRA_DELAY
        self.recur_after_failed_check = True


# dedicated form definition derived directly from one of the base forms
class form_ChargingBatteryCondition(form_Condition):

    def __init__(self, tasks_available, item=None):

        # check that item is the expected one for safety, build one by default
        if item:
            assert isinstance(item, ChargingBatteryCondition)
        else:
            item = ChargingBatteryCondition()
        super().__init__(UI_FORM_TITLE, tasks_available, item)

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # build the UI elements as needed and configure the layout
        l_threshold = ttk.Label(area, text=UI_FORM_THRESHOLD_SC)
        e_threshold = ttk.Entry(area)
        l_percent = ttk.Label(area, text="%")
        self.data_bind("threshold", e_threshold, TYPE_INT, lambda t: t > 0 and t < 100)

        l_threshold.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_threshold.grid(row=0, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)
        l_percent.grid(row=0, column=2, sticky=tk.E, padx=PAD, pady=PAD)

        area.columnconfigure(1, weight=1)

        # add captions of data to be checked
        self.add_check_caption("threshold", UI_FORM_THRESHOLD_SC)

        # always update the form at the end of initialization
        self._updateform()

    # update the form with the specific parameters (usually in the `tags`)
    def _updateform(self):
        self.data_set("threshold", self._item.tags.get("threshold"))
        return super()._updateform()

    # update the item from the form elements (usually update `tags`)
    def _updatedata(self):
        self._item.tags["threshold"] = self.data_get("threshold")
        self._item.updateitem()
        return super()._updatedata()


# function common to all extra modules to declare class items as factories
def factories():
    return (ChargingBatteryCondition, form_ChargingBatteryCondition)


# end.
