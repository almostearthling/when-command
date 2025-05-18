# interval condition item

from lib.i18n.strings import *

from tomlkit import table, items
from ..utility import check_not_none, append_not_none

from .cond import Condition


# default values for non-optional parameters
DEFAULT_INTERVAL_SECONDS = 120


# an interval based condition
class IntervalCondition(Condition):

    # availability at class level
    available = True

    def __init__(self, t: items.Table = None) -> None:
        Condition.__init__(self, t)
        self.type = "interval"
        self.hrtype = ITEM_COND_INTERVAL
        if t:
            self.interval_seconds = t.get("interval_seconds")
        else:
            self.interval_seconds = DEFAULT_INTERVAL_SECONDS

    def as_table(self):
        if not check_not_none(
            self.interval_seconds,
        ):
            raise ValueError("Invalid Interval Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        t = append_not_none(t, "interval_seconds", self.interval_seconds)
        return t


# end.
