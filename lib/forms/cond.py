# base condition form

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import APP_ICON32 as APP_ICON
from lib.icons import XMARK_ICON48 as XMARK_ICON

from lib.items.cond import Condition

import re


# regular expression for item name checking
_RE_VALIDNAME = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")


# layout generator: this is a base form and supports an extra layout for
# specific item forms, which will inherit the surrounding form layout; due
# to the intrinsic complexity of condition items, the specific layout is
# displayed in a second tab
def _form_layout(tasks_available, extra_layout=[]):
    return [[
        sg.TabGroup([[

            # common layout
            sg.Tab(UI_FORM_COMMON_PARAMS, [
                [ sg.Frame(UI_FORM_CONDITION, [
                    [
                        sg.Column([
                            [ sg.T(UI_FORM_NAME_SC) ],
                        ]),
                        sg.Column([
                            [ sg.I(key='-NAME-', expand_x=True) ],
                        ], expand_x=True),
                    ],
                    [ sg.CB(UI_FORM_CHECKCONDRECURRENT, default=False, key='-RECURRING-') ],
                    [ sg.CB(UI_FORM_SUSPENDCONDATSTARTUP, default=False, key='-SUSPENDED-') ],
                ], expand_x=True) ],
                [ sg.Frame(UI_FORM_TASKS, [
                    [ sg.T(UI_FORM_ACTIVETASKS_SC) ],
                    [ sg.Listbox(
                        [],
                        key='-TASKS-',
                        expand_x=True, expand_y=True,
                    ) ],
                    [
                        sg.T(UI_FORM_TASK_SC),
                        sg.Combo(tasks_available, key='-TASKS_AVAILABLE-', expand_x=True, readonly=True),
                        sg.B(UI_ADD, key='-ADD_TASK-'),
                        sg.B(UI_DEL, key='-DEL_TASK-'),
                    ],
                    [ sg.CB(UI_FORM_RUNTASKSSEQUENTIALLY, default=True, key='-EXEC_SEQUENCE-') ],
                    [
                        sg.Radio(UI_FORM_BREAKNEVER, 'task_stop', key='-BREAK_NEVER-'),
                        sg.Radio(UI_FORM_BREAKONFAILURE, 'task_stop', key='-BREAK_ON_FAILURE-'),
                        sg.Radio(UI_FORM_BREAKONSUCCESS, 'task_stop', key='-BREAK_ON_SUCCESS-'),
                    ],
                ], expand_x=True, expand_y=True) ],
            ]),

            # specific layout
            sg.Tab(UI_FORM_SPECIFIC_PARAMS, extra_layout),
        ]], expand_x=True, expand_y=True, tab_location='topleft') ],

        # form control section
        [ sg.Push(), sg.B(UI_OK, key='-OK-'), sg.B(UI_CANCEL, key='-CANCEL-') ],
    ]


# base form for condition items: this is never used as-is, but declined instead
# into more specific forms that will invoke the base `__init__` providing the
# extra layout that is suitable for the specific item
class form_Condition(object):
    def __init__(self, title, tasks_available, extra_layout, item=None):
        self._form = sg.Window(
            title,
            layout=_form_layout(tasks_available, extra_layout),
            icon=APP_ICON,
            size=(960, 640),
            finalize=True,
        )
        self._form['-TASKS-'].bind('<Double-Button-1>' , '+-dblclick-')
        self._data = {}
        self._results = []
        self.__dont_update = []
        self.__datachecks = [
            ('-NAME-', UI_FORM_NAME_SC, lambda x: _RE_VALIDNAME.match(x)),
        ]
        if item:
            self.set_item(item)
        else:
            self.reset_item()

    def _updatedata(self):
        self._data['-TASKS_AVAILABLE-'] = ''
        if self._item:
            self._data['-NAME-'] = self._item.name
            if self._item.break_on_failure:
                self._data['-BREAK_NEVER-'] = False
                self._data['-BREAK_ON_FAILURE-'] = True
                self._data['-BREAK_ON_SUCCESS-'] = False
            elif self._item.break_on_success:
                self._data['-BREAK_NEVER-'] = False
                self._data['-BREAK_ON_FAILURE-'] = False
                self._data['-BREAK_ON_SUCCESS-'] = True
            else:
                self._data['-BREAK_NEVER-'] = True
                self._data['-BREAK_ON_FAILURE-'] = False
                self._data['-BREAK_ON_SUCCESS-'] = False
            self._data['-RECURRING-'] = bool(self._item.recurring)
            self._data['-SUSPENDED-'] = bool(self._item.suspended)
            self._data['-EXEC_SEQUENCE-'] = bool(self._item.execute_sequence)
            self._data['-TASKS-'] = self._item.tasks.copy()
        else:
            self._data['-NAME-'] = ''
            self._data['-BREAK_NEVER-'] = True
            self._data['-BREAK_ON_FAILURE-'] = False
            self._data['-BREAK_ON_SUCCESS-'] = False
            self._data['-EXEC_SEQUENCE-'] = True
            self._data['-RECURRING-'] = True
            self._data['-SUSPENDED-'] = False
            self._data['-TASKS-'] = []

    def _updateform(self):
        for k in self._data:
            if k not in self.__dont_update:
                v = self._data[k]
                if v is None:
                    v = ''
                self._form[k].update(v)
        self._form.refresh()

    def _updateitem(self):
        self._item.name = self._data['-NAME-']
        self._item.recurring = self._data['-RECURRING-']
        self._item.suspended = self._data['-SUSPENDED-']
        self._item.break_on_failure = self._data['-BREAK_ON_FAILURE-']
        self._item.break_on_success = self._data['-BREAK_ON_SUCCESS-']
        self._item.execute_sequence = self._data['-EXEC_SEQUENCE-']
        self._item.tasks = self._data['-TASKS-'].copy()


    # list of keys of elements that should not be updated
    def dont_update(self, *keys):
        self.__dont_update += keys

    # set and remove the associated item
    def set_item(self, item):
        assert(isinstance(item, Condition))
        try:
            self._item = item.__class__(item.as_table())    # get an exact copy to mess with
        except ValueError:
            self._item = item                               # item was newly created: use it
        self._updatedata()

    def reset_item(self):
        self._item = None
        self._updatedata()


    # derived objects should use this function to add checks to be performed
    # on fields, as it avoids adding rules for already existing keys
    def add_checks(self, *checks):
        existing = list(x[0] for x in self.__datachecks)
        for check in checks:
            if check[0] not in existing:
                self.__datachecks.append(check)

    # data check function: returns None if the checks pass, a map of failed
    # entries (form item key: (label, value)) otherwise; both ValueError and
    # TypeError are treated as invalid data; should not be overridden
    def check_data(self):
        failed = {}
        for k, label, func in self.__datachecks:
            if label.endswith(":"):
                label = label[:-1]
            try:
                if not func(self._data[k]):
                    failed[k] = (label, self._data[k])
            except ValueError:
                failed[k] = (label, self._data[k])
            except TypeError:
                failed[k] = (label, self._data[k])
        return failed or None


    # event processor: should always be overridden, and the parent
    # version has to be called first
    def process_event(self, event, values):
        if values:
            self._data = values.copy()
        self._data['-TASKS-'] = self._item.tasks.copy()     # it has been overwritten
        if event in [sg.WIN_CLOSED, '-CANCEL-']:
            return False
        elif event == '-OK-':
            return True
        elif event == '-ADD_TASK-':
            if self._data['-TASKS_AVAILABLE-']:
                self._item.tasks.append(self._data['-TASKS_AVAILABLE-'])
                self._data['-TASKS-'] = self._item.tasks.copy()
        elif event == '-DEL_TASK-':
            if self._data['-TASKS_AVAILABLE-']:
                self._item.tasks = list(x for x in self._item.tasks if x != self._data['-TASKS_AVAILABLE-'])
                self._data['-TASKS-'] = self._item.tasks.copy()
        elif event == '-TASKS-+-dblclick-':
            self._data['-TASKS_AVAILABLE-'] = values['-TASKS-'][0]
        return None

    # main loop handler: should not be overridden
    def run(self):
        self._updateform()
        while True:             # Event Loop
            event, values = self._form.read()
            ret = self.process_event(event, values)
            if ret is not None:
                if ret:
                    check = self.check_data()
                    if check is None:
                        self._form.close()
                        break
                    else:
                        checks = "\n".join("- %s" % check[k][0] for k in check)
                        sg.Popup(UI_POPUP_INVALIDPARAMETERS_T % checks, title=UI_POPUP_T_ERR, icon=XMARK_ICON)
                else:
                    self._form.close()
                    return None
            self._updateform()
        self._updateitem()
        return self._item


# end.
