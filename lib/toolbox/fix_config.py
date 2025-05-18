# Fix configuration from legacy names and item types to new ones

import shutil

from ..i18n.strings import *
from ..items.cond import Condition
from ..items.event import Event
from ..items.task import Task
from ..utility import (
    write_warning,
    get_rich_console,
    whenever_has_dbus,
    whenever_has_wmi,
)

from tomlkit import items, document, parse, item, aot

# specific imports for handled types of item
from ..extra.c_sysload_win32 import SystemLoadCondition
from ..extra.c_battery_charging_win32 import (
    ChargingBatteryCondition as ChargingBatteryCondition_W,
)
from ..extra.c_battery_low_win32 import LowBatteryCondition as LowBatteryCondition_W
from ..extra.c_session_locked_win32 import SessionLockedCondition
from ..extra.c_removabledrive_win32 import RemovableDrivePresent
from ..extra.c_battery_charging_linux import (
    ChargingBatteryCondition as ChargingBatteryCondition_L,
)
from ..extra.c_battery_low_linux import LowBatteryCondition as LowBatteryCondition_L

# ...


# extract an item signature directly from a table instead of creating an item
def table_signature(item: str, t: items.Table) -> str:
    if item not in ("condition", "event", "task"):
        raise ValueError("Invalid specification for item type")
    if item == "condition":
        item = "cond"
    ty = t.get("type", None)
    if ty is None:
        raise ValueError("Unknown item specific type")
    s = "%s:%s" % (item, ty)
    tags = t.get("tags", None)
    if tags:
        sub = tags.get("subtype", None)
        if sub is None:
            raise ValueError("Item specific subtype missing")
        s = "%s:%s" % (s, sub)
    return s


# generic change subtype of item, directly in the table
def item_change_subtype(t: items.Table, new_subtype: str) -> items.Table:
    t1 = t.copy()
    tags = t1.get("tags")
    tags["subtype"] = new_subtype
    t1["tags"] = tags
    return t1


# generic command-to-wmi converter for conditions
def cond_wmi_from_command(t: items.Table, target: Condition) -> items.Table:
    t1 = t.copy()
    command_params = [
        "startup_path",
        "command",
        "match_exact",
        "match_regular_expression",
        "success_stdout",
        "success_stderr",
        "success_status",
        "failure_stdout",
        "failure_stderr",
        "failure_status",
        "timeout_seconds",
        "case_sensitive",
        "include_environment",
        "set_environment_variables",
        "command_arguments",
        "environment_variables",
    ]
    for k in command_params:
        if k in t1:
            t1.remove(k)
    t1.remove("type")
    t1.append("type", "wmi")
    cond = target(t1)
    cond.updateitem()
    return cond.as_table()


# generic command-to-dbus converter for conditions
def cond_dbus_from_command(t: items.Table, target: Condition) -> items.Table:
    t1 = t.copy()
    command_params = [
        "startup_path",
        "command",
        "match_exact",
        "match_regular_expression",
        "success_stdout",
        "success_stderr",
        "success_status",
        "failure_stdout",
        "failure_stderr",
        "failure_status",
        "timeout_seconds",
        "case_sensitive",
        "include_environment",
        "set_environment_variables",
        "command_arguments",
        "environment_variables",
    ]
    for k in command_params:
        if k in t1:
            t1.remove(k)
    t1.remove("type")
    t1.append("type", "dbus")
    cond = target(t1)
    cond.updateitem()
    return cond.as_table()


# Legacy table
#
# A table of legacy signature to test whether some items have to be modified,
# mapped to their current counterparts. The mappings are selected by available
# option, otherwise a non existing mapping could be applied. DBus is applied
# first because, in theory, it is less specific, and in case a target has the
# same name both in WMI and DBus, the WMI version is chosen if WMI is present.
LEGACY_ITEMS = {
    # ...
}

LEGACY_ITEMS_DBUS = {
    "cond:dbus:removabledrive_linux": "cond:dbus:removable_drive",
    "cond:command:battery_low_linux": "cond:dbus:battery_low",
    "cond:command:battery_charging_linux": "cond:dbus:battery_charging",
    "event:dbus:session_lock_linux": "event:dbus:session_lock",
    "event:dbus:session_unlock_linux": "event:dbus:session_unlock",
    # ...
}

LEGACY_ITEMS_WMI = {
    "cond:command:sysload": "cond:wmi:sysload",
    "cond:command:removabledrive_win": "cond:wmi:removable_drive",
    "cond:command:session_locked_win": "cond:wmi:session_locked",
    "cond:command:battery_low_win": "cond:wmi:battery_low",
    "cond:command:battery_charging_win": "cond:wmi:battery_charging",
    # ...
}


def update_legacy_items():
    if whenever_has_dbus():
        for k in LEGACY_ITEMS_DBUS:
            LEGACY_ITEMS[k] = LEGACY_ITEMS_DBUS[k]
    if whenever_has_wmi():
        for k in LEGACY_ITEMS_WMI:
            LEGACY_ITEMS[k] = LEGACY_ITEMS_WMI[k]


# Conversion table
#
# the following is a list of conversions, identified by the current signature
# which represents the target item that should be built from the table that
# is found in the old-style table: the old style and new style signatures are
# matched and the appropriate conversion function is called on the old table
# in order to produce a new one for the specific item; to achieve this the
# old and new item factories are used, taken from the respective factory mods.
# Here too the mappings are applied according to the supported options.
CONVERSIONS = {
    # ...
}

CONVERSIONS_DBUS = {
    "cond:dbus:battery_charging": (
        lambda t: cond_dbus_from_command(
            item_change_subtype(t, "battery_charging"), ChargingBatteryCondition_L
        )
    ),
    "cond:dbus:battery_low": (
        lambda t: cond_dbus_from_command(
            item_change_subtype(t, "battery_low"), LowBatteryCondition_L
        )
    ),
    "cond:dbus:removable_drive": (lambda t: item_change_subtype(t, "removable_drive")),
    "event:dbus:session_lock": (lambda t: item_change_subtype(t, "session_lock")),
    "event:dbus:session_unlock": (lambda t: item_change_subtype(t, "session_unlock")),
    # ...
}

CONVERSIONS_WMI = {
    "cond:wmi:sysload": (lambda t: cond_wmi_from_command(t, SystemLoadCondition)),
    "cond:wmi:battery_charging": (
        lambda t: cond_wmi_from_command(t, ChargingBatteryCondition_W)
    ),
    "cond:wmi:battery_low": (lambda t: cond_wmi_from_command(t, LowBatteryCondition_W)),
    "cond:wmi:session_locked": (
        lambda t: cond_wmi_from_command(
            item_change_subtype(t, "session_locked"), SessionLockedCondition
        )
    ),
    "cond:wmi:removable_drive": (
        lambda t: cond_wmi_from_command(
            item_change_subtype(t, "removable_drive"), RemovableDrivePresent
        )
    ),
    # ...
}


def update_conversions():
    if whenever_has_dbus():
        for k in CONVERSIONS_DBUS:
            CONVERSIONS[k] = CONVERSIONS_DBUS[k]
    if whenever_has_wmi():
        for k in CONVERSIONS_WMI:
            CONVERSIONS[k] = CONVERSIONS_WMI[k]


# the main fix function
def fix_config(filename: str, console=None) -> items.Table:
    with open(filename) as f:
        toml = f.read()
    doc = parse(toml)
    globals = {
        "scheduler_tick_seconds": doc.get("scheduler_tick_seconds", 5),
        "randomize_checks_within_ticks": doc.get(
            "randomize_checks_within_ticks", False
        ),
    }

    legacy_sigs = LEGACY_ITEMS.keys()
    res = document()
    for k in globals:
        if globals[k] is not None:
            res.add(k, item(globals[k]))
    for elem in ["condition", "event", "task"]:
        if elem in doc:
            lot = aot()
            for t in doc[elem]:
                sig = table_signature(elem, t)
                if sig in legacy_sigs:
                    new_sig = LEGACY_ITEMS[sig]
                    if console:
                        name = t.get("name")
                        console.print(
                            CLI_MSG_CONVERTING_ITEM % (name, sig, new_sig),
                            highlight=False,
                        )
                    converter = CONVERSIONS[new_sig]
                    new_t = converter(t)
                    lot.append(new_t)
                else:
                    lot.append(t)
            res.append(elem, lot)
    return res


# fix config file at once, save a backup copy
def fix_config_file(filename, backup=True):
    update_legacy_items()
    update_conversions()
    console = get_rich_console()
    try:
        doc = fix_config(filename, console)
        if backup:
            new_name = "%s~" % filename
            console.print(CLI_MSG_BACKUP_CONFIG % new_name)
            shutil.move(filename, new_name)
        console.print(CLI_MSG_WRITE_NEW_CONFIG % filename)
        with open(filename, "w") as f:
            f.write(doc.as_string())
    except Exception as e:
        write_warning(CLI_ERR_CANNOT_FIX_CONFIG % filename)


# end.
