# command task item

from lib.i18n.strings import *

from tomlkit import table, items
from ..utility import check_not_none, append_not_none

from .task import Task

from os.path import expanduser


# default values for non-optional parameters
DEFAULT_COMMAND = "replace_me"
DEFAULT_STARTUP_PATH = expanduser("~")


# a command based task
class CommandTask(Task):

    # availability at class level
    available = True

    def __init__(self, t: items.Table = None) -> None:
        Task.__init__(self, t)
        self.type = "command"
        self.hrtype = ITEM_TASK_COMMAND
        if t:
            assert t.get("type") == self.type
            self.startup_path = t.get("startup_path")
            self.command = t.get("command")
            self.match_exact = t.get("match_exact", False)
            self.match_regular_expression = t.get("match_regular_expression", False)
            self.success_stdout = t.get("success_stdout")
            self.success_stderr = t.get("success_stderr")
            self.success_status = t.get("success_status")
            self.failure_stdout = t.get("failure_stdout")
            self.failure_stderr = t.get("failure_stderr")
            self.failure_status = t.get("failure_status")
            self.timeout_seconds = t.get("timeout_seconds")
            self.case_sensitive = t.get("case_sensitive", False)
            self.include_environment = t.get("include_environment", True)
            self.set_environment_variables = t.get("set_environment_variables", True)
            command_arguments = t.get("command_arguments")
            if command_arguments:
                self.command_arguments = list(command_arguments)
            else:
                self.command_arguments = []
            environment_variables = t.get("environment_variables")
            if environment_variables:
                self.environment_variables = dict(environment_variables)
            else:
                self.environment_variables = None
        else:
            self.startup_path = DEFAULT_STARTUP_PATH
            self.command = DEFAULT_COMMAND
            self.command_arguments = []
            self.match_exact = False
            self.match_regular_expression = False
            self.success_stdout = None
            self.success_stderr = None
            self.success_status = None
            self.failure_stdout = None
            self.failure_stderr = None
            self.failure_status = None
            self.timeout_seconds = None
            self.case_sensitive = False
            self.include_environment = True
            self.set_environment_variables = True
            self.environment_variables = None

    def as_table(self):
        if not check_not_none(
            self.command,
            self.command_arguments,
            self.startup_path,
        ):
            raise ValueError("Invalid Command Task: mandatory field(s) missing")
        t = Task.as_table(self)
        t.append("startup_path", self.startup_path)
        t.append("command", self.command)
        t.append("command_arguments", self.command_arguments)
        t = append_not_none(t, "match_exact", self.match_exact)
        t = append_not_none(
            t, "match_regular_expression", self.match_regular_expression
        )
        t = append_not_none(t, "success_stdout", self.success_stdout)
        t = append_not_none(t, "success_stderr", self.success_stderr)
        t = append_not_none(t, "success_status", self.success_status)
        t = append_not_none(t, "failure_stdout", self.failure_stdout)
        t = append_not_none(t, "failure_stderr", self.failure_stderr)
        t = append_not_none(t, "failure_status", self.failure_status)
        t = append_not_none(t, "timeout_seconds", self.timeout_seconds)
        t = append_not_none(t, "case_sensitive", self.case_sensitive)
        t = append_not_none(t, "include_environment", self.include_environment)
        t = append_not_none(
            t, "set_environment_variables", self.set_environment_variables
        )
        t = append_not_none(t, "environment_variables", self.environment_variables)
        return t


# end.
