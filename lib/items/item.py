# utility to define items

from lib.i18n.strings import *

from lib.forms.task_command import form_CommandTask
from lib.forms.task_lua import form_LuaScriptTask
from lib.forms.task_internal import form_InternalCommandTask

from lib.forms.cond_command import form_CommandCondition
from lib.forms.cond_dbus import form_DBusCondition
from lib.forms.cond_event import form_EventCondition
from lib.forms.cond_idle import form_IdleCondition
from lib.forms.cond_interval import form_IntervalCondition
from lib.forms.cond_lua import form_LuaScriptCondition
from lib.forms.cond_time import form_TimeCondition
from lib.forms.cond_wmi import form_WMICondition

from lib.forms.event_cli import form_CommandEvent
from lib.forms.event_dbus import form_DBusEvent
from lib.forms.event_fschange import form_FilesystemChangeEvent
from lib.forms.event_wmi import form_WMIEvent


from lib.items.task_command import CommandTask
from lib.items.task_lua import LuaScriptTask
from lib.items.task_internal import InternalCommandTask

from lib.items.cond_command import CommandCondition
from lib.items.cond_event import EventCondition
from lib.items.cond_dbus import DBusCondition
from lib.items.cond_idle import IdleCondition
from lib.items.cond_interval import IntervalCondition
from lib.items.cond_lua import LuaScriptCondition
from lib.items.cond_time import TimeCondition
from lib.items.cond_wmi import WMICondition

from lib.items.event_cli import CommandEvent
from lib.items.event_dbus import DBusEvent
from lib.items.event_fschange import FilesystemChangeEvent
from lib.items.event_wmi import WMIEvent

# to dynamically determine nature of extra items
from lib.items.task import Task
from lib.items.cond import Condition
from lib.items.event import Event


# other items will share the same file for both the item and the form, and
# all related string resources should be defined within the same file


# a list of all available items to allow creating new ones: all tuples consist
# of five fields:
#
# - type: one possible item type (see below)
# - hr name: the human readable name (from i18n.strings)
# - form: the corresponding form object that will be opened
# - item: the corresponding item class that would be instantiated
#
# the `signature` string is formed as follows:
#
# <cat>:<subtype>[:<spec>]
#
# where:
#
# - <cat> (category) is one of 'task', 'cond', 'event'
# - <subtype> is the *native* specialization in **whenever**
# - <spec> is a specialization obtained by crafting one of the native items
#   for a particular purpose
#
# All are separated by underscores (and corresponds to the item and related
# form identifiers); the <spec> part is optional, omitted for items that are
# native to **whenever**.
ALL_AVAILABLE_ITEMS = [
    # signature        hr name              form                        item
    ('task:command',   ITEM_TASK_COMMAND,   form_CommandTask,           CommandTask),
    ('task:lua',       ITEM_TASK_LUA,       form_LuaScriptTask,         LuaScriptTask),
    ('task:internal',  ITEM_TASK_INTERNAL,  form_InternalCommandTask,   InternalCommandTask),

    ('cond:command',   ITEM_COND_COMMAND,   form_CommandCondition,      CommandCondition),
    ('cond:dbus',      ITEM_COND_DBUS,      form_DBusCondition,         DBusCondition),
    ('cond:event',     ITEM_COND_EVENT,     form_EventCondition,        EventCondition),
    ('cond:idle',      ITEM_COND_IDLE,      form_IdleCondition,         IdleCondition),
    ('cond:interval',  ITEM_COND_INTERVAL,  form_IntervalCondition,     IntervalCondition),
    ('cond:lua',       ITEM_COND_LUA,       form_LuaScriptCondition,    LuaScriptCondition),
    ('cond:time',      ITEM_COND_TIME,      form_TimeCondition,         TimeCondition),
    ('cond:wmi',       ITEM_COND_WMI,       form_WMICondition,          WMICondition),

    ('event:cli',      ITEM_EVENT_CLI,      form_CommandEvent,          CommandEvent),
    ('event:dbus',     ITEM_EVENT_DBUS,     form_DBusEvent,             DBusEvent),
    ('event:fschange', ITEM_EVENT_FSCHANGE, form_FilesystemChangeEvent, FilesystemChangeEvent),
    ('event:wmi',      ITEM_EVENT_WMI,      form_WMIEvent,              WMIEvent),
]


# dynamically load modules from the `extra` package
from lib import extra

for m in extra.factories:
    item_class, item_form = extra.factories[m]
    if issubclass(item_class, Task):
        prefix = 'task'
    elif issubclass(item_class, Condition):
        prefix = 'cond'
    elif issubclass(item_class, Event):
        prefix = 'event'
    else:
        prefix = None
    if prefix:
        signature = '%s:%s:%s' % (prefix, item_class.item_type, item_class.item_subtype)        # type: ignore
        ALL_AVAILABLE_ITEMS.append((signature, item_class.item_hrtype, item_form, item_class))  # type: ignore


# a dictionary version of the above list
ALL_AVAILABLE_ITEMS_D = { i[0]: (i[1], i[2], i[3]) for i in ALL_AVAILABLE_ITEMS }


# end.
