# command condition item

from lib.i18n.strings import *

import re

from tomlkit import items
from ..utility import (
    check_not_none,
    append_not_none,
    toml_list_of_command_args,
    toml_literal,
)

from .cond import Condition
from .itemhelp import CheckedTable

from os.path import expanduser, exists


# default values for non-optional parameters
DEFAULT_COMMAND = "replace_me"
DEFAULT_STARTUP_PATH = expanduser("~")

# regular expressions
ENV_VAR_PATTERN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


# a command based condition
class CommandCondition(Condition):

    # availability at class level
    available = True

    def __init__(self, t: items.Table | None = None):
        Condition.__init__(self, t)
        self.type = "command"
        self.hrtype = ITEM_COND_COMMAND
        if t:
            assert t.get("type") == self.type
            self.check_after = t.get("check_after")
            self.recur_after_failed_check = t.get("recur_after_failed_check")
            self.startup_path = t.get("startup_path")
            self.command = t.get("command")
            self.match_exact = t.get("match_exact")
            self.match_regular_expression = t.get("match_regular_expression")
            self.success_stdout = t.get("success_stdout")
            self.success_stderr = t.get("success_stderr")
            self.success_status = t.get("success_status")
            self.failure_stdout = t.get("failure_stdout")
            self.failure_stderr = t.get("failure_stderr")
            self.failure_status = t.get("failure_status")
            self.timeout_seconds = t.get("timeout_seconds")
            self.case_sensitive = t.get("case_sensitive")
            self.include_environment = t.get("include_environment")
            self.set_environment_variables = t.get("set_environment_variables")
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
            self.check_after = None
            self.recur_after_failed_check = None
            self.startup_path = DEFAULT_STARTUP_PATH
            self.command = DEFAULT_COMMAND
            self.command_arguments = []
            self.match_exact = None
            self.match_regular_expression = None
            self.success_stdout = None
            self.success_stderr = None
            self.success_status = None
            self.failure_stdout = None
            self.failure_stderr = None
            self.failure_status = None
            self.timeout_seconds = None
            self.case_sensitive = None
            self.include_environment = None
            self.set_environment_variables = None
            self.environment_variables = None

    def __load_checking(self, item: items.Table, item_line: int) -> None:
        super().__load_checking(item, item_line)
        self.type = "command"
        self.hrtype = ITEM_COND_COMMAND
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        self.check_after = tab.get_int_between("check_after", 1)
        self.recur_after_failed_check = tab.get_bool("recur_after_failed_check")
        self.startup_path = tab.get_str_check("startup_path", exists, mandatory=True)
        self.command = tab.get_str("command", mandatory=True)
        self.match_exact = tab.get_bool("match_exact")
        self.match_regular_expression = tab.get_bool("match_regular_expression")
        self.success_stdout = tab.get_str("success_stdout")
        self.success_stderr = tab.get_str("success_stderr")
        self.success_status = tab.get_int_unsigned("success_status")
        self.failure_stdout = tab.get_str("failure_stdout")
        self.failure_stderr = tab.get_str("failure_stderr")
        self.failure_status = tab.get_int_unsigned("failure_status")
        self.timeout_seconds = tab.get_int_unsigned("timeout_seconds")
        self.case_sensitive = tab.get_bool("case_sensitive")
        self.include_environment = tab.get_bool("include_environment")
        self.set_environment_variables = tab.get_bool("set_environment_variables")
        self.command_arguments = tab.get_list_of_str("command_arguments")
        self.environment_variables = tab.get_dict_check_and_keys_re(
            "environment_variables",
            e_check=lambda x: isinstance(x, str),
            k_re=ENV_VAR_PATTERN,
        )

    def as_table(self):
        if not check_not_none(
            self.command,
            self.command_arguments,
            self.startup_path,
        ):
            raise ValueError("Invalid Command Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        t = append_not_none(t, "check_after", self.check_after)
        t = append_not_none(
            t, "recur_after_failed_check", self.recur_after_failed_check
        )
        t.append("startup_path", toml_literal(self.startup_path))
        t.append("command", toml_literal(self.command))
        t.append("command_arguments", toml_list_of_command_args(self.command_arguments))
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
