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

from tomlkit import items, table
from lib.utility import check_not_none, append_not_none, generate_item_name


# base class for conditions: all condition items will have the same interface
# thus are derived from this object: the string conversion is provided also as
# a debugging helper; all base methods will have to be invoked **first** by
# derived methods, as they perform base initialization and checks
class Condition(object):

    # availability at class level
    available = False

    def __init__(self, t: table=None) -> None:
        self.type = None
        self.hrtype = None
        if t:
            self.name = t.get('name')
            self.execute_sequence = t.get('execute_sequence', True)
            self.break_on_failure = t.get('break_on_failure', False)
            self.break_on_success = t.get('break_on_success', False)
            self.suspended = t.get('suspended', False)
            self.recurring = t.get('recurring', False)
            self.max_tasks_retries = t.get('max_tasks_retries', 0)
            self.tasks = t.get('tasks')
            tags = t.get('tags')
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

    def as_table(self):
        if not check_not_none(
            self.name,
            self.type,
        ):
            raise ValueError("Invalid Condition: mandatory field(s) missing")
        t = table()
        t.append('name', self.name)
        t.append('type', self.type)
        t.append('tasks', self.tasks)
        t = append_not_none(t, 'recurring', self.recurring)
        t = append_not_none(t, 'max_tasks_retries', self.max_tasks_retries)
        t = append_not_none(t, 'execute_sequence', self.execute_sequence)
        t = append_not_none(t, 'break_on_failure', self.break_on_failure)
        t = append_not_none(t, 'break_on_success', self.break_on_success)
        t = append_not_none(t, 'suspended', self.suspended)
        t = append_not_none(t, 'tags', self.tags)
        return t


# end.
