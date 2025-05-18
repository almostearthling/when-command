# internal task item

from lib.i18n.strings import *

from tomlkit import table, items
from ..utility import check_not_none, append_not_none

from .task import Task


# default values for non-optional parameters
DEFAULT_COMMAND = "reset_conditions"


class InternalCommandTask(Task):

    available = False

    def __init__(self, t: items.Table = None):
        Task.__init__(self, t)
        self.type = "internal"
        self.hrtype = ITEM_TASK_INTERNAL
        if t:
            assert t.get("type") == self.type
            self.command = t.get("command")
        else:
            self.command = DEFAULT_COMMAND

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
