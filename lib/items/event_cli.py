# direct command event item

from lib.i18n.strings import *

from tomlkit import items
from ..utility import check_not_none

from .event import Event
from .itemhelp import CheckedTable


# a direct command based event
class CommandEvent(Event):

    # availability at class level
    available = False

    def __init__(self, t: items.Table | None = None):
        Event.__init__(self, t)
        self.type = "cli"
        self.hrtype = ITEM_EVENT_CLI
        if t:
            assert t.get("type") == self.type

    def __load_checking(self, item: items.Table, item_line: int) -> None:
        super().__load_checking(item, item_line)
        self.type = "cli"
        self.hrtype = ITEM_EVENT_CLI
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type

    def as_table(self):
        if not check_not_none(
            # nothing to be checked!
        ):
            raise ValueError("Invalid Command Event: mandatory field(s) missing")
        t = Event.as_table(self)
        return t


# end.
