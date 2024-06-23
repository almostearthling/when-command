# command condition form


from ..i18n.strings import *

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from .ui import *

from .cond import form_Condition
from ..items.cond_command import CommandCondition

import re
import os
import shutil

from shlex import split as arg_split, quote
from os.path import normpath


# regular expression for item name checking
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
    if os.path.exists(os.path.join(s, '.')):
        return True
    else:
        return False


# specialized subform
class form_CommandCondition(form_Condition):

    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, CommandCondition))
        else:
            item = CommandCondition()
        super().__init__(UI_TITLE_COMMANDCOND, tasks_available, item)
        self._envvars = []

        # this area hosts other panes, each with custom grid layout, and the
        # separators that act as borders between the sections
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # command: use a separate area to customize layout
        a_area = ttk.Frame(area)
        a_area.grid(row=0, column=0, sticky=tk.NSEW)

        l_command = ttk.Label(a_area, text=UI_FORM_COMMAND_SC)
        e_command = ttk.Entry(a_area)
        b_commandBrowse = ttk.Button(a_area, text=UI_BROWSE)
        l_command.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_command.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_commandBrowse.grid(row=0, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        self.data_bind('command', e_command, TYPE_STRING, _is_command)

        l_args = ttk.Label(a_area, text=UI_FORM_ARGS_SC)
        e_args = ttk.Entry(a_area)
        l_args.grid(row=1, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_args.grid(row=1, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        self.data_bind('command_arguments', e_args, TYPE_STRING)

        l_startupPath = ttk.Label(a_area, text=UI_FORM_STARTUPPATH_SC)
        e_startupPath = ttk.Entry(a_area)
        b_startupPathBrowse = ttk.Button(a_area, text=UI_BROWSE)
        l_startupPath.grid(row=2, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_startupPath.grid(row=2, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_startupPathBrowse.grid(row=2, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        self.data_bind('startup_path', e_startupPath, TYPE_STRING, _is_dir)

        a_area.columnconfigure(1, weight=1)

        sep1 = ttk.Separator(area)
        sep1.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=PAD)

        # environment: deserves an area to customize layout
        v_area = ttk.Frame(area)
        v_area.grid(row=3, column=0, sticky=tk.NSEW)
        v_area.columnconfigure(0, weight=1)
        v_area.columnconfigure(1, weight=1)

        # grow this part of the form
        area.rowconfigure(3, weight=1)

        # subarea for checkboxes
        vv_area1 = ttk.Frame(v_area)
        vv_area1.grid(row=0, column=0, columnspan=2, sticky=tk.EW)
        ck_preserveEnv = ttk.Checkbutton(vv_area1, text=UI_FORM_PRESERVEENVIRONMENT)
        ck_setEnvVars = ttk.Checkbutton(vv_area1, text=UI_FORM_SETWENVIRONMENT)
        ck_preserveEnv.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        ck_setEnvVars.grid(row=0, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        self.data_bind('include_environment', ck_preserveEnv)
        self.data_bind('set_environment_variables', ck_setEnvVars)

        l_vars = ttk.Label(v_area, text=UI_FORM_VARIABLES_SC)
        tv_vars = ttk.Treeview(v_area, columns=('name', 'value'), show='headings', height=5)
        l_vars.grid(row=1, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        tv_vars.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, padx=PAD, pady=PAD)
        tv_vars.heading('name', anchor=tk.W, text=UI_FORM_NAME)
        tv_vars.heading('value', anchor=tk.W, text=UI_FORM_VALUE)
        self._tv_vars = tv_vars
        self.data_bind('envvar_selection', tv_vars)

        # bind double click to variable recall
        self._tv_vars.bind('<Double-Button-1>', lambda _: self.recall_var())

        l_varName = ttk.Label(v_area, text=UI_FORM_VARNAME_SC)
        e_varName = ttk.Entry(v_area)
        l_varValue = ttk.Label(v_area, text=UI_FORM_NEWVALUE_SC)
        e_varValue = ttk.Entry(v_area)
        l_varName.grid(row=3, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        l_varValue.grid(row=3, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        e_varName.grid(row=4, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        e_varValue.grid(row=4, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        self.data_bind('varname', e_varName, TYPE_STRING, lambda x: x == '' or _RE_VALIDNAME.match(x))
        self.data_bind('newvalue', e_varValue, TYPE_STRING)

        # subarea for buttons
        vv_area2 = ttk.Frame(v_area)
        vv_area2.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW)
        b_addVar = ttk.Button(vv_area2, text=UI_UPDATE, width=BUTTON_STANDARD_WIDTH, command=self.add_var)
        b_delVar = ttk.Button(vv_area2, text=UI_DEL, width=BUTTON_STANDARD_WIDTH, command=self.del_var)
        b_addVar.grid(row=0, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)
        b_delVar.grid(row=0, column=2, sticky=tk.NSEW, padx=PAD, pady=PAD)
        vv_area2.columnconfigure(0, weight=1)

        sep2 = ttk.Separator(area)
        sep2.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=PAD)

        # checks: deserves an area to customize layout
        c_area = ttk.Frame(area)
        c_area.grid(row=5, column=0, sticky=tk.NSEW)

        l_checkFor = ttk.Label(c_area, text=UI_FORM_CHECKFOR_SC)
        cb_checkFor = ttk.Combobox(
            c_area,
            values=(UI_OUTCOME_NONE, UI_OUTCOME_SUCCESS, UI_OUTCOME_FAILURE),
            state='readonly',
            )
        l_checkFor.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cb_checkFor.grid(row=1, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        l_checkWhat = ttk.Label(c_area, text=UI_FORM_CHECKAGAINST_SC)
        cb_checkWhat = ttk.Combobox(
            c_area,
            values=(UI_EXIT_CODE, UI_STREAM_STDOUT, UI_STREAM_STDERR),
            state='readonly',
            )
        l_checkValue = ttk.Label(c_area, text=UI_FORM_TESTVAL_SC)
        e_checkValue = ttk.Entry(c_area)
        l_checkWhat.grid(row=0, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        cb_checkWhat.grid(row=1, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        l_checkValue.grid(row=0, column=2, sticky=tk.W, padx=PAD, pady=PAD)
        e_checkValue.grid(row=1, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        self.data_bind('check_for', cb_checkFor, TYPE_STRING)
        self.data_bind('check_what', cb_checkWhat, TYPE_STRING)
        self.data_bind('check_value', e_checkValue, TYPE_STRING)

        l_timeoutSecs = ttk.Label(c_area, text=UI_FORM_TIMEOUTSECS_SC)
        e_timeoutSecs = ttk.Entry(c_area)
        l_timeoutSecs.grid(row=0, column=3, sticky=tk.W, padx=PAD, pady=PAD)
        e_timeoutSecs.grid(row=1, column=3, sticky=tk.EW, padx=PAD, pady=PAD)
        self.data_bind('timeout_seconds', e_timeoutSecs, TYPE_INT, lambda x: x >= 0)

        # subarea for checkboxes
        cc_area = ttk.Frame(c_area)
        cc_area.grid(row=3, column=2, columnspan=2, sticky=tk.EW)
        ck_matchExact = ttk.Checkbutton(cc_area, text=UI_FORM_MATCHEXACT)
        ck_caseSensitive = ttk.Checkbutton(cc_area, text=UI_FORM_CASESENSITIVE)
        ck_matchRegExp = ttk.Checkbutton(cc_area, text=UI_FORM_MATCHREGEXP)
        ck_matchExact.grid(row=0, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        ck_caseSensitive.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        ck_matchRegExp.grid(row=0, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        self.data_bind('match_exact', ck_matchExact)
        self.data_bind('case_sensitive', ck_caseSensitive)
        self.data_bind('match_regular_expression', ck_matchRegExp)

        c_area.columnconfigure(2, weight=1)
        self._updateform()


    # the data update utility loads data into the item
    def _updatedata(self):
        self._item.command = self.data_get('command')
        self._item.command_arguments = arg_split(self.data_get('command_arguments'))
        self._item.startup_path = normpath(self.data_get('startup_path'))
        v = self.data_get('include_environment')
        self._item.include_environment = False if not v else None
        v = self.data_get('set_environment_variables')
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
        self._item.timeout_seconds = self.data_get('timeout_seconds') or None
        check_for = self.data_get('check_for')
        check_what = self.data_get('check_what')
        check_value = self.data_get('check_value')
        match_exact = self.data_get('match_exact')
        case_sensitive = self.data_get('case_sensitive')
        match_regular_expression = self.data_get('match_regular_expression')
        if check_for != UI_OUTCOME_NONE:
            if check_for == UI_OUTCOME_SUCCESS:
                if check_what == UI_EXIT_CODE:
                    self._item.success_status = int(check_value) if check_value != '' else None
                elif check_what == UI_STREAM_STDOUT:
                    self._item.success_stdout = str(check_value) or None
                    self._item.match_exact = bool(match_exact) or None
                    self._item.match_regular_expression = bool(match_regular_expression) or None
                    self._item.case_sensitive = bool(case_sensitive) or None
                elif check_what == UI_STREAM_STDERR:
                    self._item.success_stderr = str(check_value) or None
                    self._item.match_exact = bool(match_exact) or None
                    self._item.match_regular_expression = bool(match_regular_expression) or None
                    self._item.case_sensitive = bool(case_sensitive) or None
            elif check_for == UI_OUTCOME_FAILURE:
                if check_what == UI_EXIT_CODE:
                    self._item.failure_status = int(check_value) if check_value != '' else None
                elif check_what == UI_STREAM_STDOUT:
                    self._item.failure_stdout = str(check_value) or None
                    self._item.match_exact = bool(match_exact) or None
                    self._item.match_regular_expression = bool(match_regular_expression) or None
                    self._item.case_sensitive = bool(case_sensitive) or None
                elif check_what == UI_STREAM_STDERR:
                    self._item.failure_stderr = str(check_value) or None
                    self._item.match_exact = bool(match_exact) or None
                    self._item.match_regular_expression = bool(match_regular_expression) or None
                    self._item.case_sensitive = bool(case_sensitive) or None
        return super()._updatedata()


    def _updateform(self):
        self.data_set('varname', '')
        self.data_set('newvalue', '')
        self.data_set('command', self._item.command)
        self.data_set('command_arguments', ' '.join(quote(x) for x in self._item.command_arguments) if self._item.command_arguments else None)
        self.data_set('startup_path', self._item.startup_path)
        self.data_set('include_environment', self._item.include_environment)
        self.data_set('set_environment_variables', self._item.set_environment_variables)
        self.data_set('match_exact', self._item.match_exact)
        self.data_set('case_sensitive', self._item.case_sensitive)
        self.data_set('match_regular_expression', self._item.match_regular_expression)
        self.data_set('timeout_seconds', self._item.timeout_seconds or 0)
        check_for = UI_OUTCOME_NONE
        check_what = UI_EXIT_CODE
        check_value = ''
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
            check_value = self._item.success_status
        elif self._item.failure_stdout is not None:
            check_for = UI_OUTCOME_FAILURE
            check_what = UI_STREAM_STDOUT
            check_value = self._item.success_stdout
        elif self._item.failure_stderr is not None:
            check_for = UI_OUTCOME_FAILURE
            check_what = UI_STREAM_STDERR
            check_value = self._item.success_stderr
        self.data_set('check_for', check_for)
        self.data_set('check_what', check_what)
        self.data_set('check_value', check_value)
        self._envvars = []
        if self._item.environment_variables:
            for k in self._item.environment_variables:
                self._envvars.append([k, self._item.environment_variables[k]])
        self._envvars.sort(key=lambda x: x[0])
        self._tv_vars.delete(*self._tv_vars.get_children())
        for entry in self._envvars:
            self._tv_vars.insert('', iid="%s-%s" % (entry[0], entry[1]), values=entry, index=tk.END)
        return super()._updateform()

    def add_var(self):
        name = self.data_get('varname')
        value = self.data_get('newvalue')
        if name:
            if not value:
                messagebox.showerror(UI_POPUP_T_ERR, UI_POPUP_EMPTYVARVALUE)
            else:
                self._envvars = list(entry for entry in self._envvars if entry[0] != name)
                self._envvars.append([name, value])
                e = {}
                for l in self._envvars:
                    e[l[0]] = str(l[1])
                self._item.environment_variables = e or None
                self._envvars.sort(key=lambda x: x[0])
            self._updateform()

    def del_var(self):
        entry = self.data_get('envvar_selection')
        name = entry[0]
        value = entry[1]
        self._envvars = list(entry for entry in self._envvars if entry[0] != name)
        e = {}
        for l in self._envvars:
            e[l[0]] = str(l[1])
        self._item.environment_variables = e or None
        # first update the form data, then recall the variable in the input
        # fields, so that the user can re-add the variable again if needed
        self._updateform()
        self.data_set('varname', name)
        self.data_set('newvalue', value)

    def recall_var(self):
        entry = self.data_get('envvar_selection')
        name = entry[0]
        value = entry[1]
        self.data_set('varname', name)
        self.data_set('newvalue', value)


# end.
