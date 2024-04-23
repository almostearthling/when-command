# task items
#
# task items can be of two types:
# - command tasks
# - Lua script tasks
# as per whenever documentation.

from tomlkit import items, table
from lib.utility import check_not_none, generate_item_name


# base class for tasks: all task items will have the same interface thus they
# are derived from this object: the string conversion is provided also as a
# debugging helper; all base methods will have to be invoked **first** by
# derived methods, as they perform base initialization and checks
class Task(object):

    def __init__(self, t: items.Table=None) -> None:
        self.type = None
        self.hrtype = None
        if t:
            self.name = t.get('name')
        else:
            self.name = generate_item_name(self)

    def __str__(self):
        return "[[task]]\n%s" % self.as_table().as_string()

    def as_table(self):
        if not check_not_none(
            self.name,
            self.type,
        ):
            raise ValueError("Invalid Task: mandatory field(s) missing")
        t = table()
        t.append('name', self.name)
        t.append('type', self.type)
        return t


# end.
