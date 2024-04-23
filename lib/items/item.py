# utility to define items

from lib.i18n.strings import *

from lib.forms.task_command import form_CommandTask
from lib.forms.task_lua import form_LuaScriptTask
# ...

from lib.forms.cond_command import form_CommandCondition
from lib.forms.cond_event import form_EventCondition
from lib.forms.cond_idle import form_IdleCondition
from lib.forms.cond_interval import form_IntervalCondition
from lib.forms.cond_lua import form_LuaScriptCondition
from lib.forms.cond_time import form_TimeCondition
# ...

from lib.forms.event_cli import form_CommandEvent
from lib.forms.event_fschange import form_FilesystemChangeEvent
# ...


# a list of all available items to allow creating new ones: all tuples consist
# of five fields:
#
# - type: one possible item type (see below)
# - hr name: the human readable name (from i18n.strings)
# - form: the corresponding form object that will be opened
# - OS: one of 'win', 'linux', 'mac' (None if all OSs are supported)
# - OS variant: the supported OS variant, a short nickname such as 'u2204',
#   'win10', etc. (None if all variants are supported)
#
# the `type` string is formed as follows:
#
# <cat>_<subtype>[_<spec>]
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
    # type                          hr name                 form                        OS          OS variant
    ('task_command',                ITEM_TASK_COMMAND,      form_CommandTask,           None,       None        ),
    ('task_lua',                    ITEM_TASK_LUA,          form_LuaScriptTask,         None,       None        ),
    # ...

    ('cond_command',                ITEM_COND_COMMAND,      form_CommandCondition,      None,       None        ),
    ('cond_event',                  ITEM_COND_EVENT,        form_EventCondition,        None,       None        ),
    ('cond_idle',                   ITEM_COND_IDLE,         form_IdleCondition,         None,       None        ),
    ('cond_interval',               ITEM_COND_INTERVAL,     form_IntervalCondition,     None,       None        ),
    ('cond_lua',                    ITEM_COND_LUA,          form_LuaScriptCondition,    None,       None        ),
    ('cond_time',                   ITEM_COND_TIME,         form_TimeCondition,         None,       None        ),
    # ...

    ('event_cli',                   ITEM_EVENT_CLI,         form_CommandEvent,          None,       None        ),
    ('event_fschange',              ITEM_EVENT_FSCHANGE,    form_FilesystemChangeEvent, None,       None        ),
    # ...
]


# a dictionary version of the above list
ALL_AVAILABLE_ITEMS_D = { i[0]: (i[1], i[2], i[3], i[4]) for i in ALL_AVAILABLE_ITEMS }


# end.
