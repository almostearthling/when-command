# event items
#
# base event items can be of the following types:
# - DBus based
# - file system changes
# - command line reactions (direct `trigger` command)
# as per whenever documentation. However, more types can be derived mainly by
# using DBus or, if the wrapper can specialize enough, by listening to system
# events and trigger dedicated command line reactions when certain events
# not known to the scheduler occur.

from tomlkit import items, table
from lib.utility import check_not_none, append_not_none, generate_item_name


# base class for event: all event items will have the same interface thus they
# are derived from this object: the string conversion is provided also as a
# debugging helper; all base methods will have to be invoked **first** by
# derived methods, as they perform base initialization and checks
class Event(object):

    def __init__(self, t: items.Table=None) -> None:
        self.type = None
        self.hrtype = None
        if t:
            self.name = t.get('name')
            self.condition = t.get('condition')
        else:
            self.name = generate_item_name(self)
            self.condition = None

    def __str__(self):
        return "[[event]]\n%s" % self.as_table().as_string()

    def as_table(self):
        if not check_not_none(
            self.name,
            self.type,
        ):
            raise ValueError("Invalid Event: mandatory field(s) missing")
        t = table()
        t.append('name', self.name)
        t.append('type', self.type)
        t = append_not_none(t, 'condition', self.condition)
        return t


# end.
