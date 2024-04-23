# filesystem monitor event form

from os.path import normpath

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import APP_ICON32 as APP_ICON

from lib.forms.event import form_Event
from lib.items.event_fschange import FilesystemChangeEvent


# (extra) layout generator
def _form_layout():
    return [
        [sg.Frame(UI_FORM_SPECIFIC_PARAMS, [
            [ sg.T(UI_FORM_MONITOREDFSITEMS_SC), ],
            [ sg.Listbox([], key='-WATCH-', expand_x=True, expand_y=True), ],
            [
                sg.T(UI_FORM_ITEM_SC),
                sg.I(key='-ITEM-', expand_x=True),
                sg.FileBrowse(UI_BROWSE, key='-BROWSE_FILE-'),
            ],
            [ sg.CB(UI_FORM_RECURSIVE, key='-RECURSIVE-'), sg.Push(), sg.B(UI_ADD, key='-ADD-'), sg.B(UI_DEL, key='-DEL-'), ],
        ], expand_x=True, expand_y=True)]
    ]


# specialized subform
class form_FilesystemChangeEvent(form_Event):
    def __init__(self, conditions_available, item=None):
        if item:
            assert(isinstance(item, FilesystemChangeEvent))
        else:
            item = FilesystemChangeEvent()
        extra_layout = _form_layout()
        form_Event.__init__(self, UI_TITLE_FSCHANGEEVENT, conditions_available, extra_layout, item)
        self.dont_update('-BROWSE_FILE-')
        self._form['-WATCH-'].bind('<Double-Button-1>' , '+-dblclick-')
        if item:
            self._watch = item.watch.copy()
            self.set_item(item)
        else:
            self._watch = []
            self.reset_item()

    def _updatedata(self):
        form_Event._updatedata(self)
        self._data['-ITEM-'] = ''
        self._data['-WATCH-'] = self._item.watch.copy()
        self._watch = self._item.watch.copy()
        self._data['-RECURSIVE-'] = self._item.recursive

    def _updateitem(self):
        form_Event._updateitem(self)
        self._item.watch = self._watch.copy()
        self._item.recursive = self._data['-RECURSIVE-']

    def process_event(self, event, values):
        ret = super().process_event(event, values)
        if ret is None:
            if event == '-WATCH-+-dblclick-':
                self._data['-ITEM-'] = self._data['-WATCH-'][0]
            elif event == '-ADD-':
                item = normpath(self._data['-ITEM-'])
                if item and item not in self._watch:
                    self._watch.append(item)
            elif event == '-DEL-':
                item = self._data['-ITEM-']
                if item in self._watch:
                    self._watch = list(x for x in self._watch if x != item)
            self._data['-WATCH-'] = self._watch.copy()
        else:
            return ret


# end.
