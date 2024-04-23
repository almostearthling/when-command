# Lua condition item

from lib.i18n.strings import *

from tomlkit import items
from lib.utility import check_not_none, append_not_none

from lib.items.cond import Condition


# default values for non-optional parameters
DEFAULT_LUASCRIPT = "-- write your Lua script here"


# a Lua script based condition
class LuaScriptCondition(Condition):

    def __init__(self, t: items.Table=None) -> None:
        Condition.__init__(self, t)
        self.type = 'lua'
        self.hrtype = ITEM_COND_LUA
        if t:
            assert(t.get('type') == self.type)
            self.check_after = t.get('check_after')
            self.script = t.get('script')
            self.expect_all = t.get('expect_all', False)
            expected_results = t.get('expected_results')
            if expected_results:
                self.expected_results = dict(expected_results)
            else:
                self.expected_results = {}
        else:
            self.script = DEFAULT_LUASCRIPT
            self.check_after = None
            self.expect_all = None
            self.expected_results = None

    def as_table(self):
        if not check_not_none(
            self.script,
        ):
            raise ValueError("Invalid Lua Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        t = append_not_none(t, 'check_after', self.check_after)
        t.append('script', self.script)
        t = append_not_none(t, 'expect_all', self.expect_all)
        t = append_not_none(t, 'expected_results', self.expected_results)
        return t


# end.
