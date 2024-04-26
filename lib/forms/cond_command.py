# command condition form

from os.path import normpath

from lib.i18n.strings import *

from shlex import split as arg_split, quote

from lib.utility import sg
from lib.icons import XMARK_ICON48 as XMARK_ICON

from lib.forms.cond import form_Condition
from lib.items.cond_command import CommandCondition

import re
import os
import shutil


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


# (extra) layout generator
def _form_layout():
    return [
        [sg.Frame(UI_FORM_EXTRADELAY, [[
            sg.T(UI_FORM_EXTRADELAYSPEC),
            sg.I(key='-CHECK_AFTER-', expand_x=True),
            sg.Combo([UI_TIME_SECONDS, UI_TIME_MINUTES, UI_TIME_HOURS], default_value=UI_TIME_SECONDS, key='-CHECK_AFTER_UNIT-'),
        ]], expand_x=True, expand_y=False) ],

        [sg.Frame(UI_FORM_COMMAND, [[
            sg.Column([
                [ sg.T(UI_FORM_COMMAND_SC) ],
                [ sg.T(UI_FORM_ARGS_SC) ],
                [ sg.T(UI_FORM_STARTUPPATH_SC) ],
            ]),
            sg.Column([
                [ sg.I(key='-COMMAND-', expand_x=True), sg.FileBrowse(UI_BROWSE, key='-COMMAND_B-') ],
                [ sg.I(key='-COMMAND_ARGS-', expand_x=True) ],
                [ sg.I(key='-COMMAND_WORKFOLDER-', expand_x=True), sg.FolderBrowse(UI_BROWSE, key='-COMMAND_WORKFOLDER_B-') ],
            ], expand_x=True),
        ]], expand_x=True) ],

        [sg.Frame(UI_FORM_ENVIRONMENT, [
            [ sg.Checkbox(UI_FORM_PRESERVEENVIRONMENT, key='-COMMAND_KEEP_ENV-', default=True) ],
            [ sg.T(UI_FORM_VARIABLES_SC, ) ],
            [ sg.Table(
                [['' for x in range(2)] for y in range(3)],
                headings=[UI_FORM_NAME, UI_FORM_VALUE],
                key='-COMMAND_ENVVARS-',
                num_rows=3,
                justification='left',
                expand_x=True, expand_y=True,
            ) ],
            [
                sg.Column([[ sg.T(UI_FORM_VARNAME_SC) ], [ sg.I(key='-ENVVAR_NAME-', expand_x=True) ]], expand_x=True),
                sg.Column([[ sg.T(UI_FORM_NEWVALUE_SC) ], [ sg.I(key='-ENVVAR_VALUE-', expand_x=True) ]], expand_x=True),
            ],
            [ sg.Push(), sg.B_ADD(UI_UPDATE, key='-UPDATE_ENVVAR-'), sg.B_DEL(UI_DEL, key='-DELETE_ENVVAR-') ],
        ], expand_x=True, expand_y=True) ],

        [sg.Frame(UI_FORM_CHECKS, [[
                sg.Column([
                    [ sg.T(UI_FORM_CHECKFOR_SC) ],
                    [ sg.Combo([UI_OUTCOME_NONE, UI_OUTCOME_SUCCESS, UI_OUTCOME_FAILURE], key='-CHECK_FOR-', default_value=UI_OUTCOME_NONE, readonly=True) ]
                ], vertical_alignment='top'),
                sg.Column([
                    [ sg.T(UI_FORM_TESTVAL) ],
                    [
                        sg.Combo([UI_EXIT_CODE, UI_STREAM_STDOUT, UI_STREAM_STDERR], key='-CHECK_WHAT-', default_value=UI_EXIT_CODE, readonly=True),
                        sg.I(key='-CHECK_VALUE-', expand_x=True),
                    ],
                    [
                        sg.CB(UI_FORM_MATCHEXACT, key='-CHECK_EXACT-'),
                        sg.CB(UI_FORM_CASESENSITIVE, key='-CHECK_CASE_SENSITIVE-'),
                        sg.CB(UI_FORM_MATCHREGEXP, key='-CHECK_REGEXP-'),
                    ],
                ], expand_x=True)
        ]], expand_x=True) ],
    ]


# specialized subform
class form_CommandCondition(form_Condition):
    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, CommandCondition))
        else:
            item = CommandCondition()
        extra_layout = _form_layout()
        form_Condition.__init__(self, UI_TITLE_COMMANDCOND, tasks_available, extra_layout, item)
        self._envvars = []
        self._form['-COMMAND_ENVVARS-'].bind('<Double-Button-1>' , '+-dblclick-')
        self.dont_update('-COMMAND_B-', '-COMMAND_WORKFOLDER_B-')   # must force it, I don't know why
        self.add_checks(
            ('-COMMAND-', UI_FORM_COMMAND_SC, _is_command),
            ('-COMMAND_WORKFOLDER-', UI_FORM_STARTUPPATH_SC, _is_dir),
            ('-CHECK_AFTER-', UI_FORM_EXTRADELAYSPEC, lambda x: int(x) > 0),
        )

    def _updatedata(self):
        form_Condition._updatedata(self)
        self._data['-ENVVAR_NAME-'] = ''
        self._data['-ENVVAR_VALUE-'] = ''

        if self._item:
            self._data['-COMMAND-'] = self._item.command
            self._data['-COMMAND_ARGS-'] = ' '.join(quote(x) for x in self._item.command_arguments) if self._item.command_arguments else None
            self._data['-COMMAND_WORKFOLDER-'] = self._item.startup_path
            self._data['-COMMAND_KEEP_ENV-'] = self._item.include_environment
            self._data['-CHECK_EXACT-'] = self._item.match_exact
            self._data['-CHECK_CASE_SENSITIVE-'] = self._item.case_sensitive
            self._data['-CHECK_REGEXP-'] = self._item.match_regular_expression
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
            self._data['-CHECK_FOR-'] = check_for
            self._data['-CHECK_WHAT-'] = check_what
            self._data['-CHECK_VALUE-'] = check_value
            self._data['-COMMAND_ENVVARS-'] = []
            self._envvars = []
            if self._item.environment_variables:
                for k in self._item.environment_variables:
                    self._data['-COMMAND_ENVVARS-'].append([k, self._item.environment_variables[k]])
                    self._envvars.append([k, self._item.environment_variables[k]])
            if self._item.check_after is not None and self._item.check_after % 3600 == 0:
                ca = int(self._item.check_after / 3600)
                cau = UI_TIME_HOURS
            elif self._item.check_after is not None and self._item.check_after % 60 == 0:
                ca = int(self._item.check_after / 60)
                cau = UI_TIME_MINUTES
            else:
                ca = self._item.check_after
                cau = UI_TIME_SECONDS
            self._data['-CHECK_AFTER-'] = ca
            self._data['-CHECK_AFTER_UNIT-'] = cau
        else:
            self._data['-COMMAND-'] = ''
            self._data['-COMMAND_ARGS-'] = ''
            self._data['-COMMAND_WORKFOLDER-'] = ''
            self._data['-COMMAND_KEEP_ENV-'] = False
            self._data['-CHECK_FOR-'] = UI_OUTCOME_NONE
            self._data['-CHECK_WHAT-'] = UI_EXIT_CODE
            self._data['-CHECK_VALUE-'] = ''
            self._data['-CHECK_EXACT-'] = False
            self._data['-CHECK_CASE_SENSITIVE-'] = False
            self._data['-CHECK_REGEXP-'] = False
            self._data['-COMMAND_ENVVARS-'] = []
            self._data['-CHECK_AFTER-'] = None
            self._data['-CHECK_AFTER_UNIT-'] = UI_TIME_SECONDS

    def _updateitem(self):
        form_Condition._updateitem(self)
        self._item.command = normpath(self._data['-COMMAND-'])
        self._item.command_arguments = arg_split(self._data['-COMMAND_ARGS-'])
        self._item.startup_path = normpath(self._data['-COMMAND_WORKFOLDER-'])
        self._item.include_environment = self._data['-COMMAND_KEEP_ENV-']
        self._item.environment_variables = {}
        for l in self._envvars:
            self._item.environment_variables[l[0]] = str(l[1])
        self._item.success_status = None
        self._item.success_stdout = None
        self._item.success_stderr = None
        self._item.failure_status = None
        self._item.failure_stdout = None
        self._item.failure_stderr = None
        self._item.match_exact = None
        self._item.match_regular_expression = None
        self._item.case_sensitive = None
        check_for = self._data['-CHECK_FOR-']
        check_what = self._data['-CHECK_WHAT-']
        if check_for != UI_OUTCOME_NONE:
            if check_for == UI_OUTCOME_SUCCESS:
                if check_what == UI_EXIT_CODE:
                    self._item.success_status = int(self._data['-CHECK_VALUE-'])
                elif check_what == UI_STREAM_STDOUT:
                    self._item.success_stdout = str(self._data['-CHECK_VALUE-'])
                    self._item.match_exact = bool(self._data['-CHECK_EXACT-'])
                    self._item.match_regular_expression = bool(self._data['-CHECK_REGEXP-'])
                    self._item.case_sensitive = bool(self._data['-CHECK_CASE_SENSITIVE-'])
                elif check_what == UI_STREAM_STDERR:
                    self._item.success_stderr = str(self._data['-CHECK_VALUE-'])
                    self._item.match_exact = bool(self._data['-CHECK_EXACT-'])
                    self._item.match_regular_expression = bool(self._data['-CHECK_REGEXP-'])
                    self._item.case_sensitive = bool(self._data['-CHECK_CASE_SENSITIVE-'])
            elif check_for == UI_OUTCOME_FAILURE:
                if check_what == UI_EXIT_CODE:
                    self._item.failure_status = int(self._data['-CHECK_VALUE-'])
                elif check_what == UI_STREAM_STDOUT:
                    self._item.failure_stdout = str(self._data['-CHECK_VALUE-'])
                    self._item.match_exact = bool(self._data['-CHECK_EXACT-'])
                    self._item.match_regular_expression = bool(self._data['-CHECK_REGEXP-'])
                    self._item.case_sensitive = bool(self._data['-CHECK_CASE_SENSITIVE-'])
                elif check_what == UI_STREAM_STDERR:
                    self._item.failure_stderr = str(self._data['-CHECK_VALUE-'])
                    self._item.match_exact = bool(self._data['-CHECK_EXACT-'])
                    self._item.match_regular_expression = bool(self._data['-CHECK_REGEXP-'])
                    self._item.case_sensitive = bool(self._data['-CHECK_CASE_SENSITIVE-'])
        if self._data['-CHECK_AFTER-']:
            if self._data['-CHECK_AFTER_UNIT-'] == UI_TIME_HOURS:
                self._item.check_after = int(self._data['-CHECK_AFTER-']) * 3600
            elif self._data['-CHECK_AFTER_UNIT-'] == UI_TIME_MINUTES:
                self._item.check_after = int(self._data['-CHECK_AFTER-']) * 60
            else:
                self._item.check_after = int(self._data['-CHECK_AFTER-'])
        else:
            self._item.check_after = None

    def process_event(self, event, values):
        ret = super().process_event(event, values)
        if ret is None:
            if event == '-COMMAND_ENVVARS-+-dblclick-':
                self._data['-ENVVAR_NAME-'] = self._envvars[self._data['-COMMAND_ENVVARS-'][0]][0]
                self._data['-ENVVAR_VALUE-'] = self._envvars[self._data['-COMMAND_ENVVARS-'][0]][1]

            elif event == '-UPDATE_ENVVAR-':
                if self._data['-ENVVAR_NAME-'] and self._data['-ENVVAR_VALUE-']:
                    if _RE_VALIDNAME.match(self._data['-ENVVAR_NAME-']):
                        r = list(e for e in self._envvars if e[0] != self._data['-ENVVAR_NAME-'])
                        r.append([self._data['-ENVVAR_NAME-'], self._data['-ENVVAR_VALUE-']])
                        self._envvars = r
                    else:
                        sg.Popup(UI_POPUP_INVALIDVARNAME, title=UI_POPUP_T_ERR, icon=XMARK_ICON)
                else:
                    sg.Popup(UI_POPUP_EMPTYVARVALUE, title=UI_POPUP_T_ERR, icon=XMARK_ICON)

            elif event == '-DELETE_ENVVAR-':
                if self._data['-ENVVAR_NAME-']:
                    r = list(e for e in self._envvars if e[0] != self._data['-ENVVAR_NAME-'])
                    self._envvars = r
                else:
                    sg.Popup(UI_POPUP_EMPTYVARVALUE, title=UI_POPUP_T_ERR, icon=XMARK_ICON)

            # ...
            self._data['-COMMAND_ENVVARS-'] = []
            for l in self._envvars:
                self._data['-COMMAND_ENVVARS-'].append(l.copy())
        else:
            return ret


# end.
