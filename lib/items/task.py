# task items
#
# task items can be of two types:
# - command tasks
# - Lua script tasks
# as per whenever documentation.

from tomlkit import table, items
from ..utility import (
    check_not_none,
    append_not_none,
    generate_item_name,
    is_valid_item_name,
    is_private_item_name,
)

from .itemhelp import CheckedTable


# base class for tasks: all task items will have the same interface thus they
# are derived from this object: the string conversion is provided also as a
# debugging helper; all base methods will have to be invoked **first** by
# derived methods, as they perform base initialization and checks
class Task(object):

    # availability at class level
    available = False

    def __init__(self, t: items.Table | None = None):
        self.type = None
        self.hrtype = None
        if t:
            self.name = t.get("name")
            tags = t.get("tags")
            if tags:
                self.tags = dict(tags)
            else:
                self.tags = None
        else:
            self.name = generate_item_name(self)
            self.tags = None

    def __str__(self):
        return "[[task]]\n%s" % self.as_table().as_string()

    # the following too is a constructor, that may generate errors: it can be
    # used in a configuration checking function, or by the constructor itself
    # to check the correctness of the configuration file as a side effect
    def __load_checking(self, item: items.Table, item_line: int) -> None:
        self.type = None
        self.hrtype = None
        tab = CheckedTable(item, item_line)
        self.name = tab.get_str_check("name", check=is_valid_item_name)
        self.tags = tab.get_dict("tags")

    @property
    def signature(self):
        s = "task:%s" % self.type
        if "subtype" in self.__dict__:
            assert isinstance(self.subtype, str)  # type: ignore
            s += ":%s" % self.subtype  # type: ignore
        return s

    @property
    def private(self):
        assert isinstance(self.name, str)
        return is_private_item_name(self.name)

    def as_table(self):
        if not check_not_none(
            self.name,
            self.type,
        ):
            raise ValueError("Invalid Task: mandatory field(s) missing")
        t = table()
        t.append("name", self.name)
        t.append("type", self.type)
        t = append_not_none(t, "tags", self.tags)
        return t


# end.
