# multiple conditions to run tasks (aka confluence)
#
# private items that enable the condition "confluence" feature (issue #187),
# that is the possibility for a task to depend on more than one condition.
#
# The idea is to have a persistence file where *all* the conditions that are
# defined as concurring to the triggering of tasks are recorded: this file is
# periodically read, and when all the conditions that concur to a specific
# task (or list/set of tasks) are found in the file, the following happens:
#
# 1. the conditions are _removed_ from the file
# 2. the corresponding task or list/set of tasks is executed
#
# For this purpose, the conditions that concur to tasks will all be bound to
# a single Lua-based task, which writes their name in the file, while multiple
# conditions will be built for each task group to be activated by multiple
# conditions.
#
# The persistence file does not need to be structured, it only has to be read,
# operated on, and written quickly. No concurrent reads or writes should be
# allowed, assuming that one instance of a verified condition cannot concur to
# multiple task groups (this is arbitrary, but cleaner than the opposite), and
# that once a certain set of conditions that concur to a task group is verified
# it has to be atomically removed from the list.
#
# The condition names are "mangled" before being written to the persistence
# file, but the mangling is simple and effective: it only consists of a pair
# of colons around the name. This ensures that no name given to other items
# can conflict with the mangled name, since brackets are not allowed chars
# for item names. This also allow for a quick and precise search without the
# need for special considerations: if the name of a condition is "Cond1", for
# instance, searching for the string ":Cond1:" will match only the presence
# of "Cond1" and not, for instance, "ThatCond1" - which is mangled, instead,
# as ":ThatCond1:". This also eliminates the need for multiple lines, regex
# search, and other complications. The colon character is used because it has
# no special meaning in Lua pattern syntax, so the `string.gsub` function can
# be used.

from ..i18n.strings import *

import os
from tomlkit import items, table

import tkinter as tk
import ttkbootstrap as ttk

from typing import List, Tuple

from ..utility import check_not_none, append_not_none

from ..forms.ui import *

# since a condition is defined, the base form is the one for conditions
from ..forms.cond import form_Condition


from ..utility import (
    get_tempdir,
    get_luadir,
    get_private_item_name_prefix,
)

from ..items import cond, task_lua, cond_lua, cond_interval
from ..toolbox import install_lua


# constants
_MCRT_PERSIST_FILE = ".mcrt_persist"
_MCRT_LOCK_FILE = ".mcrt_persist.lock"
_MCRT_LIBRARY = "_mcrt_lib.lua"

_MCRT_EXTRA_DELAY = 15

_LUA_LIBRARY = """
-- mcrt: multiple conditions to run a task
-- NOTE: internals have a double underscore and will not be directly
-- used in the scripts that require the library

MCRT_LOCK_FILE = [[{MCRT_LOCK_FILE}]]
MCRT_PERSIST_FILE = [[{MCRT_PERSIST_FILE}]]

-- mangle names
function __mangle_name(name)
    return ":" .. name .. ":"
end

-- find whether or not a (mangled) name is present in a string
function __has_name(name, s)
    return string.find(s, mcrt_mangle_name(name)) ~= nil
end

-- remove a name from a string
function __rm_name(name, s)
    return string.gsub(s, __mangle_name(name), "")
end

-- add a name to a string
function __add_name(name, s)
    return s .. __mangle_name(name)
end


-- test if a file exists
function __file_exists(file)
  local f = io.open(file, "rb")
  if f then f:close() end
  return f ~= nil
end

-- wait for the lock file to disappear: unfortunately stock Lua has no
-- sleep() function, so we do busy wait here hoping that it will never be
-- useful and that the lock would last possibly a bunch of usecs at most
function __wait_lock()
    while __file_exists(MCRT_LOCK_FILE) do end
end

-- set and reset the lock
function __set_lock()
    local f = io.open(MCRT_LOCK_FILE, "wb")
    f:close()
end

function __reset_lock()
    if __file_exists(MCRT_LOCK_FILE) then
        os.remove(MCRT_LOCK_FILE)
    end
end

-- read the contents of the persistent file, return nil if read failed
function __read_persistent()
    local f = io.open(MCRT_PERSIST_FILE, "r")
    local s = nil
    if f then
        s = f:read("*all")
        f:close()
    end
    return s
end

-- write the specified contents to the persistent file, truncate the file
-- on null content, which is useful for initialization
function __write_persistent(content)
    local f = io.open(MCRT_PERSIST_FILE, "w")
    if content ~= nil then
        f:write(content)
    end
    f:close()
end


-- actual library functions

-- initialize the persistent file
function initialize()
    __wait_lock()
    __set_lock()
    __write_persistent(nil)
    __reset_lock()
end

-- set the condition bearing the provided name to verified
function set_condition_verified(cond_name)
    __wait_lock()
    __set_lock()
    local persistent = __read_persistent()
    if persistent ~= nil then
        if !__has_name(cond_name, persistent) then
            persistent = __add_name(cond_name, persistent)
        end
    else
        persistent = __add_name(cond_name, "")
    end
    __write_persistent(persistent)
    __reset_lock()
end

-- check whether the provided conditions are all verified, and if so remove
-- their names prior to returning true; otherwise return false
function check_conditions_verified(cond_names)
    local res = true
    __wait_lock()
    __set_lock()
    local persistent = __read_persistent()
    for _, name in ipairs(cond_names) do
        if !__has_name(name, persistent) then
            res = false
            break
        end
    end
    if res then
        for _, name in ipairs(cond_names) do
            persistent = __rm_name(name, persistent)
        end
        __write_persistent(persistent)
    end
    __reset_lock()
    return res
end

-- end.
"""


# this is the prefix for all of our item names
_ITEM_PREFIX = get_private_item_name_prefix() + "_MCRT_"

# specific names, local to this module
_TASK_INITIALIZER = _ITEM_PREFIX + "Initializer"
_TASK_UPDATER = _ITEM_PREFIX + "Updater"
_COND_INITIALIZER = _ITEM_PREFIX + "Initializer"

# the template for the confluence condition Lua script
_MCRT_COND_CONFLUENCE_SCRIPT_TEMPLATE = f"""\
local mcrt = require "{_MCRT_LIBRARY}"
res = mcrt.check_conditions_verified([[COND_LIST]])
"""


# the persistence file is the file that contains the list of conditions that
# concur to task triggering which have been successfully checked
def _mcrt_persist_file():
    return os.path.join(get_tempdir(), _MCRT_PERSIST_FILE)


# the lock file is checked when trying to access the persistence file: no other
# access (including read-only access) will be performed when the lock file is
# present, which indicates a current access
def _mcrt_lock_file():
    return os.path.join(get_tempdir(), _MCRT_LOCK_FILE)


# utility to install the Lua library: it also reserves the library file name
# so that it is not overwritten by the user in case he decides to install
# a Lua library of choice
def mcrt_install_lib():
    s = os.path.join(get_luadir(), _MCRT_LIBRARY)
    if not os.path.exists(s):
        lua_library = _LUA_LIBRARY.format(
            MCRT_LOCK_FILE=_mcrt_lock_file(),
            MCRT_PERSIST_FILE=_mcrt_persist_file(),
        )
        with open(s, "w") as f:
            f.write(lua_library)
    install_lua.reserve_lua(_MCRT_LIBRARY)


# the following items are the specific ones that implement the confluence

# 1. initialization task: resets the persistence file; the reason why we want
# this to be performed by the Lua interpreter instead of the GUI application,
# is that in this way the MCRT system is initialized even when used with
# another frontend
_mcrt_InitializationTask = task_lua.LuaScriptTask()
_mcrt_InitializationTask.name = _TASK_INITIALIZER
_mcrt_InitializationTask.script = f"""\
local mcrt = require "{_MCRT_LIBRARY}"
mcrt.initialize()
"""


# return this item and its name
def mcrt_initializer() -> task_lua.LuaScriptTask:
    return _mcrt_InitializationTask

def mcrt_initializer_name() -> str:
    return _TASK_INITIALIZER


# 2. updater: just adds the verified condition to the persistence file
_mcrt_UpdateTask = task_lua.LuaScriptTask()
_mcrt_UpdateTask.name = _TASK_UPDATER
_mcrt_UpdateTask.script = f"""\
local mcrt = require "{_MCRT_LIBRARY}"
mcrt.set_condition_verified(whenever_condition)
"""


# return this item and its name
def mcrt_updater() -> task_lua.LuaScriptTask:
    return _mcrt_UpdateTask

def mcrt_updater_name() -> str:
    return _TASK_UPDATER


# 3. initialization condition: it is a once-only condition that only is
# verified at the first tick, and runs the initialization task; using a
# zero duration here makes us quite confident that, if the user has not
# edited the configuration file by hand, this will be the first interval
# based condition that will be verified, because the interval condition
# definition form only accepts values strictly above zero, while whenever
# also accepts a zero duration in the configuration (which is in fact the
# way to create a condition that is verified at startup)
_mcrt_InitializationCond = cond_interval.IntervalCondition()
_mcrt_InitializationCond.name = _COND_INITIALIZER
_mcrt_InitializationCond.interval_seconds = 0  # that is, at the first tick
_mcrt_InitializationCond.tasks = [_mcrt_InitializationTask.name]


# return this item and its name
def mcrt_initial_condition() -> cond_interval.IntervalCondition:
    return _mcrt_InitializationCond

def mcrt_initial_condition_name() -> str:
    return _COND_INITIALIZER


# 4. confluence condition: uses the script template defined above; we
# can implement this type of condition as an "extra" condition anyway, so
# we define an item and a form for it exactly in the same way: the only
# difference is that the item is forced into the available ones and not
# dynamically loaded from the `extra` module folder
class ConfluenceCondition(cond_lua.LuaScriptCondition):

    # availability at class level: these variables *MUST* be set for all items
    item_type = "lua"
    item_subtype = "mcrt_confluence"
    item_hrtype = ITEM_COND_MCRT
    available = True

    def __init__(self, t: items.Table | None = None):
        self.type = self.item_type
        self.subtype = self.item_subtype
        self.hrtype = self.item_hrtype
        if t:
            assert t.get("type") == self.type
            self.tags = t.get("tags", table())
            assert isinstance(self.tags, items.Table)
            assert self.tags.get("subtype") == self.subtype
        else:
            self.tags = table()
            self.tags.append("subtype", self.subtype)
            self.tags.append("mcrt_confluent_conditions", list())
        self.updateitem()

    def updateitem(self):
        confluent_conditions = self.tags.get("mcrt_confluent_conditions", list())
        self.script = _MCRT_COND_CONFLUENCE_SCRIPT_TEMPLATE.replace(
            "[[COND_LIST]]",
            '{"%s"}' % '", "'.join(confluent_conditions),
        )
        self.expected_results = {"res": True}
        self.check_after = _MCRT_EXTRA_DELAY  # for now keep it fixed to 15 seconds
        self.recur_after_failed_check = True

    @classmethod
    def check_tags(cls, tags):
        missing = []
        errors = []
        confluent_conditions = tags.get("mcrt_confluent_conditions")
        if confluent_conditions is None:
            missing.append("mcrt_confluent_conditions")
        elif (
            not isinstance(confluent_conditions, list)
            or not len(confluent_conditions) > 1
            or any(not isinstance(x, str) for x in confluent_conditions)
        ):
            errors.append("mcrt_confluent_conditions")
        if errors or missing:
            return (errors, missing)
        return None


# TODO: this form should disable the possibility to be confluent
class form_ConfluenceCondition(form_Condition):

    # note that the available conditions should be filtered, the provided
    # names must correspond to conditions that activate confluence: this
    # module provides a helper to distinguish them from others
    def __init__(self, tasks_available, conds_available, item=None):
        # check that item is the expected one for safety, build one by default
        if item:
            assert isinstance(item, ConfluenceCondition)
        else:
            item = ConfluenceCondition()
        super().__init__(UI_TITLE_MCRTCOND, tasks_available, item)

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # copy the list of conditions, since we have to manipulate it: remove
        # the conditions that are already in the activating lists and sort
        # the left ones for readability in the combo box; note that the items
        # that are not present in the available list are probably leftovers
        # from a manual edit of the configuration file, so they should be
        # discarded if found
        self._conds_available = conds_available.copy()
        self._conds_activating = item.tags.get("mcrt_confluent_conditions") or list()
        for cond in self._conds_activating.copy():
            if cond in self._conds_available:
                self._conds_available.remove(cond)
            else:
                self._conds_activating.remove(cond)
        self._conds_available.sort()

        # ...

        # always update the form at the end of initialization
        self._updateform()

    # update the form with the specific parameters (usually in the `tags`)
    def _updateform(self) -> None:
        self.data_set("parameter1", self._item.tags.get("parameter1"))  # type: ignore
        return super()._updateform()

    # update the item from the form elements (usually update `tags`)
    def _updatedata(self) -> None:
        self._item.tags["parameter1"] = self.data_get("parameter1")  # type: ignore
        self._item.updateitem()  # type: ignore
        return super()._updatedata()


# check whether a condition is confluent
def is_mcrt_confluent_cond(c: cond.Condition) -> bool:
    if c.tasks is not None and len(c.tasks) == 1:
        return c.tasks[0] == _TASK_UPDATER
    return False

# check whether a condition implements confluence
def is_mcrt_confluence_cond(c: cond.Condition) -> bool:
    return isinstance(c, ConfluenceCondition)


# only return interesting symbols
__all__ = [
    "mcrt_initial_condition",
    "mcrt_initial_condition_name",
    "mcrt_initializer",
    "mcrt_initializer_name",
    "mcrt_updater",
    "mcrt_updater_name",
    "is_mcrt_confluent_cond",
    "is_mcrt_confluence_cond",
    "mcrt_install_lib",
    "ConfluenceCondition",
]


# end.
