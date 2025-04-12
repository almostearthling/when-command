# DBus event item

from lib.i18n.strings import *

from tomlkit import table
from ..utility import check_not_none, append_not_none

from .event import Event


# default values for non-optional parameters
DEFAULT_BUS = ':session'
DEFAULT_RULE = "type='signal',sender='org.gnome.TypingMonitor',interface='org.gnome.TypingMonitor'"


# a DBus signal based event
class DBusEvent(Event):

    # availability at class level
    available = False

    def __init__(self, t: table=None) -> None:
        Event.__init__(self, t)
        self.type = 'dbus'
        self.hrtype = ITEM_EVENT_DBUS
        if t:
            assert(t.get('type') == self.type)
            self.bus = t.get('bus')
            assert(self.bus in (':session', ':system'))
            self.rule = t.get('rule')
            self.parameter_check_all = t.get('parameter_check_all')
            self.parameter_check = t.get('parameter_check')
        else:
            self.bus = DEFAULT_BUS
            self.rule = DEFAULT_RULE
            self.parameter_check_all = False
            self.parameter_check = None

    def as_table(self):
        if not check_not_none(
            self.bus,
            self.rule,
        ):
            raise ValueError("Invalid DBus Event: mandatory field(s) missing")
        t = Event.as_table(self)
        t.append('bus', self.bus)
        t.append('rule', self.rule)
        t = append_not_none(t, 'parameter_check_all', self.parameter_check_all)
        t = append_not_none(t, 'parameter_check', self.parameter_check)
        return t


# end.
