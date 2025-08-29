# idle session condition item

from lib.i18n.strings import *

from tomlkit import items
from ..utility import check_not_none, append_not_none

from .cond import Condition
from .itemhelp import CheckedTable


# default values for non-optional parameters
DEFAULT_IDLE_SECONDS = 600


# an idle session based condition
class IdleCondition(Condition):

    # availability at class level
    available = True

    def __init__(self, t: items.Table | None = None):
        Condition.__init__(self, t)
        self.type = "idle"
        self.hrtype = ITEM_COND_IDLE
        if t:
            assert t.get("type") == self.type
            self.idle_seconds = t.get("idle_seconds")
        else:
            self.idle_seconds = DEFAULT_IDLE_SECONDS

    def __load_checking(self, item: items.Table, item_line: int) -> None:
        super().__load_checking(item, item_line)
        self.type = "interval"
        self.hrtype = ITEM_COND_INTERVAL
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        self.idle_seconds = tab.get_int_between("idle_seconds", 1)

    def as_table(self):
        if not check_not_none(
            self.idle_seconds,
        ):
            raise ValueError("Invalid Idle Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        t = append_not_none(t, "idle_seconds", self.idle_seconds)
        return t


# end.
