# internal task item

from lib.i18n.strings import *

from tomlkit import items
from ..utility import check_not_none

from .itemhelp import CheckedTable
from .task import Task


# default values for non-optional parameters
DEFAULT_COMMAND = "reset_conditions"


class InternalCommandTask(Task):

    available = False

    def __init__(self, t: items.Table | None = None):
        Task.__init__(self, t)
        self.type = "internal"
        self.hrtype = ITEM_TASK_INTERNAL
        if t:
            assert t.get("type") == self.type
            self.command = t.get("command")
        else:
            self.command = DEFAULT_COMMAND

    def __load_checking(self, item: items.Table, item_line: int) -> None:
        super().__load_checking(item, item_line)
        self.type = "internal"
        self.hrtype = ITEM_TASK_INTERNAL
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        # TODO: maybe we can actually check that it is a real command
        self.command = tab.get_str("command", mandatory=True)

    def as_table(self):
        if not check_not_none(
            self.command,
        ):
            raise ValueError(
                "Invalid Internal Command Task: mandatory field(s) missing"
            )
        t = Task.as_table(self)
        t.append("command", self.command)
        return t


# end.
