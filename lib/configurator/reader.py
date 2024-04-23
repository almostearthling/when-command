# reader
# read and parse a configuration file

from tomlkit import parse

# import item definitions
from lib.items.task_command import CommandTask
from lib.items.task_lua import LuaScriptTask

from lib.items.cond_command import CommandCondition
from lib.items.cond_lua import LuaScriptCondition
from lib.items.cond_interval import IntervalCondition
from lib.items.cond_idle import IdleCondition
from lib.items.cond_event import EventCondition
from lib.items.cond_time import TimeCondition
# ...

from lib.items.event_cli import CommandEvent
from lib.items.event_dbus import DBusEvent
from lib.items.event_fschange import FilesystemChangeEvent


def read_whenever_config(filename):
    with open(filename) as f:
        toml = f.read()
    doc = parse(toml)
    res_tasks = []
    res_conditions = []
    res_events = []
    res_globals = {
        'scheduler_tick_seconds': doc.get('scheduler_tick_seconds', 5),
        'randomize_checks_within_ticks': doc.get('randomize_checks_within_ticks', False),
    }
    for item_table in doc['task']:
        if item_table['type'] == 'command':
            item = CommandTask(item_table)
        elif item_table['type'] == 'lua':
            item = LuaScriptTask(item_table)
        else:
            item = None
        if item:
            res_tasks.append(item)
    for item_table in doc['condition']:
        if item_table['type'] == 'command':
            item = CommandCondition(item_table)
        elif item_table['type'] == 'lua':
            item = LuaScriptCondition(item_table)
        elif item_table['type'] == 'interval':
            item = IntervalCondition(item_table)
        elif item_table['type'] == 'idle':
            item = IdleCondition(item_table)
        elif item_table['type'] == 'time':
            item = TimeCondition(item_table)
        elif item_table['type'] == 'event':
            item = EventCondition(item_table)
        # ...
        else:
            item = None
        if item:
            res_conditions.append(item)
    for item_table in doc['event']:
        if item_table['type'] == 'cli':
            item = CommandEvent(item_table)
        elif item_table['type'] == 'dbus':
            item = DBusEvent(item_table)
        elif item_table['type'] == 'fschange':
            item = FilesystemChangeEvent(item_table)
        # ...
        if item:
            res_events.append(item)
    return (res_tasks, res_conditions, res_events, res_globals)


# end.
