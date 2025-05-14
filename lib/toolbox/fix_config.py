# Fix configuration from legacy names and item types to new ones

import shutil

from ..i18n.strings import *
from ..items.item import ALL_AVAILABLE_ITEMS, ALL_AVAILABLE_ITEMS_D
from ..items.cond import Condition
from ..items.event import Event
from ..items.task import Task
from ..utility import write_warning, get_rich_console

from tomlkit import items, document, parse, item, aot

# specific imports for handled types of item
from ..extra.c_sysload_win32 import SystemLoadCondition
from ..extra.c_battery_charging_win32 import ChargingBatteryCondition
from ..extra.c_battery_low_win32 import LowBatteryCondition
from ..extra.c_session_locked_win32 import SessionLockedCondition



# extract an item signature directly from a table instead of creating an item
def table_signature(item: str, t: items.Table) -> str:
    if item not in ('condition', 'event', 'task'):
        raise ValueError("Invalid specification for item type")
    if item == 'condition':
        item = 'cond'
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
    t1.remove('type')
    t1.append('type', 'wmi')
    cond = target(t1)
    cond.updateitem()
    return cond.as_table()



# Legacy table
#
# A table of legacy signature to test whether some items have to be modified,
# mapped to their current counterparts
LEGACY_ITEMS = {
    'cond:command:sysload': 'cond:wmi:sysload',
    'cond:command:removabledrive_win': 'cond:command:removable_drive',
    'cond:command:removabledrive_linux': 'cond:command:removable_drive',
    'cond:command:session_locked_win': 'cond:wmi:session_locked',
    'cond:command:battery_low_win': 'cond:wmi:battery_low',
    'cond:command:battery_charging_win': 'cond:wmi:battery_charging',
    'cond:command:battery_low_linux': 'cond:command:battery_low',
    'cond:command:battery_charging_linux': 'cond:command:battery_charging',
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
    'cond:wmi:session_locked': (lambda t: cond_wmi_from_command(item_change_subtype(t, 'session_locked'), SessionLockedCondition)),
    'cond:command:battery_charging': (lambda t: item_change_subtype(t, 'battery_charging')),
    'cond:command:battery_low': (lambda t: item_change_subtype(t, 'battery_low')),
    'cond:command:removable_drive': (lambda t: item_change_subtype(t, 'removable_drive')),
    'event:dbus:session_lock': (lambda t: item_change_subtype(t, 'session_lock')),
    'event:dbus:session_unlock': (lambda t: item_change_subtype(t, 'session_unlock')),
    # ...
}



# the main fix function
def fix_config(filename: str, console=None) -> items.Table:
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
    for elem in ['condition', 'event', 'task']:
        if elem in doc:
            lot = aot()
            for t in doc[elem]:
                sig = table_signature(elem, t)
                if sig in legacy_sigs:
                    new_sig = LEGACY_ITEMS[sig]
                    if console:
                        name = t.get('name')
                        console.print(CLI_MSG_CONVERTING_ITEM % (name, sig, new_sig), highlight=False)
                    converter = CONVERSIONS[new_sig]
                    new_t = converter(t)
                    lot.append(new_t)
                else:
                    lot.append(t)
            res.append(elem, lot)
    return res


# fix config file at once, save a backup copy
def fix_config_file(filename, backup=True):
    console = get_rich_console()
    try:
        doc = fix_config(filename, console)
        if backup:
            new_name = "%s~" % filename
            console.print(CLI_MSG_BACKUP_CONFIG % new_name)
            shutil.move(filename, new_name)
        console.print(CLI_MSG_WRITE_NEW_CONFIG % filename)
        with open(filename, 'w') as f:
            f.write(doc.as_string())
    except Exception as e:
        write_warning(CLI_ERR_CANNOT_FIX_CONFIG % filename)


# end.
