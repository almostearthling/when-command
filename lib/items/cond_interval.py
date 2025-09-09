# interval condition item

from lib.i18n.strings import *

from tomlkit import items
from ..utility import check_not_none, append_not_none

from .cond import Condition
from .itemhelp import CheckedTable


# default values for non-optional parameters
DEFAULT_INTERVAL_SECONDS = 120


# an interval based condition
class IntervalCondition(Condition):

    # availability at class level
    available = True

    def __init__(self, t: items.Table | None = None):
        Condition.__init__(self, t)
        self.type = "interval"
        self.hrtype = ITEM_COND_INTERVAL
        if t:
            self.interval_seconds = t.get("interval_seconds")
        else:
            self.interval_seconds = DEFAULT_INTERVAL_SECONDS

    def __load_checking(self, item: items.Table, item_line: int) -> None:
        super().__load_checking(item, item_line)
        self.type = "interval"
        self.hrtype = ITEM_COND_INTERVAL
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        self.interval_seconds = tab.get_int_between("interval_seconds", 1, mandatory=True)

    def as_table(self):
        if not check_not_none(
            self.interval_seconds,
        ):
            raise ValueError("Invalid Interval Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        t = append_not_none(t, "interval_seconds", self.interval_seconds)
        return t


# end.
