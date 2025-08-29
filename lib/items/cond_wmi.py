# WMI condition item

from lib.i18n.strings import *

from tomlkit import items
from ..utility import (
    check_not_none,
    append_not_none,
    toml_list_of_tables,
    toml_script_string,
)

from .cond import Condition
from .itemhelp import CheckedTable


# default values for non-optional parameters
DEFAULT_QUERY = "SELECT * from Win32_Processor"


# a WMI query based condition
class WMICondition(Condition):

    # availability at class level
    available = False

    def __init__(self, t: items.Table | None = None):
        Condition.__init__(self, t)
        self.type = "wmi"
        self.hrtype = ITEM_COND_WMI
        if t:
            assert t.get("type") == self.type
            self.check_after = t.get("check_after")
            self.recur_after_failed_check = t.get("recur_after_failed_check")
            self.query = t.get("query")
            self.result_check_all = t.get("result_check_all")
            self.result_check = t.get("result_check")
        else:
            self.check_after = None
            self.recur_after_failed_check = None
            self.query = DEFAULT_QUERY
            self.result_check_all = None
            self.result_check = None

    def __load_checking(self, item: items.Table, item_line: int) -> None:
        super().__load_checking(item, item_line)
        self.type = "wmi"
        self.hrtype = ITEM_EVENT_WMI
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        self.check_after = tab.get_int_between("check_after", 1)
        self.recur_after_failed_check = tab.get_bool("recur_after_failed_check")
        # hard to check that it is a real WMI query, so we just get a string
        self.query = tab.get_str("query")
        self.result_check_all = tab.get_bool("result_check_all")
        self.result_check = tab.get_array_of_dict("result_check")

    def as_table(self):
        if not check_not_none(
            self.query,
        ):
            raise ValueError("Invalid WMI Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        t = append_not_none(t, "check_after", self.check_after)
        t = append_not_none(
            t, "recur_after_failed_check", self.recur_after_failed_check
        )
        t.append("query", toml_script_string(self.query))
        t = append_not_none(t, "result_check_all", self.result_check_all)
        t = append_not_none(
            t, "result_check", toml_list_of_tables(self.result_check)
        )
        return t


# end.
