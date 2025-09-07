# condition items
#
# base condition items can be of the following types:
# - interval conditions
# - time conditions
# - idle session conditions
# - event conditions
# - DBus inspection conditions
# - command conditions
# - Lua script conditions
# as per whenever documentation. However, more types can be derived especially
# by crafting command, event, DBus inspection, and Lua script based conditions
# into more specialized versions. whenever allows a list of strings to be
# stored in the `tags` entry for each item, so that specialized items can be
# created in the configuration file and recognized by the wrapper when the
# configuration is loaded back.

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


# base class for conditions: all condition items will have the same interface
# thus are derived from this object: the string conversion is provided also as
# a debugging helper; all base methods will have to be invoked **first** by
# derived methods, as they perform base initialization and checks
class Condition(object):

    # availability at class level
    available = False

    def __init__(self, t: items.Table | None = None):
        self.type = None
        self.hrtype = None
        if t:
            self.name = t.get("name")
            self.execute_sequence = t.get("execute_sequence")
            self.break_on_failure = t.get("break_on_failure")
            self.break_on_success = t.get("break_on_success")
            self.suspended = t.get("suspended")
            self.recurring = t.get("recurring")
            self.max_tasks_retries = t.get("max_tasks_retries")
            self.tasks = t.get("tasks")
            tags = t.get("tags")
            if tags:
                self.tags = dict(tags)
            else:
                self.tags = None
        else:
            self.name = generate_item_name(self)
            self.recurring = None
            self.max_tasks_retries = None
            self.execute_sequence = None
            self.break_on_failure = None
            self.break_on_success = None
            self.suspended = None
            self.tasks = []
            self.tags = None

    def __str__(self):
        return "[[condition]]\n%s" % self.as_table().as_string()

    # the following too is a constructor, that may generate errors: it can be
    # used in a configuration checking function, or by the constructor itself
    # to check the correctness of the configuration file as a side effect
    def __load_checking(
        self, item: items.Table, item_line: int, tasks: list[str] | None = None
    ) -> None:
        self.type = None
        self.hrtype = None
        tab = CheckedTable(item, item_line)
        self.name = tab.get_str_check("name", check=is_valid_item_name)
        self.execute_sequence = tab.get_bool("execute_sequence")
        self.break_on_failure = tab.get_bool("break_on_failure")
        self.break_on_success = tab.get_bool("break_on_success")
        self.suspended = tab.get_bool("suspended")
        self.recurring = tab.get_bool("recurring")
        self.max_tasks_retries = tab.get_int_between("max_tasks_retries", -1)
        if tasks is None:
            check = is_valid_item_name
        else:
            check = lambda x: x in tasks
        self.tasks = tab.get_list_of_str_check("tasks", check=check)
        self.tags = tab.get_dict("tags")

    # the checking-only function: either returns True or fails
    # FIXME: this function cannot be used now, and is committed only
    # for synchronization reasons
    @classmethod
    def check_in_document(cls, name: str, doc: TOMLDocument, tasks=None) -> bool:
        dd = TOMLDocumentDescriptor(doc)
        try:
            # the `get_aot()` method returns a list of AOTs, containing a
            # single element if there are any items of this type in the
            # configuration file; if the list is empty, there are no events
            # defined and an `IndexError` is thrown
            li = dd.get_aot("condition")[0]
        # the `except` clause should be the following, we don't care though:
        # except InvalidArrayOfTablesError, IndexError:
        except Exception:
            raise ConfigurationError(
                name,
                message="no conditions found in the configuration",
            )
        # retrieve the desired table and descriptor (which is only used to find
        # the line number at wich the item starts!!!) and use them to build a
        # dummy item: the checking constructor will raise a ConfigurationError
        # on errors, which will also contain useful information about what went
        # wrong
        elem = None
        elemd = None
        print ("@@@@@@@@@@@@@@", repr(li.tables))
        for k in li.tables:
            for tabd in li.tables[k]:
                aot = doc.get("condition")
                assert isinstance(aot, items.AoT)
                # TODO: check that the `container_position` is actually the
                # index in the array of tables (although 1-based as per docs)
                print(">>>>>>>>>>>>>>>>", repr(tabd))
                # tab = aot[tabd.container_position - 1]
                tab = aot[0]
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
        o.__load_checking(elem, elemd.line_no, tasks)
        # if no exception has been raised, checking was positive
        return True

    @property
    def signature(self):
        s = "cond:%s" % self.type
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
            raise ValueError("Invalid Condition: mandatory field(s) missing")
        t = table()
        t.append("name", self.name)
        t.append("type", self.type)
        t.append("tasks", self.tasks)
        t = append_not_none(t, "recurring", self.recurring)
        t = append_not_none(t, "max_tasks_retries", self.max_tasks_retries)
        t = append_not_none(t, "execute_sequence", self.execute_sequence)
        t = append_not_none(t, "break_on_failure", self.break_on_failure)
        t = append_not_none(t, "break_on_success", self.break_on_success)
        t = append_not_none(t, "suspended", self.suspended)
        t = append_not_none(t, "tags", self.tags)
        return t


# end.
