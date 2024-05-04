# base task form

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import APP_ICON32 as APP_ICON
from lib.icons import XMARK_ICON48 as XMARK_ICON

from lib.items.task import Task

import re


# regular expression for item name checking
_RE_VALIDNAME = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")


# layout generator: this is a base form and supports an extra layout for
# specific item forms, which will inherit the surrounding form layout
def _form_layout(extra_layout=[]):
    return [
        # common layout
        [ sg.Frame(UI_FORM_TASK, [[
            sg.Column([
                [ sg.T(UI_FORM_NAME_SC) ],
            ]),
            sg.Column([
                [ sg.I(key='-NAME-', expand_x=True) ],
            ], expand_x=True),
        ]], expand_x=True)],

        # extra layout
        extra_layout,

        # form control section
        [ sg.Push(), sg.B_OK(UI_OK, key='-OK-'), sg.B_CANCEL(UI_CANCEL, key='-CANCEL-') ],
    ]


# base form for task items: this is never used as-is, but declined instead
# into more specific forms that will invoke the base `__init__` providing the
# extra layout that is suitable for the specific item
class form_Task(object):
    def __init__(self, title, extra_layout, item=None):
        layout = _form_layout(extra_layout)
        self._form = sg.Window(title, layout=layout, icon=APP_ICON, size=(960, 640), finalize=True)
        self._data = {}
        self.__dont_update = []
        self.__datachecks = [
            ('-NAME-', UI_FORM_NAME_SC, lambda x: _RE_VALIDNAME.match(x)),
        ]
        if item:
            self.set_item(item)
        else:
            self.reset_item()

    def _updatedata(self):
        if self._item:
            self._data['-NAME-'] = self._item.name
        else:
            self._data['-NAME-'] = ''

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


    # list of keys of elements that should not be updated
    def dont_update(self, *keys):
        self.__dont_update += keys

    # set and remove the associated item
    def set_item(self, item):
        assert(isinstance(item, Task))
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
        if event in [sg.WIN_CLOSED, '-CANCEL-']:
            return False
        elif event == '-OK-':
            return True
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
                        sg.popup(UI_POPUP_INVALIDPARAMETERS_T % checks, title=UI_POPUP_T_ERR, icon=XMARK_ICON)
                else:
                    self._form.close()
                    return None
            self._updateform()
        self._updateitem()
        return self._item


# end.
