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

import os

from ..utility import (
    get_tempdir,
    get_luadir,
    get_private_item_name_prefix,
)

from ..items import task_lua, cond_lua, cond_interval
from ..toolbox import install_lua


# constants
_MCRT_PERSIST_FILE = ".mcrt_persist"
_MCRT_LOCK_FILE = ".mcrt_persist.lock"
_MCRT_LIBRARY = "_mcrt_lib.lua"

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
_mcrt_InitializationTask.name = _ITEM_PREFIX + "_Initializer"
_mcrt_InitializationTask.script = f"""\
local mcrt = require "{_MCRT_LIBRARY}"
mcrt.initialize()
"""


# return this item
def mcrt_initializer() -> task_lua.LuaScriptTask:
    return _mcrt_InitializationTask


# 2. updater: just adds the verified condition to the persistence file
_mcrt_UpdateTask = task_lua.LuaScriptTask()
_mcrt_UpdateTask.name = _ITEM_PREFIX + "_Updater"
_mcrt_UpdateTask.script = f"""\
local mcrt = require "{_MCRT_LIBRARY}"
mcrt.set_condition_verified(whenever_condition)
"""


# return this item
def mcrt_updater() -> task_lua.LuaScriptTask:
    return _mcrt_UpdateTask


# 3. initialization condition: it is a once-only condition that only is
# verified at the first tick, and runs the initialization task; using a
# zero duration here makes us quite confident that, if the user has not
# edited the configuration file by hand, this will be the first interval
# based condition that will be verified, because the interval condition
# definition form only accepts values strictly above zero, while whenever
# also accepts a zero duration in the configuration (which is in fact the
# way to create a condition that is verified at startup)
_mcrt_InitializationCond = cond_interval.IntervalCondition()
_mcrt_InitializationCond.name = _ITEM_PREFIX + "_Initializer"
_mcrt_InitializationCond.interval_seconds = 0  # that is, at the first tick
_mcrt_InitializationCond.tasks = [_mcrt_InitializationTask.name]


# return this item
def mcrt_initial_condition() -> cond_interval.IntervalCondition:
    return _mcrt_InitializationCond


# 4. the confluence condition creation function uses a template to define a
# new condition for each set of conditions that have to be verified in order
# to let a task group be run: verification depends on the result of the Lua
# function, that must be `true`
_mcrt_CondConfluence_scriptTemplate = f"""\
local mcrt = require "{_MCRT_LIBRARY}"
res = mcrt.check_conditions_verified([[COND_LIST]])
"""


def mcrt_confluence_condition(
    name: str, conditions: list[str]
) -> cond_lua.LuaScriptCondition:
    cond = cond_lua.LuaScriptCondition()
    cond.name = name
    cond.script = _mcrt_CondConfluence_scriptTemplate.replace(
        "[[COND_LIST]]",
        '{"%s"}' % '", "'.join(conditions),
    )
    cond.expected_results = {"res": True}
    cond.tags = {
        "mcrt_confluent_conditions": conditions,
    }
    return cond


# only return interesting elements (this may actually change)
__all__ = [
    "mcrt_initial_condition",
    "mcrt_initializer",
    "mcrt_updater",
    "mcrt_confluence_condition",
    "mcrt_install_lib",
]


# end.
