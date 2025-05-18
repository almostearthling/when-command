# idle session condition item

from lib.i18n.strings import *

from tomlkit import table, items
from ..utility import check_not_none, append_not_none

from .cond import Condition


# default values for non-optional parameters
DEFAULT_IDLE_SECONDS = 600


# an idle session based condition
class IdleCondition(Condition):

    # availability at class level
    available = True

    def __init__(self, t: items.Table = None) -> None:
        Condition.__init__(self, t)
        self.type = "idle"
        self.hrtype = ITEM_COND_IDLE
        if t:
            assert t.get("type") == self.type
            self.idle_seconds = t.get("idle_seconds")
        else:
            self.idle_seconds = DEFAULT_IDLE_SECONDS

    def as_table(self):
        if not check_not_none(
            self.idle_seconds,
        ):
            raise ValueError("Invalid Idle Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        t = append_not_none(t, "idle_seconds", self.idle_seconds)
        return t


# end.
