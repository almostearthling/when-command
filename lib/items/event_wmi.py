# WMI event item

from lib.i18n.strings import *

from tomlkit import items
from ..utility import check_not_none, toml_script_string

from .event import Event
from .itemhelp import CheckedTable


DEFAULT_QUERY = """\
SELECT * FROM __InstanceCreationEvent
  WITHIN 10
  WHERE TargetInstance ISA 'Win32_Process'
    AND TargetInstance.Name = 'Notepad.exe'
"""


# a direct command based event
class WMIEvent(Event):

    # availability at class level
    available = False

    def __init__(self, t: items.Table | None = None):
        Event.__init__(self, t)
        self.type = "wmi"
        self.hrtype = ITEM_EVENT_WMI
        if t:
            assert t.get("type") == self.type
            self.query = t.get("query")
        else:
            self.query = DEFAULT_QUERY

    def __load_checking(self, item: items.Table, item_line: int) -> None:
        super().__load_checking(item, item_line)
        self.type = "wmi"
        self.hrtype = ITEM_EVENT_WMI
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        # hard to check that it is a real WMI query, so we just get a string
        self.query = tab.get_str("query")

    def as_table(self):
        if not check_not_none(
            self.query,
        ):
            raise ValueError("Invalid WMI Event: mandatory field(s) missing")
        t = Event.as_table(self)
        t.append("query", toml_script_string(self.query))
        return t


# end.
