# filesystem monitor event form

from os.path import normpath, exists

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import XMARK_ICON48 as XMARK_ICON

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
            [ sg.CB(UI_FORM_RECURSIVE, key='-RECURSIVE-'), sg.Push(), sg.B_ADD(UI_ADD, key='-ADD-'), sg.B_DEL(UI_DEL, key='-DEL-'), ],
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
            if item.watch:
                self._watch = item.watch.copy()
            else:
                self._watch = []
            self.set_item(item)
        else:
            self._watch = []
            self.reset_item()

    def _updatedata(self):
        form_Event._updatedata(self)
        self._data['-ITEM-'] = ''
        self._data['-WATCH-'] = self._item.watch.copy()
        if self._item.watch:
            self._watch = self._item.watch.copy()
        else:
            self._watch = []
        self._data['-RECURSIVE-'] = self._item.recursive

    def _updateitem(self):
        form_Event._updateitem(self)
        self._item.watch = self._watch.copy() or None
        self._item.recursive = self._data['-RECURSIVE-']

    def process_event(self, event, values):
        ret = super().process_event(event, values)
        if ret is None:
            if event == '-WATCH-+-dblclick-':
                self._data['-ITEM-'] = self._data['-WATCH-'][0]
            elif event == '-ADD-':
                item = normpath(self._data['-ITEM-'])
                try:
                    if exists(item) and item not in self._watch:
                        self._watch.append(item)
                    else:
                        sg.popup(UI_POPUP_INVALIDFILEORDIR, title=UI_POPUP_T_ERR, icon=XMARK_ICON)
                except Exception:
                    sg.popup(UI_POPUP_INVALIDFILEORDIR, title=UI_POPUP_T_ERR, icon=XMARK_ICON)
            elif event == '-DEL-':
                item = self._data['-ITEM-']
                if item in self._watch:
                    self._watch = list(x for x in self._watch if x != item)
            self._data['-WATCH-'] = self._watch.copy()
        else:
            return ret


# end.
