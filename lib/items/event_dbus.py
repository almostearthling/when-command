# DBus event item

from lib.i18n.strings import *

import json

from tomlkit import items
from ..utility import (
    check_not_none,
    append_not_none,
    toml_list_of_tables,
)

from .event import Event
from .itemhelp import CheckedTable


# default values for non-optional parameters
DEFAULT_BUS = ":session"
DEFAULT_RULE = (
    "type='signal',sender='org.gnome.TypingMonitor',interface='org.gnome.TypingMonitor'"
)


# a DBus signal based event
class DBusEvent(Event):

    # availability at class level
    available = False

    def __init__(self, t: items.Table | None = None):
        Event.__init__(self, t)
        self.type = "dbus"
        self.hrtype = ITEM_EVENT_DBUS
        if t:
            assert t.get("type") == self.type
            self.bus = t.get("bus")
            assert self.bus in [":session", ":system"]
            self.rule = t.get("rule")
            self.parameter_check_all = t.get("parameter_check_all")
            self.parameter_check = t.get("parameter_check")
        else:
            self.bus = DEFAULT_BUS
            self.rule = DEFAULT_RULE
            self.parameter_check_all = None
            self.parameter_check = None

    def __load_checking(self, item: items.Table, item_line: int) -> None:
        super().__load_checking(item, item_line)
        self.type = "dbus"
        self.hrtype = ITEM_EVENT_DBUS
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        # hard to check that it is a real DBus rule, so we just get a string
        self.bus = tab.get_str_check_in("rule", [":session", ":system"], mandatory=True)
        self.rule = tab.get_str("rule", mandatory=True)
        self.parameter_check_all = tab.get_bool("parameter_check_all")
        self.parameter_check = tab.get_bool("parameter_check")

    def as_table(self):
        if not check_not_none(
            self.bus,
            self.rule,
        ):
            raise ValueError("Invalid DBus Event: mandatory field(s) missing")
        t = Event.as_table(self)
        t.append("bus", self.bus)
        t.append("rule", self.rule)
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
