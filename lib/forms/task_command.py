# command task form

import sys
from os.path import normpath

from ..i18n.strings import *

from shlex import split as arg_split, quote

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog

from .ui import *

from ..utility import get_executable_extensions

from .task import form_Task
from ..items.task_command import CommandTask

import re
import os
import shutil


# regular expression for variable name checking
_RE_VALIDNAME = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")


# functions to check existence of commands and directories
def _is_command(s):
    if os.path.exists(s) and os.access(s, os.X_OK):
        return True
    elif shutil.which(s):
        return True
    else:
        return False


def _is_dir(s):
    if os.path.exists(os.path.join(s, ".")):
        return True
    else:
        return False


# specialized task box
class form_CommandTask(form_Task):

    def __init__(self, item=None):
        if item:
            assert isinstance(item, CommandTask)
        else:
            item = CommandTask()
        super().__init__(UI_TITLE_COMMANDTASK, item)

        # form data
        self._envvars = []

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # command section: use a separate area to customize layout
        area_command = ttk.Frame(area)
        l_command = ttk.Label(area_command, text=UI_FORM_COMMAND_SC)
        e_command = ttk.Entry(area_command)
        b_commandBrowse = ttk.Button(
            area_command, text=UI_BROWSE, command=self.browse_command
        )
        l_args = ttk.Label(area_command, text=UI_FORM_ARGS_SC)
        e_args = ttk.Entry(area_command)
        l_startupPath = ttk.Label(area_command, text=UI_FORM_STARTUPPATH_SC)
        e_startupPath = ttk.Entry(area_command)
        b_startupPathBrowse = ttk.Button(
            area_command, text=UI_BROWSE, command=self.browse_startup_path
        )
        sep1 = ttk.Separator(area)

        # arrange widgets in frame
        l_command.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_command.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_commandBrowse.grid(row=0, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        l_args.grid(row=1, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_args.grid(row=1, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        l_startupPath.grid(row=2, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_startupPath.grid(row=2, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_startupPathBrowse.grid(row=2, column=2, sticky=tk.EW, padx=PAD, pady=PAD)

        # environment section: deserves an area to customize layout
        area_vars = ttk.Frame(area)
        l_vars = ttk.Label(area_vars, text=UI_FORM_VARIABLES_SC)
        # build a scrolled frame for the treeview
        sftv_vars = ttk.Frame(area_vars)
        tv_vars = ttk.Treeview(
            sftv_vars, columns=("name", "value"), show="headings", height=7
        )
        tv_vars.heading("name", anchor=tk.W, text=UI_FORM_NAME)
        tv_vars.heading("value", anchor=tk.W, text=UI_FORM_VALUE)
        sb_vars = ttk.Scrollbar(sftv_vars, orient=tk.VERTICAL, command=tv_vars.yview)
        tv_vars.configure(yscrollcommand=sb_vars.set)
        tv_vars.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_vars.pack(side=tk.RIGHT, fill=tk.Y)
        l_varName = ttk.Label(area_vars, text=UI_FORM_VARNAME_SC)
        e_varName = ttk.Entry(area_vars)
        l_varValue = ttk.Label(area_vars, text=UI_FORM_NEWVALUE_SC)
        e_varValue = ttk.Entry(area_vars)
        b_addVar = ttk.Button(
            area_vars, text=UI_UPDATE, width=BUTTON_STANDARD_WIDTH, command=self.add_var
        )
        b_delVar = ttk.Button(
            area_vars, text=UI_DEL, width=BUTTON_STANDARD_WIDTH, command=self.del_var
        )
        sep2 = ttk.Separator(area)

        # environment section: subarea for checkboxes
        area_vars_flags = ttk.Frame(area)
        ck_preserveEnv = ttk.Checkbutton(
            area_vars_flags, text=UI_FORM_PRESERVEENVIRONMENT
        )
        ck_setEnvVars = ttk.Checkbutton(area_vars_flags, text=UI_FORM_SETWENVIRONMENT)

        # environment section: arrange widgets in frame
        l_vars.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=PAD, pady=PAD)
        sftv_vars.grid(
            row=1, column=0, columnspan=4, sticky=tk.NSEW, padx=PAD, pady=PAD
        )
        l_varName.grid(row=2, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        l_varValue.grid(row=2, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        e_varName.grid(row=3, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        e_varValue.grid(row=3, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_addVar.grid(row=3, column=2, sticky=tk.NSEW, padx=PAD, pady=PAD)
        b_delVar.grid(row=3, column=3, sticky=tk.NSEW, padx=PAD, pady=PAD)

        # bind double click to variable recall
        tv_vars.bind("<Double-Button-1>", lambda _: self.recall_var())

        # environment section: arrange widgets in frame
        ck_preserveEnv.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        ck_setEnvVars.grid(row=0, column=1, sticky=tk.W, padx=PAD, pady=PAD)

        # checks section: deserves an area to customize layout
        area_checks = ttk.Frame(area)
        l_checkFor = ttk.Label(area_checks, text=UI_FORM_CHECKFOR_SC)
        cb_checkFor = ttk.Combobox(
            area_checks,
            values=(UI_OUTCOME_NONE, UI_OUTCOME_SUCCESS, UI_OUTCOME_FAILURE),
            state="readonly",
        )
        l_checkWhat = ttk.Label(area_checks, text=UI_FORM_CHECKAGAINST_SC)
        cb_checkWhat = ttk.Combobox(
            area_checks,
            values=(UI_EXIT_CODE, UI_STREAM_STDOUT, UI_STREAM_STDERR),
            state="readonly",
        )
        l_checkValue = ttk.Label(area_checks, text=UI_FORM_TESTVAL_SC)
        e_checkValue = ttk.Entry(area_checks)
        l_timeoutSecs = ttk.Label(area_checks, text=UI_FORM_TIMEOUTSECS_SC)
        e_timeoutSecs = ttk.Entry(area_checks)

        # checks section: arrange widgets in frame
        l_checkFor.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cb_checkFor.grid(row=1, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        l_checkWhat.grid(row=0, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        cb_checkWhat.grid(row=1, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        l_checkValue.grid(row=0, column=2, sticky=tk.W, padx=PAD, pady=PAD)
        e_checkValue.grid(row=1, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        l_timeoutSecs.grid(row=0, column=3, sticky=tk.W, padx=PAD, pady=PAD)
        e_timeoutSecs.grid(row=1, column=3, sticky=tk.EW, padx=PAD, pady=PAD)

        # checks section: subarea for checkboxes
        area_checks_flags = ttk.Frame(area)
        ck_matchExact = ttk.Checkbutton(area_checks_flags, text=UI_FORM_MATCHEXACT)
        ck_caseSensitive = ttk.Checkbutton(
            area_checks_flags, text=UI_FORM_CASESENSITIVE
        )
        ck_matchRegExp = ttk.Checkbutton(area_checks_flags, text=UI_FORM_MATCHREGEXP)

        # checks section: arrange widgets in frame
        ck_matchExact.grid(row=0, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        ck_caseSensitive.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        ck_matchRegExp.grid(row=0, column=2, sticky=tk.EW, padx=PAD, pady=PAD)

        # arrange top items in the grid
        area_command.grid(row=0, column=0, sticky=tk.NSEW)
        sep1.grid(row=1, column=0, sticky=tk.EW, pady=PAD)
        area_vars.grid(row=2, column=0, sticky=tk.NSEW)
        area_vars_flags.grid(row=3, column=0, sticky=tk.NSEW)
        sep2.grid(row=4, column=0, sticky=tk.EW, pady=PAD)
        area_checks.grid(row=5, column=0, sticky=tk.NSEW)
        area_checks_flags.grid(row=6, column=0, sticky=tk.NSEW)

        # expand appropriate sections
        area.rowconfigure(2, weight=1)
        area.columnconfigure(0, weight=1)
        area_command.columnconfigure(1, weight=1)
        area_vars.columnconfigure(0, weight=1)
        area_vars.rowconfigure(1, weight=1)
        area_vars.columnconfigure(1, weight=1)
        area_checks.columnconfigure(2, weight=1)

        # bind data to widgets
        self.data_bind("command", e_command, TYPE_STRING)
        self.data_bind("command_arguments", e_args, TYPE_STRING)
        self.data_bind("startup_path", e_startupPath, TYPE_STRING)
        # the following checks would be optimal, but are actually too strict
        # self.data_bind('command', e_command, TYPE_STRING, _is_command)
        # self.data_bind('startup_path', e_startupPath, TYPE_STRING, _is_dir)
        self.data_bind("include_environment", ck_preserveEnv)
        self.data_bind("set_environment_variables", ck_setEnvVars)
        self.data_bind("envvar_selection", tv_vars)
        self.data_bind(
            "varname",
            e_varName,
            TYPE_STRING,
            lambda x: x == "" or _RE_VALIDNAME.match(x),
        )
        self.data_bind("newvalue", e_varValue, TYPE_STRING)
        self.data_bind("check_for", cb_checkFor, TYPE_STRING)
        self.data_bind("check_what", cb_checkWhat, TYPE_STRING)
        self.data_bind("check_value", e_checkValue, TYPE_STRING)
        self.data_bind("timeout_seconds", e_timeoutSecs, TYPE_INT, lambda x: x >= 0)
        self.data_bind("match_exact", ck_matchExact)
        self.data_bind("case_sensitive", ck_caseSensitive)
        self.data_bind("match_regular_expression", ck_matchRegExp)

        # propagate widgets that need to be accessed
        self._tv_vars = tv_vars

        # update the form
        self._updateform()

    # the data update utility loads data into the item
    def _updatedata(self):
        self._item.command = self.data_get("command")
        self._item.command_arguments = arg_split(self.data_get("command_arguments"))
        self._item.startup_path = normpath(self.data_get("startup_path"))
        v = self.data_get("include_environment")
        self._item.include_environment = False if not v else None
        v = self.data_get("set_environment_variables")
        self._item.set_environment_variables = False if not v else None
        e = {}
        for l in self._envvars:
            e[l[0]] = str(l[1])
        self._item.environment_variables = e or None
        self._item.success_status = None
        self._item.success_stdout = None
        self._item.success_stderr = None
        self._item.failure_status = None
        self._item.failure_stdout = None
        self._item.failure_stderr = None
        self._item.match_exact = None
        self._item.match_regular_expression = None
        self._item.case_sensitive = None
        self._item.timeout_seconds = self.data_get("timeout_seconds") or None
        check_for = self.data_get("check_for")
        check_what = self.data_get("check_what")
        check_value = self.data_get("check_value")
        match_exact = self.data_get("match_exact")
        case_sensitive = self.data_get("case_sensitive")
        match_regular_expression = self.data_get("match_regular_expression")
        if check_for != UI_OUTCOME_NONE:
            if check_for == UI_OUTCOME_SUCCESS:
                if check_what == UI_EXIT_CODE:
                    self._item.success_status = (
                        int(check_value) if check_value != "" else None
                    )
                elif check_what == UI_STREAM_STDOUT:
                    self._item.success_stdout = str(check_value) or None
                    self._item.match_exact = bool(match_exact) or None
                    self._item.match_regular_expression = (
                        bool(match_regular_expression) or None
                    )
                    self._item.case_sensitive = bool(case_sensitive) or None
                elif check_what == UI_STREAM_STDERR:
                    self._item.success_stderr = str(check_value) or None
                    self._item.match_exact = bool(match_exact) or None
                    self._item.match_regular_expression = (
                        bool(match_regular_expression) or None
                    )
                    self._item.case_sensitive = bool(case_sensitive) or None
            elif check_for == UI_OUTCOME_FAILURE:
                if check_what == UI_EXIT_CODE:
                    self._item.failure_status = (
                        int(check_value) if check_value != "" else None
                    )
                elif check_what == UI_STREAM_STDOUT:
                    self._item.failure_stdout = str(check_value) or None
                    self._item.match_exact = bool(match_exact) or None
                    self._item.match_regular_expression = (
                        bool(match_regular_expression) or None
                    )
                    self._item.case_sensitive = bool(case_sensitive) or None
                elif check_what == UI_STREAM_STDERR:
                    self._item.failure_stderr = str(check_value) or None
                    self._item.match_exact = bool(match_exact) or None
                    self._item.match_regular_expression = (
                        bool(match_regular_expression) or None
                    )
                    self._item.case_sensitive = bool(case_sensitive) or None
        return super()._updatedata()

    def _updateform(self):
        self.data_set("varname", "")
        self.data_set("newvalue", "")
        self.data_set("command", self._item.command)
        self.data_set(
            "command_arguments",
            (
                " ".join(quote(x) for x in self._item.command_arguments)
                if self._item.command_arguments
                else None
            ),
        )
        self.data_set("startup_path", self._item.startup_path)
        self.data_set(
            "include_environment",
            (
                self._item.include_environment
                if self._item.include_environment is False
                else True
            ),
        )
        self.data_set(
            "set_environment_variables",
            (
                self._item.set_environment_variables
                if self._item.set_environment_variables is False
                else True
            ),
        )
        self.data_set("match_exact", self._item.match_exact or False)
        self.data_set("case_sensitive", self._item.case_sensitive or False)
        self.data_set(
            "match_regular_expression", self._item.match_regular_expression or False
        )
        self.data_set("timeout_seconds", self._item.timeout_seconds or 0)
        check_for = UI_OUTCOME_NONE
        check_what = UI_EXIT_CODE
        check_value = ""
        if self._item.success_status is not None:
            check_for = UI_OUTCOME_SUCCESS
            check_what = UI_EXIT_CODE
            check_value = self._item.success_status
        elif self._item.success_stdout is not None:
            check_for = UI_OUTCOME_SUCCESS
            check_what = UI_STREAM_STDOUT
            check_value = self._item.success_stdout
        elif self._item.success_stderr is not None:
            check_for = UI_OUTCOME_SUCCESS
            check_what = UI_STREAM_STDERR
            check_value = self._item.success_stderr
        if self._item.failure_status is not None:
            check_for = UI_OUTCOME_FAILURE
            check_what = UI_EXIT_CODE
            check_value = self._item.failure_status
        elif self._item.failure_stdout is not None:
            check_for = UI_OUTCOME_FAILURE
            check_what = UI_STREAM_STDOUT
            check_value = self._item.failure_stdout
        elif self._item.failure_stderr is not None:
            check_for = UI_OUTCOME_FAILURE
            check_what = UI_STREAM_STDERR
            check_value = self._item.failure_stderr
        self.data_set("check_for", check_for)
        self.data_set("check_what", check_what)
        self.data_set("check_value", check_value)
        self._envvars = []
        if self._item.environment_variables:
            for k in self._item.environment_variables:
                self._envvars.append([k, self._item.environment_variables[k]])
        self._envvars.sort(key=lambda x: x[0])
        self._tv_vars.delete(*self._tv_vars.get_children())
        for entry in self._envvars:
            self._tv_vars.insert(
                "", iid="%s-%s" % (entry[0], entry[1]), values=entry, index=tk.END
            )
        return super()._updateform()

    def add_var(self):
        name = self.data_get("varname")
        value = self.data_get("newvalue")
        if name:
            if not value:
                messagebox.showerror(UI_POPUP_T_ERR, UI_POPUP_EMPTYVARVALUE)
            else:
                self._envvars = list(
                    entry for entry in self._envvars if entry[0] != name
                )
                self._envvars.append([name, value])
                e = {}
                for l in self._envvars:
                    e[l[0]] = str(l[1])
                self._item.environment_variables = e or None
                self._envvars.sort(key=lambda x: x[0])
                self._updatedata()
                self._updateform()

    def del_var(self):
        entry = self.data_get("envvar_selection")
        name = entry[0]
        value = entry[1]
        self._envvars = list(entry for entry in self._envvars if entry[0] != name)
        e = {}
        for l in self._envvars:
            e[l[0]] = str(l[1])
        self._item.environment_variables = e or None
        # first update the form data, then recall the variable in the input
        # fields, so that the user can re-add the variable again if needed
        self._updatedata()
        self._updateform()
        self.data_set("varname", name)
        self.data_set("newvalue", value)

    def recall_var(self):
        entry = self.data_get("envvar_selection")
        name = entry[0]
        value = entry[1]
        self.data_set("varname", name)
        self.data_set("newvalue", value)

    def browse_command(self):
        filetypes = [(UI_FILETYPE_ALL, ".*")]
        if sys.platform.startswith("win"):
            exts = get_executable_extensions()
            if exts:
                execs_list = " ".join(exts)
                filetypes.insert(0, (UI_FILETYPE_EXECUTABLES, execs_list))
        entry = filedialog.askopenfilename(parent=self.dialog, filetypes=filetypes)
        if entry:
            self.data_set("command", entry)

    def browse_startup_path(self):
        entry = filedialog.askdirectory(parent=self.dialog)
        if entry:
            self.data_set("startup_path", entry)


# end.
