# reset conditions on resume
#
# private items that enable the "Reset Conditions on Resume" feature: it is
# achieved by creating
#
# - a private event that fires when the workstation resumes from sleep
# - a private condition that the above event triggers
# - a private task that runs the whenever internal `reset_conditions` command

import sys
import os

from ..utility import get_private_item_name_prefix

if sys.platform.startswith("win"):
    from ..items.event_wmi import WMIEvent
elif sys.platform == "linux":
    from ..items.event_dbus import DBusEvent
else:
    raise OSError("unsupported platform")

from ..items.cond_event import EventCondition
from ..items.task_internal import InternalCommandTask


_ITEM_NAMES = get_private_item_name_prefix() + "ResetConditionsOnResume"

def name_ResetConditionsOnResume():
    return _ITEM_NAMES


# task and condition are the same for all platforms

_task = InternalCommandTask()
_task.name = _ITEM_NAMES
_task.command = "reset_conditions"
task_ResetConditionsOnResume = _task

_cond = EventCondition()
_cond.name = _ITEM_NAMES
_cond.tasks = [_ITEM_NAMES]
_cond.recurring = True
_cond.suspended = False
condition_ResetConditionsOnResume = _cond


# if no platform is matched, event is None just to avoid complaints
_event = None

# build the event for Windows platforms: see
# https://devblogs.microsoft.com/scripting/monitor-and-respond-to-windows-power-events-with-powershell/
# for details
if sys.platform.startswith("win"):
    _SECONDS_TO_MONITOR = 15
    _EVENT_RESUME = 7
    _event = WMIEvent()
    _event.name = _ITEM_NAMES
    _event.condition = _ITEM_NAMES
    _event.query = (
        f"SELECT * FROM Win32_PowerManagementEvent"
        f"  WITHIN {_SECONDS_TO_MONITOR}"
        f"  WHERE EventType={_EVENT_RESUME}"
    )

# build the event for Linux platforms: see
# https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html#Signals
# for details
# if sys.platform == "linux":
if True:
    from ..items.event_dbus import DBusEvent
    _event = DBusEvent()
    _event.name = _ITEM_NAMES
    _event.condition = _ITEM_NAMES
    _event.bus = ":system"
    _event.rule = (
        "type=signal,"
        "interface=org.freedesktop.login1.Manager,"
        "sender=org.freedesktop.login1,"
        "member=PrepareForSleep,"
    )
    _event.parameter_check = '[{0, "eq", false}]'

event_ResetConditionsOnResume = _event


# only export useful stuff
__all__ = [
    "task_ResetConditionsOnResume",
    "condition_ResetConditionsOnResume",
    "event_ResetConditionsOnResume",
    "name_ResetConditionsOnResume",
]


# end.
