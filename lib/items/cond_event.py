# evenb condition item

from lib.i18n.strings import *

from tomlkit import items
from lib.utility import check_not_none, append_not_none

from lib.items.cond import Condition


# default values for non-optional parameters
# (none here)


# an event based condition: this does not support the 'bucket' keyword!
class EventCondition(Condition):

    def __init__(self, t: items.Table=None) -> None:
        Condition.__init__(self, t)
        self.type = 'event'
        self.hrtype = ITEM_COND_EVENT
        if t:
            assert(t.get('type') == self.type)

    def as_table(self):
        if not check_not_none(
            # nothing to be checked!
        ):
            raise ValueError("Invalid Event Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        return t


# end.
