# task items
#
# task items can be of two types:
# - command tasks
# - Lua script tasks
# as per whenever documentation.

from tomlkit import table, items, TOMLDocument
from tomlkit_extras import (
    TOMLDocumentDescriptor,
    AoTDescriptor,
    TableDescriptor,
    Hierarchy,
)

from ..utility import (
    check_not_none,
    append_not_none,
    generate_item_name,
    is_valid_item_name,
    is_private_item_name,
)

from .itemhelp import CheckedTable, ConfigurationError


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
        check = lambda x: is_valid_item_name(x) or is_private_item_name(x)
        tab = CheckedTable(item, item_line)
        self.name = tab.get_str_check("name", check=check, mandatory=True)
        self.tags = tab.get_dict("tags")

    # the checking-only function: either returns True or fails
    @classmethod
    def check_in_document(cls, name: str, doc: TOMLDocument) -> bool:
        dd = TOMLDocumentDescriptor(doc)
        try:
            # the `get_aot()` method returns a list of AOTs, containing a
            # single element if there are any items of this type in the
            # configuration file; if the list is empty, there are no events
            # defined and an `IndexError` is thrown
            li = dd.get_aot("task")[0]
        # the `except` clause should be the following, we don't care though:
        # except InvalidArrayOfTablesError, IndexError:
        except Exception:
            raise ConfigurationError(
                name,
                message="no tasks found in the configuration",
            )
        # retrieve the desired table and descriptor (which is only used to find
        # the line number at wich the item starts!!!) and use them to build a
        # dummy item: the checking constructor will raise a ConfigurationError
        # on errors, which will also contain useful information about what went
        # wrong
        elem = None
        elemd = None
        for k in li.tables:
            for tabd in li.tables[k]:
                if tabd.hierarchy == "task":
                    aot = doc.get("task")
                    assert isinstance(aot, items.AoT)
                    # TODO: check that the `container_position` is actually the
                    # index in the array of tables (although 1-based as per docs)
                    tab = aot[tabd.container_position - 1]
                    try:
                        if tab.get("name") == name:
                            elem = tab
                            elemd = tabd
                            break
                    except Exception:
                        raise ConfigurationError(
                            name,
                            message=f"condition not found in the configuration",
                        )
        # check that elem and elemd are not None
        assert elem is not None and elemd is not None
        # now build a dummy event table using the checking constructor
        o = cls()
        o.__load_checking(elem, elemd.line_no)
        # if no exception has been raised, checking was positive
        return True

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
