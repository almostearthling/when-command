# direct command event item

from lib.i18n.strings import *

from tomlkit import table
from lib.utility import check_not_none

from lib.items.event import Event


# a direct command based event
class CommandEvent(Event):

    # availability at class level
    available = False

    def __init__(self, t: table=None) -> None:
        Event.__init__(self, t)
        self.type = 'cli'
        self.hrtype = ITEM_EVENT_CLI
        if t:
            assert(t.get('type') == self.type)

    def as_table(self):
        if not check_not_none(
            # nothing to be checked!
        ):
            raise ValueError("Invalid Command Event: mandatory field(s) missing")
        t = Event.as_table(self)
        return t


# end.
