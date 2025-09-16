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


# base class for event: all event items will have the same interface thus they
# are derived from this object: the string conversion is provided also as a
# debugging helper; all base methods will have to be invoked **first** by
# derived methods, as they perform base initialization and checks
class Event(object):

    # availability at class level
    available = False

    def __init__(self, t: items.Table | None = None):
        self.type = None
        self.hrtype = None
        if t:
            self.name = t.get("name")
            self.condition = t.get("condition")
            tags = t.get("tags")
            if tags:
                self.tags = dict(tags)
            else:
                self.tags = None
        else:
            self.name = generate_item_name(self)
            self.condition = None
            self.tags = None

    def __str__(self):
        return "[[event]]\n%s" % self.as_table().as_string()

    # the following too is a constructor, that may generate errors: it can be
    # used in a configuration checking function, or by the constructor itself
    # to check the correctness of the configuration file as a side effect
    def __load_checking(
        self, item: items.Table, item_line: int, event_conds: list[str] | None = None
    ) -> None:
        self.type = None
        self.hrtype = None
        name_check = lambda x: is_valid_item_name(x) or is_private_item_name(x)
        if event_conds is None:
            check = name_check
        else:
            check = lambda x: x in event_conds
        tab = CheckedTable(item, item_line)
        self.name = tab.get_str_check("name", check=name_check, mandatory=True)
        self.condition = tab.get_str_check("condition", check=check, mandatory=True)
        self.tags = tab.get_dict("tags")

    # the checking-only function: either returns True or fails
    @classmethod
    def check_in_document(
        cls, name: str, doc: TOMLDocument, event_conds: list[str] | None = None
    ) -> bool:
        dd = TOMLDocumentDescriptor(doc)
        try:
            # the `get_aot()` method returns a list of AOTs, containing a
            # single element if there are any items of this type in the
            # configuration file; if the list is empty, there are no events
            # defined and an `IndexError` is thrown
            li = dd.get_aot("event")[0]
        # the `except` clause should be the following, we don't care though:
        # except InvalidArrayOfTablesError, IndexError:
        except Exception:
            raise ConfigurationError(
                name,
                message="no events found in the configuration",
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
                if tabd.hierarchy == "event":
                    aot = doc.get("event")
                    assert isinstance(aot, items.AoT)
                    tab = aot[tabd.container_position - 1]
                    try:
                        if tab.get("name") == name:
                            elem = tab
                            elemd = tabd
                            break
                    except Exception:
                        raise ConfigurationError(
                            name,
                            message=f"event not found in the configuration",
                        )
        # check that elem and elemd are not None
        assert elem is not None and elemd is not None
        # now build a dummy event table using the checking constructor
        o = cls()
        o.__load_checking(elem, elemd.line_no, event_conds)
        # a `check_tags(elem)` can be provided by specialized items, which
        # returns a list of parameters in the `tags` table which are incorrect;
        # the `check_tags()` method should also check that, when no tags are
        # present (and thus the passed value is None), the absence of tags is
        # expected, which is an unlikely case
        if "check_tags" in cls.__dict__:
            tags = elem.get("tags")
            err = cls.check_tags(tags)  # type: ignore
            if err is not None and len(err) > 0:
                if isinstance(err, str):
                    raise ConfigurationError(
                        name,
                        "tags",
                        elemd.line_no,
                        message=err,
                    )
                else:
                    assert isinstance(err, tuple)
                    error, missing = err
                    error.append("(missing: %s)" % ", ".join(missing))
                    raise ConfigurationError(
                        name,
                        "tags",
                        elemd.line_no,
                        message="the following entries in `tags` are incorrect: %s"
                        % ", ".join(error),
                    )
        # if no exception has been raised, checking was positive
        return True

    @property
    def signature(self) -> str:
        s = "event:%s" % self.type
        if "subtype" in self.__dict__:
            assert isinstance(self.subtype, str)  # type: ignore
            s += ":%s" % self.subtype  # type: ignore
        return s

    @property
    def private(self) -> bool:
        assert isinstance(self.name, str)
        return is_private_item_name(self.name)

    def as_table(self) -> items.Table:
        if not check_not_none(
            self.name,
            self.type,
        ):
            raise ValueError("Invalid Event: mandatory field(s) missing")
        t = table()
        t.append("name", self.name)
        t.append("type", self.type)
        t = append_not_none(t, "condition", self.condition)
        t = append_not_none(t, "tags", self.tags)
        return t


# end.
