# filesystem monitor event item

from lib.i18n.strings import *

from tomlkit import table
from ..utility import check_not_none, append_not_none

from .event import Event

from os.path import expanduser


# default values for non-optional parameters
DEFAULT_WATCH = [ expanduser('~') ]


# a filesystem change based event (NOTE: `poll_seconds` unsupported for now)
class FilesystemChangeEvent(Event):

    # availability at class level
    available = True

    def __init__(self, t: table=None) -> None:
        Event.__init__(self, t)
        self.type = 'fschange'
        self.hrtype = ITEM_EVENT_FSCHANGE
        if t:
            assert(t.get('type') == self.type)
            self.watch = t.get('watch')
            self.recursive = t.get('recursive')
            # self.poll_seconds = t.get('poll_seconds')
        else:
            self.watch = DEFAULT_WATCH
            self.recursive = None
            # self.poll_seconds = None

    def as_table(self):
        if not check_not_none(
            self.watch,
        ):
            raise ValueError("Invalid File System Change Event: mandatory field(s) missing")
        t = Event.as_table(self)
        t.append('watch', self.watch)
        t = append_not_none(t, 'recursive', self.recursive)
        # t = append_not_none(t, 'poll_seconds', self.poll_seconds)
        return t


# end.
