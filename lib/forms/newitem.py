# form to select what type of new item should be created

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import APP_ICON32 as APP_ICON

from lib.items.item import ALL_AVAILABLE_ITEMS


# layout generator (fixed)
def _form_layout():
    return [
        [ sg.Frame(
            UI_FORM_ITEMTYPE,
            [
                [sg.Radio(ITEM_TASK, 'item', True, key='-TASK-')],
                [sg.Radio(ITEM_COND, 'item', False, key='-CONDITION-')],
                [sg.Radio(ITEM_EVENT, 'item', False, key='-EVENT-')],
            ],
            expand_x=True,
        ) ],
        [ sg.T(UI_FORM_ITEMSUBTYPES) ],
        [ sg.Table(
            auto_size_columns=True,
            headings=[UI_FORM_ITEM, 'ITEM_CODE'],
            visible_column_map=(True, False),
            values=[],
            key='-SUBTYPES-',
            num_rows=5,
            justification='left',
            expand_x=True, expand_y=True,
        ) ],

        # form control section
        [ sg.Push(), sg.B_OK(UI_OK, key='-OK-'), sg.B_CANCEL(UI_CANCEL, key='-CANCEL-') ],
    ]


# form class: this form is fixed and will not be derived
class form_NewItem(object):
    def __init__(self):
        self._form = sg.Window(
            UI_TITLE_NEWITEM,
            layout=_form_layout(),
            icon=APP_ICON,
            size=(640, 400),
            finalize=True,
        )
        # self._form['-SUBTYPES-'].bind('<Button-1>' , '+-click-')
        self._form['-TASK-'].bind('<Button-1>' , '+-click-')
        self._form['-CONDITION-'].bind('<Button-1>' , '+-click-')
        self._form['-EVENT-'].bind('<Button-1>' , '+-click-')
        self.__dont_update = []
        self._subtypes = []
        self._subtypes_display = []
        self._type = 'task'
        self._data = {}
        self._updatedata()

    def _updatedata(self):
        if self._type == 'task':
            self._data['-TASK-'] = True
            self._data['-CONDITION-'] = False
            self._data['-EVENT-'] = False
        elif self._type == 'cond':
            self._data['-TASK-'] = False
            self._data['-CONDITION-'] = True
            self._data['-EVENT-'] = False
        elif self._type == 'event':
            self._data['-TASK-'] = False
            self._data['-CONDITION-'] = False
            self._data['-EVENT-'] = True
        else:
            raise ValueError("Invalid choice for item type")
        self._subtypes = list(x for x in ALL_AVAILABLE_ITEMS
                              if x[0].startswith('%s:' % self._type)
                              and x[3].available)
        self._subtypes_display = list([x[1], x[0]] for x in self._subtypes)
        self._data['-SUBTYPES-'] = self._subtypes_display.copy()

    def _updateform(self):
        for k in self._data:
            if k not in self.__dont_update:
                v = self._data[k]
                if v is None:
                    v = ''
                self._form[k].update(v)
        self._form.refresh()

    def dont_update(self, *keys):
        self.__dont_update += keys

    def run(self):
        ok = False
        self._updateform()
        while True:             # Event Loop
            event, values = self._form.read()
            self._data = values
            if event in [sg.WIN_CLOSED, '-CANCEL-']:
                self._form.close()
                break
            elif event == '-TASK-+-click-':
                self._type = 'task'
            elif event == '-CONDITION-+-click-':
                self._type = 'cond'
            elif event == '-EVENT-+-click-':
                self._type = 'event'
            elif event == '-OK-':
                self._form.close()
                ok = True
                break
            self._updatedata()
            self._updateform()

        if ok:
            choice = self._data['-SUBTYPES-']
            if choice:
                return self._type, self._subtypes[choice[0]][2]
            else:
                return None
        else:
            return None

# end.
