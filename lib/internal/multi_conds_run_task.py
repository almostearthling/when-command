# multiple conditions to run tasks (aka confluence)
#
# private items that enable the condition "confluence" feature (issue #187),
# that is the possibility for a task to depend on more than one condition.
#
# The idea is to have a persistence store where *all* the conditions that are
# defined as concurring to the triggering of tasks are recorded: this store is
# periodically read, and when all the conditions that concur to a specific
# task (or list/set of tasks) are found in the store, the following happens:
#
# 1. the conditions are _removed_ from the store
# 2. the corresponding task or list/set of tasks is executed
#
# For this purpose, the conditions that concur to tasks will all be bound to
# a single Lua-based task, which writes their name in the store, while multiple
# conditions will be built for each task group to be activated by multiple
# conditions.
#
# The persistence store does not need to be structured, it only has to be read,
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
import ttkbootstrap.constants as ttkc

from typing import List, Tuple

from ..forms.ui import *

# since a condition is defined, the base form is the one for conditions
from ..forms.cond import form_Condition

from ..utility import (
    get_luadir,
    get_lua_initscript,
    get_lua_path,
    get_private_item_name_prefix,
    clean_caption,
)

from ..items import cond, task_lua, cond_lua, cond_interval
from ..toolbox import install_lua


# constants
_MCRT_LOCK = "Confluence_LOCK"
_MCRT_PERSIST = "Confluence_STATE"
_MCRT_LIBRARY = "_mcrt_lib"

_MCRT_EXTRA_DELAY = 15

_LUA_LIBRARY = """\
-- mcrt: multiple conditions to run a task
-- NOTE: internals have a double underscore and will not be directly
-- used in the scripts that require the library


local __MCRT_LOCK = [[{MCRT_SHAREDSTATE_LOCK}]]
local __MCRT_PERSIST = [[{MCRT_SHAREDSTATE_PERSIST}]]


-- the library itself
local mcrt = {}


-- mangle names
local function __mangle_name(name)
    return ":" .. name .. ":"
end

-- find whether or not a (mangled) name is present in a string
local function __has_name(name, s)
    return string.find(s, __mangle_name(name)) ~= nil
end

-- remove a name from a string
local function __rm_name(name, s)
    return string.gsub(s, __mangle_name(name), "")
end

-- add a name to a string
local function __add_name(name, s)
    return s .. __mangle_name(name)
end


-- actual library functions

-- initialization just resets the shared state
function mcrt.initialize()
    if sync.lock(__MCRT_LOCK, 1.0) then
        local ok, msg = pcall(function()
            local sst = {{ }}
            sst.persistent = ""
            sharedstate.save(__MCRT_PERSIST, sst)
        end)
        if not ok then
            log.debug("the following error occurred: " .. (msg or "<unknown>"))
            res = false
        end
        sync.release(__MCRT_LOCK)
        return res
    else
        log.debug("could not acquire shared state for condition confluence")
        return false
    end

-- set the condition bearing the provided name to verified
function mcrt.set_condition_verified(cond_name)
    if sync.lock(__MCRT_LOCK, 1.0) then
        local ok, msg = pcall(function()
            local sst = sharedstate.load(__MCRT_PERSIST)
            local persistent = sst.persistent
            if persistent ~= nil then
                if not __has_name(cond_name, persistent) then
                    persistent = __add_name(cond_name, persistent)
                end
            else
                persistent = __add_name(cond_name, "")
            end
            sst.persistent = persistent
            sharedstate.save(__MCRT_PERSIST, sst)
        end)
        if not ok then
            log.debug("the following error occurred: " .. (msg or "<unknown>"))
            res = false
        end
        sync.release(__MCRT_LOCK)
        return res
    else
        log.debug("could not acquire shared state for condition confluence")
        return false
    end
end

-- check whether the provided conditions are all verified, and if so remove
-- their names prior to returning true; otherwise return false
function mcrt.check_conditions_verified(cond_names)
    if sync.lock(__MCRT_LOCK, 1.0) then
        res = true
        local ok, msg = pcall(function()
            local sst = sharedstate.load(__MCRT_PERSIST)
            local persistent = sst.persistent
            if persistent ~= nil then
                for _, name in ipairs(cond_names) do
                    if not __has_name(name, persistent) then
                        res = false
                        break
                    end
                end
                if res then
                    for _, name in ipairs(cond_names) do
                        persistent = __rm_name(name, persistent)
                    end
                    sst.persistent = persistent
                    sharedstate.save(__MCRT_PERSIST, sst)
                end
            else
                res = false
            end
        end)
        if not ok then
            log.debug("the following error occurred: " .. (msg or "<unknown>"))
            res = false
        end
        sync.release(__MCRT_LOCK)
        return res
    else
        log.debug("could not acquire shared state for condition confluence")
        return false
    end
end

-- return the library table
return mcrt


-- end.
"""


# this is the prefix for all of our item names
_ITEM_PREFIX = get_private_item_name_prefix() + "MCRT_"

# specific names, local to this module
_TASK_INITIALIZER = _ITEM_PREFIX + "Initializer"
_TASK_UPDATER = _ITEM_PREFIX + "Updater"
_COND_INITIALIZER = _ITEM_PREFIX + "Initializer"

# the template for the confluence condition Lua script
_MCRT_COND_CONFLUENCE_SCRIPT_TEMPLATE = f"""
    local mcrt = require("{_MCRT_LIBRARY}")
    res = mcrt.check_conditions_verified([[COND_LIST]])
"""


# utility to install the Lua library: it also reserves the library file name
# so that it is not overwritten by the user in case he decides to install
# a Lua library of choice
def install_lib():
    libfilename = f"{_MCRT_LIBRARY}.lua"
    s = os.path.join(get_luadir(), libfilename)
    if not os.path.exists(s):
        lua_library = _LUA_LIBRARY.format(
            "{}",  # this replaces the brackets!
            MCRT_SHAREDSTATE_LOCK=_ITEM_PREFIX + _MCRT_LOCK,
            MCRT_PERSIST_FILE=_ITEM_PREFIX + _MCRT_PERSIST,
        )
        with open(s, "w") as f:
            f.write(lua_library)
    install_lua.reserve_lua(libfilename)


# the following items are the specific ones that implement the confluence


# 1. initialization task: resets the persistence file; the reason why we want
# this to be performed by the Lua interpreter instead of the GUI application,
# is that in this way the MCRT system is initialized even when used with
# another frontend
def initializer() -> task_lua.LuaScriptTask:
    task = task_lua.LuaScriptTask()
    task.name = _TASK_INITIALIZER
    task.variables_to_set = {"LUA_PATH": get_lua_path()}
    task.init_script_path = get_lua_initscript()
    task.script = f"""
    local mcrt = require("{_MCRT_LIBRARY}")
    mcrt.initialize()
    """
    return task


def initializer_name() -> str:
    return _TASK_INITIALIZER


# 2. updater: just adds the verified condition to the persistence file
def updater() -> task_lua.LuaScriptTask:
    task = task_lua.LuaScriptTask()
    task.name = _TASK_UPDATER
    task.variables_to_set = {"LUA_PATH": get_lua_path()}
    task.init_script_path = get_lua_initscript()
    task.script = f"""
    local mcrt = require("{_MCRT_LIBRARY}")
    mcrt.set_condition_verified(whenever_condition)
    """
    return task


def updater_name() -> str:
    return _TASK_UPDATER


# 3. initialization condition: it is a once-only condition that only is
# verified at the first tick, and runs the initialization task; using a
# zero duration here makes us quite confident that, if the user has not
# edited the configuration file by hand, this will be the first interval
# based condition that will be verified, because the interval condition
# definition form only accepts values strictly above zero, while whenever
# also accepts a zero duration in the configuration (which is in fact the
# way to create a condition that is verified at startup)
def initial_condition() -> cond_interval.IntervalCondition:
    cond = cond_interval.IntervalCondition()
    cond.name = _COND_INITIALIZER
    cond.interval_seconds = 0  # that is, at the first tick
    cond.tasks = [_TASK_INITIALIZER]
    return cond


def initial_condition_name() -> str:
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
        # first initialize the base class
        cond_lua.LuaScriptCondition.__init__(self, t)

        # then set type (same as base), subtype and human readable name
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
        self.variables_to_set = {"LUA_PATH": get_lua_path()}
        self.init_script_path = get_lua_initscript()
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
    def __init__(self, tasks_available, item=None):
        # check that item is the expected one for safety, build one by default
        if item:
            assert isinstance(item, ConfluenceCondition)
        else:
            item = ConfluenceCondition()

        self._conds_available = list()
        self._conds_activating = item.tags.get("mcrt_confluent_conditions") or list()
        super().__init__(UI_TITLE_MCRTCOND, tasks_available, item)

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        l_activatingConds = ttk.Label(area, text=UI_FORM_MCRT_ACTIVATINGCONDS_SC)
        sftv_activatingConds = ttk.Frame(area)
        tv_activatingConds = ttk.Treeview(
            sftv_activatingConds,
            columns=("seq", "conditions"),
            show="",
            displaycolumns=(1,),
            height=5,
            bootstyle=ttkc.SECONDARY,
        )
        sb_activatingConds = ttk.Scrollbar(
            sftv_activatingConds, orient=tk.VERTICAL, command=tv_activatingConds.yview
        )
        tv_activatingConds.configure(yscrollcommand=sb_activatingConds.set)
        tv_activatingConds.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_activatingConds.pack(side=tk.RIGHT, fill=tk.Y)

        sf_condChoose = ttk.Frame(area)
        l_chooseCond = ttk.Label(sf_condChoose, text=UI_FORM_COND_SC)
        cb_chooseCond = ttk.Combobox(
            sf_condChoose, values=self._conds_available, state="readonly"
        )
        b_addCond = ttk.Button(
            sf_condChoose,
            text=UI_ADD,
            width=BUTTON_STANDARD_WIDTH,
            command=self.add_cond,
        )
        b_delCond = ttk.Button(
            sf_condChoose,
            text=UI_DEL,
            width=BUTTON_STANDARD_WIDTH,
            command=self.del_cond,
        )

        # choose condition section: arrange items
        l_chooseCond.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cb_chooseCond.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_addCond.grid(row=0, column=2, sticky=tk.E, padx=PAD, pady=PAD)
        b_delCond.grid(row=0, column=3, sticky=tk.E, padx=PAD, pady=PAD)

        # notebook area: arrange items
        l_activatingConds.grid(row=0, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        sftv_activatingConds.grid(row=1, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        sf_condChoose.grid(row=2, column=0, sticky=tk.EW, padx=PAD, pady=PAD)

        # expand appropriate sections
        sf_condChoose.columnconfigure(1, weight=1)
        area.rowconfigure(1, weight=1)
        area.columnconfigure(0, weight=1)

        # bind data to widgets
        self.data_bind(
            "cond_selection",
            tv_activatingConds,
            check=lambda _: len(self._conds_activating) > 1,
        )
        self.data_bind("choose_cond", cb_chooseCond, TYPE_STRING)

        # add a check that the chosen conditions should be more than one
        self.add_check_caption(
            "cond_selection", clean_caption(UI_FORM_MCRT_ACTIVATINGCONDS_SC)
        )

        # propagate widgets that need to be accessed
        self._tv_activatingConds = tv_activatingConds
        self._cb_chooseCond = cb_chooseCond

        # always update the form at the end of initialization
        self._updateform()

    def add_cond(self):
        # only add a condition if not present, ignore otherwise
        elem = self.data_get("choose_cond")
        if elem and elem not in self._conds_activating:
            self._conds_activating.append(elem)
        self._updatedata()
        self._updateform()

    def del_cond(self):
        elem = self.data_get("cond_selection")
        if elem:
            idx = int(elem[0])
            del self._conds_activating[idx]
            self._updatedata()
            self._updateform()

    # update the form with the specific parameters (usually in the `tags`)
    def _updateform(self) -> None:
        self._tv_activatingConds.delete(*self._tv_activatingConds.get_children())
        idx = 0
        for cond in self._conds_activating:
            self._tv_activatingConds.insert(
                "", iid="%s-%s" % (idx, cond), values=(idx, cond), index=tk.END
            )
            idx += 1
        return super()._updateform()

    # update the item from the form elements (usually update `tags`)
    def _updatedata(self) -> None:
        assert isinstance(self._item, ConfluenceCondition)
        self._item.tags["mcrt_confluent_conditions"] = self._conds_activating  # type: ignore
        return super()._updatedata()

    # set the list of available conditions, that implement confluence
    def set_available_conditions(self, conds: list[str]) -> None:
        self._conds_available = conds.copy()
        self._conds_available.sort()
        self._cb_chooseCond["values"] = self._conds_available
        for cond in self._conds_activating.copy():
            if cond not in self._conds_available:
                self._conds_activating.remove(cond)
        self._updateform()


# check whether a condition is confluent
def is_confluent_cond(c: cond.Condition) -> bool:
    if c.tasks is not None and len(c.tasks) == 1:
        return c.tasks[0] == _TASK_UPDATER
    return False


# check whether a condition implements confluence
def is_confluence_cond(c: cond.Condition) -> bool:
    return isinstance(c, ConfluenceCondition)


# only return interesting symbols
__all__ = [
    "initial_condition",
    "initial_condition_name",
    "initializer",
    "initializer_name",
    "updater",
    "updater_name",
    "is_confluent_cond",
    "is_confluence_cond",
    "install_lib",
    "ConfluenceCondition",
    "form_ConfluenceCondition",
]


# end.
