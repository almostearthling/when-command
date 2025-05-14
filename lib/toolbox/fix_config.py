# Fix configuration from legacy names and item types to new ones

import shutil

from ..items.item import ALL_AVAILABLE_ITEMS, ALL_AVAILABLE_ITEMS_D
from ..items.cond import Condition
from ..items.event import Event
from ..items.task import Task
from ..configurator.writer import write_whenever_config

from tomlkit import items, document, parse, item, aot

# specific imports for handled types of item
from ..extra.c_sysload_win32 import SystemLoadCondition
from ..extra.c_battery_charging_win32 import ChargingBatteryCondition
from ..extra.c_battery_low_win32 import LowBatteryCondition



# extract an item signature directly from a table instead of creating an item
def table_signature(item: str, t: items.Table) -> str:
    if item not in ('cond', 'event', 'task'):
        raise ValueError("Invalid specification for item type")
    ty = t.get('type', None)
    if ty is None:
        raise ValueError("Unknown item specific type")
    s = "%s:%s" % (item, ty)
    tags = t.get('tags', None)
    if tags:
        sub = tags.get('subtype', None)
        if sub is None:
            raise ValueError("Item specific subtype missing")
        s = "%s:%s" % (s, sub)
    return s



# generic change subtype of item, directly in the table
def item_change_subtype(t: items.Table, new_subtype: str) -> items.Table:
    t1 = t.copy()
    tags = t1.get('tags')
    tags['subtype'] = new_subtype
    t1['tags'] = tags
    return t1



# generic command-to-wmi converter for conditions
def cond_wmi_from_command(t: items.Table, target: Condition) -> items.Table:
    t1 = t.copy()
    t1.remove('command')
    t1.remove('command_arguments')
    cond = target(t1)
    cond.updateitem()
    return cond.as_table()


# specific conversion functions, referenced in the conversion table below
def cond_wmi_sysload__cond_command_sysload(t: items.Table) -> items.Table:
    return cond_wmi_from_command(t, SystemLoadCondition)


# Legacy table
#
# A table of legacy signature to test whether some items have to be modified,
# mapped to their current counterparts
LEGACY_ITEMS = {
    'cond:command:sysload': 'cond:wmi:sysload',
    'cond:command:removabledrive': 'cond:command:removable_drive',
    'cond:command:session_locked_win': 'cond:command:session_locked',
    'cond:command:battery_low_win': 'cond:wmi:battery_low',
    'cond:command:battery_charging_win': 'cond:wmi:battery_charging',
    'event:dbus:session_lock_linux': 'event:dbus:session_lock',
    'event:dbus:session_unlock_linux': 'event:dbus:session_unlock',
    # ...
}


# Conversion table
#
# the following is a list of conversions, identified by the current signature
# which represents the target item that should be built from the table that
# is found in the old-style table: the old style and new style signatures are
# matched and the appropriate conversion function is called on the old table
# in order to produce a new one for the specific item; to achieve this the
# old and new item factories are used, taken from the respective factory mods
CONVERSIONS = {
    'cond:wmi:sysload': (lambda t: cond_wmi_from_command(t, SystemLoadCondition)),
    'cond:wmi:battery_charging': (lambda t: cond_wmi_from_command(t, ChargingBatteryCondition)),
    'cond:wmi:battery_low': (lambda t: cond_wmi_from_command(t, LowBatteryCondition)),
    'cond:command:removable_drive': (lambda t: item_change_subtype(t, 'removable_drive')),
    'cond:command:session_locked': (lambda t: item_change_subtype(t, 'session_locked')),
    'event:dbus:session_lock': (lambda t: item_change_subtype(t, 'session_lock')),
    'event:dbus:session_unlock': (lambda t: item_change_subtype(t, 'session_unlock')),
    # ...
}


# the main fix function
def fix_config(filename: str) -> items.Table:
    with open(filename) as f:
        toml = f.read()
    doc = parse(toml)
    globals = {
        'scheduler_tick_seconds': doc.get('scheduler_tick_seconds', 5),
        'randomize_checks_within_ticks': doc.get('randomize_checks_within_ticks', False),
    }

    legacy_sigs = LEGACY_ITEMS.keys()
    res = document()
    for k in globals:
        if globals[k] is not None:
            res.add(k, item(globals[k]))
    if 'task' in doc:
        tasks = aot()
        for t in doc['task']:
            sig = table_signature(t)
            if sig in legacy_sigs:
                new_sig = LEGACY_ITEMS[sig]
                converter = CONVERSIONS[new_sig]
                new_t = converter(t)
                tasks.append(new_t)
            else:
                tasks.append(t)
        res.append('task', t)
    if 'condition' in doc:
        tasks = aot()
        for t in doc['condition']:
            sig = table_signature(t)
            if sig in legacy_sigs:
                new_sig = LEGACY_ITEMS[sig]
                converter = CONVERSIONS[new_sig]
                new_t = converter(t)
                tasks.append(new_t)
            else:
                tasks.append(t)
        res.append('condition', t)
    if 'event' in doc:
        tasks = aot()
        for t in doc['event']:
            sig = table_signature(t)
            if sig in legacy_sigs:
                new_sig = LEGACY_ITEMS[sig]
                converter = CONVERSIONS[new_sig]
                new_t = converter(t)
                tasks.append(new_t)
            else:
                tasks.append(t)
        res.append('event', t)
    return res


# fix config file at once, save a backup copy
def fix_config_file(filename, backup=True):
    doc = fix_config(filename)
    if backup:
        new_name = "%s~"
        shutil.move(filename, new_name)
    with open(filename, 'w') as f:
        f.write(doc.as_string())


# end.
