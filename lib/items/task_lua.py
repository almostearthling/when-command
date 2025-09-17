# Lua task item

from lib.i18n.strings import *

import re
import os

from tomlkit import items
from ..utility import check_not_none, append_not_none, toml_script_string

from .itemhelp import CheckedTable
from .task import Task


# default values for non-optional parameters
DEFAULT_LUASCRIPT = "-- write your Lua script here"

# regular expressions
LUA_VAR_PATTERN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


# a Lua script based task
class LuaScriptTask(Task):

    # availability at class level
    available = True

    def __init__(self, t: items.Table | None = None):
        Task.__init__(self, t)
        self.type = "lua"
        self.hrtype = ITEM_TASK_LUA
        if t:
            assert t.get("type") == self.type
            self.script = t.get("script")
            self.expect_all = t.get("expect_all")
            self.init_script_path = t.get("init_script_path")
            variables_to_set = t.get("variables_to_set")
            if variables_to_set:
                self.variables_to_set = dict(variables_to_set)
            else:
                self.variables_to_set = None
            expected_results = t.get("expected_results")
            if expected_results:
                self.expected_results = dict(expected_results)
            else:
                self.expected_results = None
        else:
            self.script = DEFAULT_LUASCRIPT
            self.expect_all = None
            self.expected_results = None
            self.variables_to_set = None
            self.init_script_path = None

    def load_checking(self, item: items.Table, item_line: int) -> None:
        super().load_checking(item, item_line)
        self.type = "lua"
        self.hrtype = ITEM_TASK_LUA
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        # hard to check that it is a real Lua script, so we just get a string
        self.script = tab.get_str("script", mandatory=True)
        self.expect_all = tab.get_bool("expect_all")
        self.init_script_path = tab.get_str_check(
            "init_script_path", check=os.path.isfile
        )
        self.variables_to_set = tab.get_list_of_dict_check_keys_re(
            "variables_to_set", LUA_VAR_PATTERN
        )
        self.expected_results = tab.get_list_of_dict_check_keys_re(
            "expected_results", LUA_VAR_PATTERN
        )

    def as_table(self) -> items.Table:
        if not check_not_none(
            self.script,
        ):
            raise ValueError("Invalid Lua Task: mandatory field(s) missing")
        t = Task.as_table(self)
        t.append("script", toml_script_string(self.script))
        t = append_not_none(t, "expect_all", self.expect_all)
        t = append_not_none(t, "variables_to_set", self.variables_to_set)
        t = append_not_none(t, "expected_results", self.expected_results)
        t = append_not_none(t, "init_script_path", self.init_script_path)
        return t


# end.
