# filesystem monitor event item

from lib.i18n.strings import *

from tomlkit import items
from ..utility import check_not_none, append_not_none, toml_list_of_literals

from .event import Event
from .itemhelp import CheckedTable

from os.path import expanduser, exists


# default values for non-optional parameters
DEFAULT_WATCH = [expanduser("~")]


# a filesystem change based event (NOTE: `poll_seconds` unsupported for now)
class FilesystemChangeEvent(Event):

    # availability at class level
    available = True

    def __init__(self, t: items.Table | None = None):
        Event.__init__(self, t)
        self.type = "fschange"
        self.hrtype = ITEM_EVENT_FSCHANGE
        if t:
            assert t.get("type") == self.type
            self.watch = t.get("watch")
            self.recursive = t.get("recursive")
            # self.poll_seconds = t.get('poll_seconds')
        else:
            self.watch = DEFAULT_WATCH
            self.recursive = None
            # self.poll_seconds = None

    def __load_checking(self, item: items.Table, item_line: int) -> None:
        super().__load_checking(item, item_line)
        self.type = "fschange"
        self.hrtype = ITEM_EVENT_FSCHANGE
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        # since `whenever` will complain on non-existing paths to watch
        # `os.path.exists()` is a good checking function for valid paths
        self.watch = tab.get_list_of_str_check("watch", exists)
        self.recursive = tab.get_str("recursive")

    def as_table(self):
        if not check_not_none(
            self.watch,
        ):
            raise ValueError(
                "Invalid File System Change Event: mandatory field(s) missing"
            )
        t = Event.as_table(self)
        t.append("watch", toml_list_of_literals(self.watch))
        t = append_not_none(t, "recursive", self.recursive)
        # t = append_not_none(t, 'poll_seconds', self.poll_seconds)
        return t


# end.
