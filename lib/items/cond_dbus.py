# DBus condition item

from lib.i18n.strings import *

import json

from tomlkit import table, items
from ..utility import (
    check_not_none,
    append_not_none,
    toml_list_of_tables,
    toml_script_string,
)

from .cond import Condition


# default values for non-optional parameters
DEFAULT_BUS = ":session"
DEFAULT_SERVICE = "org.gnome.Settings"
DEFAULT_OBJECT_PATH = "/org/gnome/Settings"
DEFAULT_INTERFACE = "org.gtk.Actions"
DEFAULT_METHOD = "List"


# a DBus inspection based condition
class DBusCondition(Condition):

    # availability at class level
    available = False

    def __init__(self, t: items.Table = None) -> None:
        Condition.__init__(self, t)
        self.type = "dbus"
        self.hrtype = ITEM_COND_DBUS
        if t:
            assert t.get("type") == self.type
            self.check_after = t.get("check_after")
            self.recur_after_failed_check = t.get("recur_after_failed_check")
            self.bus = t.get("bus")
            self.service = t.get("service")
            self.object_path = t.get("object_path")
            self.interface = t.get("interface")
            self.method = t.get("method")
            self.parameter_call = t.get("parameter_call")
            self.parameter_check_all = t.get("parameter_check_all", False)
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
            self.parameter_check_all = False
            self.parameter_check = None

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
        t = append_not_none(t, "parameter_call", self.parameter_call)
        t = append_not_none(t, "parameter_check_all", self.parameter_check_all)
        # JSON check strings should still be supported, but will eventually go away
        if isinstance(self.parameter_check, str):
            pc = json.loads(self.parameter_check)
            t.append("parameter_check", toml_list_of_tables(pc))
        else:
            t = append_not_none(
                t, "parameter_check", toml_list_of_tables(self.parameter_check)
            )
        return t


# end.
