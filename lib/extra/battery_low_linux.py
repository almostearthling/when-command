# Module for creating conditions that determine that a battery is draining
# and below a certain threshold, specific for Linux platforms:
#
# - uses the upower command, which in turn relies on DBus: an optimization
#   will be to directly ask DBus saving many subprocesses; this version should
#   be considered temporary
# - exploits the new feature of only triggering the condition once when
#   the actual parameters are met
# - normally the condition is only tested every fifth minute (change the
#   _CHECK_EXTRA_DELAY constant to specify a different number of seconds)
#
#  A module achieving the same goal on Linux is (being made) available.

# this header is common to all extra modules
from tomlkit import items, table

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from ..i18n.strings import *
from ..utility import check_not_none, append_not_none

from ..forms.ui import *


# since a condition is defined, the base form is the one for conditions
from ..forms.cond import form_Condition

# import item to derive from
from ..items.cond_command import CommandCondition


# imports specific to this module
import sys
import subprocess
import shutil



# resource strings (not internationalized for the moment)
ITEM_COND_LOWBATT = "Low Battery Condition"

_UI_TITLE_LOWBATT = "%s: Low Battery Condition Editor" % UI_APP
_UI_FORM_LOWBATT_THRESHOLD_SC = "Battery charge is below:"


# default values
_DEFAULT_THRESHOLD_VALUE = 40
_CHECK_EXTRA_DELAY = 300


# check for availability: this version of the check is only for Linux, the
# one for Windows is in a separate file, and availability is in fact mutually
# exclusive: with this check we assume that this module is only run on Linux
def _available():
    if sys.platform == 'linux':
        if (
            shutil.which("upower") and
            shutil.which("bash") and
            shutil.which("grep") and
            shutil.which("awk") and
            shutil.which("sed")
        ):
            return True
        return False
    else:
        return False


# the specific item is derived from the actual parent item
class LowBatteryCondition(CommandCondition):

    # availability at class level: these variables *MUST* be set for all items
    item_type = 'command'
    item_subtype = 'battery_low_linux'
    item_hrtype = ITEM_COND_LOWBATT
    available = _available()

    def __init__(self, t: items.Table=None) -> None:
        # first initialize the base class (mandatory)
        CommandCondition.__init__(self, t)

        # then set type (same as base), subtype and human readable name: this
        # is mandatory in order to correctly display the item in all forms
        self.type = self.item_type
        self.subtype = self.item_subtype
        self.hrtype = self.item_hrtype

        # initializin from a table should always have this form:
        if t:
            assert(t.get('type') == self.type)
            self.tags = t.get('tags')
            assert(isinstance(self.tags, items.Table))
            assert(self.tags.get('subtype') == self.subtype)

        # while creating a new item must always initialize specific parameters
        else:
            self.tags = table()
            self.tags.append('subtype', self.subtype)
            self.tags.append('threshold', _DEFAULT_THRESHOLD_VALUE)
        self._batterypath = subprocess.run(
            ['bash', '-c', "upower -e | grep -F 'battery'"],
            capture_output=True,
        ).stdout.decode("utf-8").strip()
        self.updateitem()

    def updateitem(self):
        # set base item properties according to specific parameters in `tags`
        threshold = self.tags.get('threshold', _DEFAULT_THRESHOLD_VALUE)
        battery = self._batterypath
        cmdline = (
            f"( upower -i {battery} | grep -F 'state:' | grep -F 'discharging' > /dev/null 2>&1 ) && " +
            f"[ `upower -i {battery} | grep -F 'percentage:' | awk '{{print $2}}' | sed 's/%//g'` -lt {threshold} ] && " +
            f"echo OK"
        )
        self.command = "bash"
        self.command_arguments = [
            "-c",
            cmdline,
        ]
        self.success_stdout = "OK"
        self.startup_path = "."
        self.check_after = _CHECK_EXTRA_DELAY
        self.recur_after_failed_check = True


# dedicated form definition derived directly from one of the base forms
class form_LowBatteryCondition(form_Condition):

    def __init__(self, tasks_available, item=None):

        # check that item is the expected one for safety, build one by default
        if item:
            assert(isinstance(item, LowBatteryCondition))
        else:
            item = LowBatteryCondition()
        super().__init__(_UI_TITLE_LOWBATT, tasks_available, item)

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # build the UI elements as needed and configure the layout
        l_threshold = ttk.Label(area, text=_UI_FORM_LOWBATT_THRESHOLD_SC)
        e_threshold = ttk.Entry(area)
        l_percent = ttk.Label(area, text="%")
        self.data_bind('threshold', e_threshold, TYPE_INT, lambda t: t > 0 and t < 100)

        l_threshold.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_threshold.grid(row=0, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)
        l_percent.grid(row=0, column=2, sticky=tk.E, padx=PAD, pady=PAD)

        area.columnconfigure(1, weight=1)

        # always update the form at the end of initialization
        self._updateform()

    # update the form with the specific parameters (usually in the `tags`)
    def _updateform(self):
        self.data_set('threshold', self._item.tags.get('threshold'))
        return super()._updateform()

    # update the item from the form elements (usually update `tags`)
    def _updatedata(self):
        self._item.tags['threshold'] = self.data_get('threshold')
        self._item.updateitem()
        return super()._updatedata()



# function common to all extra modules to declare class items as factories
def factories():
    return (LowBatteryCondition, form_LowBatteryCondition)


# end.
