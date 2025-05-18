# Module for creating conditions that determine that a battery is charging
# or attached to AC and above a certain threshold, specific for Windows
# platforms:
#
# - uses the new powershell and the Get-CimInstance utility/command
# - exploits the new feature of only triggering the condition once when
#   the actual parameters are met
# - normally the condition is only tested every fifth minute (change the
#   _CHECK_EXTRA_DELAY constant to specify a different number of seconds)
#
#  A module achieving the same goal on Linux is available.

# this header is common to all extra modules
from tomlkit import items, table

import tkinter as tk
import ttkbootstrap as ttk

from ..i18n.strings import *
from ..utility import whenever_has_dbus

from ..forms.ui import *


# since a condition is defined, the base form is the one for conditions
from ..forms.cond import form_Condition

# import item to derive from
from ..items.cond_dbus import DBusCondition


# imports specific to this module
import sys
import dbus


# resource strings (not internationalized for the moment)
ITEM_HR_NAME = "Charging Battery Condition"

_UI_FORM_TITLE = "%s: Charging Battery Condition Editor" % UI_APP

_UI_FORM_CHARGINGBATT_THRESHOLD_SC = "Battery charge is above:"


# default values
_DEFAULT_THRESHOLD_VALUE = 80
_CHECK_EXTRA_DELAY = 120


# check for availability: this version of the check is only for Linux, the
# one for Windows is in a separate file, and availability is in fact mutually
# exclusive: with this check we assume that this module is only run on Linux
def _available():
    if sys.platform == "linux":
        return whenever_has_dbus()
    else:
        return False


# the specific item is derived from the actual parent item
class ChargingBatteryCondition(DBusCondition):

    # availability at class level: these variables *MUST* be set for all items
    item_type = "dbus"
    item_subtype = "battery_charging"
    item_hrtype = ITEM_HR_NAME
    available = _available()

    def __init__(self, t: items.Table = None) -> None:
        # first initialize the base class (mandatory)
        DBusCondition.__init__(self, t)

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
            self.tags.append("threshold", _DEFAULT_THRESHOLD_VALUE)

        # detect battery by querying DBus
        # see https://upower.freedesktop.org/docs/Device.html
        bus = dbus.SystemBus()
        service_name = "org.freedesktop.UPower"
        device_service_name = "org.freedesktop.UPower.Device"
        props_name = "org.freedesktop.DBus.Properties"
        upower_obj = bus.get_object(service_name, "/org/freedesktop/UPower")
        upower = dbus.Interface(upower_obj, service_name)
        all_devices = upower.EnumerateDevices()
        all_batteries = list(
            x for x in all_devices if str(x).split("/")[-1].startswith("battery_")
        )
        batteries = []
        for x in all_batteries:
            batt_obj = bus.get_object(service_name, x)
            batt = dbus.Interface(batt_obj, props_name)
            if batt.Get(device_service_name, "PowerSupply"):
                batteries.append(str(x))
        # WARNING: this is completely arbitrary
        batteries.sort()
        self._batterypath = batteries.pop(0)
        self.updateitem()

    def updateitem(self):
        # set base item properties according to specific parameters in `tags`
        # for the values of `State` and `Percentage` see the above link
        threshold = int(self.tags.get("threshold", _DEFAULT_THRESHOLD_VALUE))
        self.bus = ":system"
        self.service = "org.freedesktop.UPower"
        self.object_path = self._batterypath
        self.interface = "org.freedesktop.DBus.Properties"
        self.method = "GetAll"
        self.parameter_call = '["org.freedesktop.UPower.Device"]'
        self.parameter_check = (
            """[
            { "index": [0, "State"], "operator": "neq", "value": 2 },
            { "index": [0, "Percentage"], "operator": "gt", "value": %s }
        ]"""
            % threshold
        )
        self.parameter_check_all = True
        self.check_after = _CHECK_EXTRA_DELAY
        self.recur_after_failed_check = True


# dedicated form definition derived directly from one of the base forms
class form_ChargingBatteryCondition(form_Condition):

    def __init__(self, tasks_available, item=None):

        # check that item is the expected one for safety, build one by default
        if item:
            assert isinstance(item, ChargingBatteryCondition)
        else:
            item = ChargingBatteryCondition()
        super().__init__(_UI_FORM_TITLE, tasks_available, item)

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # build the UI elements as needed and configure the layout
        l_threshold = ttk.Label(area, text=_UI_FORM_CHARGINGBATT_THRESHOLD_SC)
        e_threshold = ttk.Entry(area)
        l_percent = ttk.Label(area, text="%")
        self.data_bind("threshold", e_threshold, TYPE_INT, lambda t: t > 0 and t < 100)

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
    return (ChargingBatteryCondition, form_ChargingBatteryCondition)


# end.
