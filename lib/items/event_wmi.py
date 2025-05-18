# WMI event item

from lib.i18n.strings import *

from tomlkit import table, items
from ..utility import check_not_none, append_not_none

from .event import Event


# TODO: use a real query
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

    def __init__(self, t: items.Table = None) -> None:
        Event.__init__(self, t)
        self.type = "wmi"
        self.hrtype = ITEM_EVENT_WMI
        if t:
            assert t.get("type") == self.type
            self.query = t.get("query")
        else:
            self.query = DEFAULT_QUERY

    def as_table(self):
        if not check_not_none(
            self.query,
        ):
            raise ValueError("Invalid WMI Event: mandatory field(s) missing")
        t = Event.as_table(self)
        t.append("query", self.query)
        return t
