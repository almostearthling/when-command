# base event form

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import APP_ICON32 as APP_ICON

from lib.items.event import Event


# layout generator: this is a base form and supports an extra layout for
# specific item forms, which will inherit the surrounding form layout
def _form_layout(conditions_available, extra_layout=[]):
    return [
        # common layout
        [ sg.Frame(UI_FORM_COMMON_PARAMS, [[
            sg.Column([
                [ sg.T(UI_FORM_NAME_SC) ],
                [ sg.T(UI_FORM_COND_SC) ],
            ]),
            sg.Column([
                [ sg.I(key='-NAME-', expand_x=True) ],
                [ sg.Combo(conditions_available, key='-CONDITION-', expand_x=True, readonly=True) ],
            ], expand_x=True),
        ]], expand_x=True) ],

        # extra layout
        extra_layout,

        # form control section
        [ sg.Push(), sg.B(UI_OK, key='-OK-'), sg.B(UI_CANCEL, key='-CANCEL-') ],
    ]


# base form for event items: this is never used as-is, but declined instead
# into more specific forms that will invoke the base `__init__` providing the
# extra layout that is suitable for the specific item
class form_Event(object):
    def __init__(self, title, conditions_available, extra_layout, item=None):
        layout = _form_layout(conditions_available, extra_layout)
        self._form = sg.Window(title, layout=layout, icon=APP_ICON, size=(960, 640), finalize=True)
        self._data = {}
        self.__dont_update = []
        if item:
            self.set_item(item)
        else:
            self.reset_item()

    def _updatedata(self):
        if self._item:
            self._data['-NAME-'] = self._item.name
            self._data['-CONDITION-'] = self._item.condition
        else:
            self._data['-NAME-'] = ''
            self._data['-CONDITION-'] = ''

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

    def dont_update(self, *keys):
        self.__dont_update += keys

    def set_item(self, item):
        assert(isinstance(item, Event))
        try:
            self._item = item.__class__(item.as_table())    # get an exact copy to mess with
        except ValueError:
            self._item = item                               # item was newly created: use it
        self._updatedata()

    def reset_item(self):
        self._item = None
        self._updatedata()

    def process_event(self, event, values):
        if values:
            self._data = values.copy()
            self._item.condition = self._data['-CONDITION-']
        if event in [sg.WIN_CLOSED, '-CANCEL-']:
            self._form.close()
            return False
        elif event == '-OK-':
            self._form.close()
            return True
        return None

    def run(self):
        self._updateform()
        while True:             # Event Loop
            event, values = self._form.read()
            ret = self.process_event(event, values)
            if ret is not None:
                if ret:
                    break
                else:
                    return None
            self._updateform()
        self._updateitem()
        self._form.close()
        return self._item


# end.
