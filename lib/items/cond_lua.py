# Lua condition item

from lib.i18n.strings import *

import re
import os

from tomlkit import items
from ..utility import check_not_none, append_not_none, toml_script_string

from .cond import Condition
from .itemhelp import CheckedTable


# default values for non-optional parameters
DEFAULT_LUASCRIPT = "-- write your Lua script here"

# regular expressions
LUA_VAR_PATTERN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


# a Lua script based condition
class LuaScriptCondition(Condition):

    # availability at class level
    available = True

    def __init__(self, t: items.Table | None = None):
        Condition.__init__(self, t)
        self.type = "lua"
        self.hrtype = ITEM_COND_LUA
        if t:
            assert t.get("type") == self.type
            self.check_after = t.get("check_after")
            self.recur_after_failed_check = t.get("recur_after_failed_check")
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
            self.check_after = None
            self.recur_after_failed_check = None
            self.expect_all = None
            self.expected_results = None
            self.variables_to_set = None
            self.init_script_path = None

    def load_checking(
        self, item: items.Table, item_line: int, tasks: list[str] | None = None
    ) -> None:
        super().load_checking(item, item_line, tasks)
        self.type = "lua"
        self.hrtype = ITEM_COND_LUA
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        self.check_after = tab.get_int_between("check_after", 1)
        self.recur_after_failed_check = tab.get_bool("recur_after_failed_check")
        # hard to check that it is a real Lua script, so we just get a string
        self.script = tab.get_str("script", mandatory=True)
        self.expect_all = tab.get_bool("expect_all")
        self.init_script_path = tab.get_str_check(
            "init_script_path", check=os.path.isfile
        )
        self.variables_to_set = tab.get_dict_check_keys_re(
            "variables_to_set", LUA_VAR_PATTERN
        )
        self.expected_results = tab.get_dict_check_keys_re(
            "expected_results", LUA_VAR_PATTERN
        )

    def as_table(self):
        if not check_not_none(
            self.script,
        ):
            raise ValueError("Invalid Lua Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        t = append_not_none(t, "check_after", self.check_after)
        t = append_not_none(
            t, "recur_after_failed_check", self.recur_after_failed_check
        )
        t.append("script", toml_script_string(self.script))
        t = append_not_none(t, "expect_all", self.expect_all)
        t = append_not_none(t, "variables_to_set", self.variables_to_set)
        t = append_not_none(t, "expected_results", self.expected_results)
        t = append_not_none(t, "init_script_path", self.init_script_path)
        return t


# end.
