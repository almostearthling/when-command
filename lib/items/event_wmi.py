# WMI event item

from lib.i18n.strings import *

import re

from tomlkit import items
from ..utility import check_not_none, append_not_none, toml_script_string

from .event import Event
from .itemhelp import CheckedTable


# a regular expression to check a valid WMI namespace
_RE_VALID_WMI_NAMESPACE = re.compile(
    r"^[a-zA-Z_][a-zA-Z0-9_]*(\\[a-zA-Z_][a-zA-Z0-9_]*)+$"
)

# namespace paths must start with "ROOT\" (case insensitive)
_WMI_NAMESPACE_PREFIX = "ROOT\\"


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
            self.namespace = t.get("namespace")
        else:
            self.query = DEFAULT_QUERY
            self.namespace = None

    def load_checking(
        self, item: items.Table, item_line: int, event_conds: list[str] | None = None
    ) -> None:
        super().load_checking(item, item_line, event_conds)
        self.type = "wmi"
        self.hrtype = ITEM_EVENT_WMI
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        # hard to check that it is a real WMI query, so we just get a string
        self.query = tab.get_str("query", mandatory=True)

        # possibly provided namespace path is checked for correctness
        def _is_valid_namespace(x: str) -> bool:
            if isinstance(x, str) and bool(_RE_VALID_WMI_NAMESPACE.match(x)):
                return x.upper().startswith(_WMI_NAMESPACE_PREFIX)
            else:
                return False

        self.namespace = tab.get_str_check("namespace", _is_valid_namespace)

    def as_table(self):
        if not check_not_none(
            self.query,
        ):
            raise ValueError("Invalid WMI Event: mandatory field(s) missing")
        t = Event.as_table(self)
        t = append_not_none(t, "namespace", self.namespace)
        t.append("query", toml_script_string(self.query))
        return t


# end.
