# DBus condition item

from lib.i18n.strings import *

import json
import re

from tomlkit import items
from ..utility import (
    check_not_none,
    append_not_none,
    toml_list_of_tables,
    is_dbus_operator,
)

from .cond import Condition
from .itemhelp import CheckedTable


# default values for non-optional parameters
DEFAULT_BUS = ":session"
DEFAULT_SERVICE = "org.gnome.Settings"
DEFAULT_OBJECT_PATH = "/org/gnome/Settings"
DEFAULT_INTERFACE = "org.gtk.Actions"
DEFAULT_METHOD = "List"


# check regular expressions
RE_DBUS_SERVICE_NAME = re.compile(
    r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)+$"
)
RE_DBUS_OBJECT_PATH = re.compile(r"^/([a-zA-Z0-9_]+(/[a-zA-Z0-9_]+)*)?$")
RE_DBUS_INTERFACE_NAME = re.compile(
    r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)+$"
)
RE_DBUS_MEMBER_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
RE_DBUS_ERROR_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)+$")


# a DBus inspection based condition
class DBusCondition(Condition):

    # availability at class level
    available = False

    def __init__(self, t: items.Table | None = None):
        Condition.__init__(self, t)
        self.type = "dbus"
        self.hrtype = ITEM_COND_DBUS
        if t:
            assert t.get("type") == self.type
            self.check_after = t.get("check_after")
            self.recur_after_failed_check = t.get("recur_after_failed_check")
            self.bus = t.get("bus")
            assert self.bus in [":session", ":system"]
            self.service = t.get("service")
            self.object_path = t.get("object_path")
            self.interface = t.get("interface")
            self.method = t.get("method")
            self.parameter_call = t.get("parameter_call")
            self.parameter_check_all = t.get("parameter_check_all")
            self.parameter_check = t.get("parameter_check")
        else:
            self.check_after = None
            self.recur_after_failed_check = None
            self.bus = DEFAULT_BUS
            self.service = DEFAULT_SERVICE
            self.object_path = DEFAULT_OBJECT_PATH
            self.interface = DEFAULT_INTERFACE
            self.method = DEFAULT_METHOD
            self.parameter_call = None
            self.parameter_check_all = None
            self.parameter_check = None

    def load_checking(
        self, item: items.Table, item_line: int, tasks: list[str] | None = None
    ) -> None:
        super().load_checking(item, item_line, tasks)
        self.type = "dbus"
        self.hrtype = ITEM_COND_DBUS
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        self.check_after = tab.get_int_between("check_after", 1)
        self.recur_after_failed_check = tab.get_bool("recur_after_failed_check")
        self.bus = tab.get_str_check_in("rule", [":session", ":system"], mandatory=True)
        self.service = tab.get_str_check_re(
            "service", RE_DBUS_SERVICE_NAME, mandatory=True
        )
        self.object_path = tab.get_str_check_re(
            "object_path", RE_DBUS_OBJECT_PATH, mandatory=True
        )
        self.interface = tab.get_str_check_re(
            "interface", RE_DBUS_INTERFACE_NAME, mandatory=True
        )
        self.method = tab.get_str_check_re(
            "method", RE_DBUS_MEMBER_NAME, mandatory=True
        )

        # as per documentation, `parameter_call` is a list, whse members are
        # either simple values or lists, which can be deeply nested... that
        # is why we need recursion at this point
        def _check_param(x) -> bool:
            if (
                isinstance(x, bool)
                or isinstance(x, int)
                or isinstance(x, float)
                or isinstance(x, str)
            ):
                return True
            elif isinstance(x, list):
                for y in x:
                    if not (
                        isinstance(y, bool)
                        or isinstance(y, int)
                        or isinstance(y, float)
                        or isinstance(y, str)
                    ):
                        return False
            else:
                return False
            return True

        self.parameter_call = tab.get_list_check("parameter_call", _check_param)
        self.parameter_check_all = tab.get_bool("parameter_check_all")

        # these are expressed via a list of inline dictionaries whose
        # elements are fixed, and *must* exist, and have a specific form; we
        # use a dictionary based trick
        def _check_idx(x) -> bool:
            if isinstance(x, int) and x >= 0:
                return True
            elif isinstance(x, list):
                for y in x:
                    if not (isinstance(y, int) and y >= 0) and not isinstance(y, str):
                        return False
                return True
            else:
                return False

        tests = {
            "index": _check_idx,
            "operator": is_dbus_operator,
            "value": lambda x: isinstance(x, (bool, int, float, str)),
        }
        self.parameter_check = tab.get_list_of_dict_check_keys_vs_values(
            "parameter_check", lambda k, v: k in tests and tests[k](v)
        )

    def as_table(self):
        if not check_not_none(
            self.bus,
            self.service,
            self.object_path,
            self.interface,
            self.method,
        ):
            raise ValueError("Invalid DBus Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        t = append_not_none(t, "check_after", self.check_after)
        t = append_not_none(
            t, "recur_after_failed_check", self.recur_after_failed_check
        )
        t.append("bus", self.bus)
        t.append("service", self.service)
        t.append("object_path", self.object_path)
        t.append("interface", self.interface)
        t.append("method", self.method)
        if isinstance(
            self.parameter_call, str
        ):  # this only works with the (unavailable) form
            pc = json.loads(self.parameter_call)
            t.append("parameter_call", toml_list_of_tables(pc))
        else:
            t = append_not_none(t, "parameter_call", self.parameter_call)
        t = append_not_none(t, "parameter_check_all", self.parameter_check_all)
        # JSON check strings should still be supported, but will eventually go away
        if isinstance(
            self.parameter_check, str
        ):  # this only works with the (unavailable) form
            pc = json.loads(self.parameter_check)
            t.append("parameter_check", toml_list_of_tables(pc))
        else:
            t = append_not_none(
                t, "parameter_check", toml_list_of_tables(self.parameter_check)
            )
        return t


# end.
