# sysload condition module
#
# use a command to check whether the system load is low: it uses
# - vmstat on Linux
# - (Get-CimInstance -Class Win32_Processor).LoadPercentage on Windows
#
# for now no availability on Mac
#
# This module serves as a template for possible other extra modules.

# this header is common to all extra modules
from tomlkit import items, table

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from ..i18n.strings import *
from ..utility import check_not_none, append_not_none

from ..forms.ui import *

# specific imports follow below here
import sys

# since a condition is defined, the base form is the one for conditions
from ..forms.cond import form_Condition

# import item to derive from
from ..items.cond_command import CommandCondition


# imports specific to this module
import shutil


# resource strings (not internationalized)
ITEM_HR_NAME = "System Load Below Threshold Condition"

UI_FORM_TITLE = "%s: System Load Condition Editor" % UI_APP
UI_FORM_SYSLOADTHRESHOLD_SC = "Load is below:"


# default values
DEFAULT_LOW_LOAD_PERC = 3
CHECK_EXTRA_DELAY = 60


# localize the aforementioned constants: this pattern is the same in every
# extra module
from .i18n.localized import localized_strings

m = localized_strings(__name__)
if m is not None:
    ITEM_HR_NAME = m.ITEM_HR_NAME
    UI_FORM_TITLE = m.UI_FORM_TITLE
    UI_FORM_SYSLOADTHRESHOLD_SC = m.UI_FORM_SYSLOADTHRESHOLD_SC


# check for availability: in this case check all needed commands
def _available():
    if sys.platform == "linux":
        if (
            shutil.which("bash")
            and shutil.which("vmstat")
            and shutil.which("bc")
            and shutil.which("awk")
        ):
            return True
        return False
    else:
        return False


# the specific item is derived from the actual parent item
class SystemLoadCondition(CommandCondition):

    # availability at class level: these variables *MUST* be set for all items
    item_type = "command"
    item_subtype = "sysload"
    item_hrtype = ITEM_HR_NAME
    available = _available()

    def __init__(self, t: items.Table = None) -> None:
        # first initialize the base class
        CommandCondition.__init__(self, t)
        # then set type (same as base), subtype and human readable name
        self.type = self.item_type
        self.subtype = self.item_subtype
        self.hrtype = self.item_hrtype
        if t:
            assert t.get("type") == self.type
            self.tags = t.get("tags")
            assert isinstance(self.tags, items.Table)
            assert self.tags.get("subtype") == self.subtype
        else:
            self.tags = table()
            self.tags.append("subtype", self.subtype)
            self.tags.append("threshold", DEFAULT_LOW_LOAD_PERC)
        self.updateitem()

    def updateitem(self):
        self.command = "bash"
        self.command_arguments = [
            "-c",
            "echo '%s <' `vmstat | tail -1 | awk '{print \$14}'` | bc"
            % self.tags.get("threshold", DEFAULT_LOW_LOAD_PERC),
        ]
        self.success_stdout = "1"
        self.startup_path = "."
        self.check_after = CHECK_EXTRA_DELAY  # for now keep it fixed to one minute
        self.recur_after_failed_check = True


# dedicated form definition derived directly from one of the base forms
class form_SystemLoadCondition(form_Condition):

    def __init__(self, tasks_available, item=None):

        # check that item is the expected one for safety, build one by default
        if item:
            assert isinstance(item, SystemLoadCondition)
        else:
            item = SystemLoadCondition()
        super().__init__(UI_FORM_TITLE, tasks_available, item)

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # build the UI elements as needed and configure the layout
        l_threshold = ttk.Label(area, text=UI_FORM_SYSLOADTHRESHOLD_SC)
        e_threshold = ttk.Entry(area)
        l_percent = ttk.Label(area, text="%")
        self.data_bind("threshold", e_threshold, TYPE_INT, lambda x: 0 < x < 100)

        l_threshold.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_threshold.grid(row=0, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)
        l_percent.grid(row=0, column=2, sticky=tk.E, padx=PAD, pady=PAD)

        area.columnconfigure(1, weight=1)

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
    return (SystemLoadCondition, form_SystemLoadCondition)


# end.
