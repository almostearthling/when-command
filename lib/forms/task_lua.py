# Lua task form

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import XMARK_ICON48 as XMARK_ICON

from lib.utility import guess_typed_value
from lib.forms.task import form_Task
from lib.items.task_lua import LuaScriptTask

import re


# regular expression for item name checking
_RE_VALIDNAME = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")


# (extra) layout generator
def _form_layout():
    return [
        [ sg.Frame(UI_FORM_SCRIPT, [[
            sg.Multiline(key='-SCRIPT-', size=(None, 5), font='Courier 10', expand_x=True, expand_y=True),
        ]], expand_x=True, expand_y=True) ],

        [ sg.Frame(UI_FORM_EXPECTRESULTS, [
            [ sg.T(UI_FORM_VARIABLES_SC, ) ],
            [ sg.Table(
                [['' for x in range(2)] for y in range(3)],
                headings=[UI_FORM_NAME, UI_FORM_VALUE],
                key='-LUA_RESULTS-',
                num_rows=3,
                justification='left',
                expand_x=True,
            ) ],
            [
                sg.Column([[ sg.T(UI_FORM_VARNAME_SC) ], [ sg.I(key='-LUAVAR_NAME-', expand_x=True) ]], expand_x=True),
                sg.Column([[ sg.T(UI_FORM_NEWVALUE_SC) ], [ sg.I(key='-LUAVAR_VALUE-', expand_x=True) ]], expand_x=True),
            ],
            [
                sg.CB(UI_FORM_MATCHALLRESULTS, key='-LUAVAR_MATCH_ALL-', default=False),
                sg.Push(),
                sg.B_ADD(UI_UPDATE, key='-UPDATE_LUAVAR-'),
                sg.B_DEL(UI_DEL, key='-DELETE_LUAVAR-'),
            ],
        ], expand_x=True) ],
    ]


# specialized subform
class form_LuaScriptTask(form_Task):
    def __init__(self, item=None):
        if item:
            assert(isinstance(item, LuaScriptTask))
        else:
            item = LuaScriptTask()
        extra_layout = _form_layout()
        form_Task.__init__(self, UI_TITLE_LUATASK, extra_layout, item)
        self._form['-LUA_RESULTS-'].bind('<Double-Button-1>' , '+-dblclick-')
        self._results = []

    def _updatedata(self):
        form_Task._updatedata(self)
        self._data['-LUAVAR_NAME-'] = ''
        self._data['-LUAVAR_VALUE-'] = ''
        if self._item:
            self._data['-SCRIPT-'] = self._item.script
            self._data['-LUAVAR_MATCH_ALL-'] = self._item.expect_all
            self._data['-LUA_RESULTS-'] = []
            self._results = []
            if self._item.expected_results:
                for k in self._item.expected_results:
                    self._data['-LUA_RESULTS-'].append([k, self._item.expected_results[k]])
                    self._results.append([k, self._item.expected_results[k]])
        else:
            self._data['-SCRIPT-'] = ''
            self._data['-LUAVAR_MATCH_ALL-'] = False
            self._data['-LUA_RESULTS-'] = []

    def _updateitem(self):
        form_Task._updateitem(self)
        self._item.script = self._data['-SCRIPT-']
        self._item.expect_all = self._data['-LUAVAR_MATCH_ALL-']
        e = {}
        for l in self._results:
            e[l[0]] = guess_typed_value(str(l[1]))
        self._item.expected_results = e or None

    def process_event(self, event, values):
        ret = super().process_event(event, values)
        if ret is None:
            if event == '-LUA_RESULTS-+-dblclick-':
                self._data['-LUAVAR_NAME-'] = self._results[self._data['-LUA_RESULTS-'][0]][0]
                self._data['-LUAVAR_VALUE-'] = self._results[self._data['-LUA_RESULTS-'][0]][1]
            elif event == '-UPDATE_LUAVAR-':
                if self._data['-LUAVAR_NAME-'] and self._data['-LUAVAR_VALUE-']:
                    if _RE_VALIDNAME.match(self._data['-LUAVAR_NAME-']):
                        r = list(e for e in self._results if e[0] != self._data['-LUAVAR_NAME-'])
                        r.append([self._data['-LUAVAR_NAME-'], self._data['-LUAVAR_VALUE-']])
                        self._results = r
                    else:
                        sg.popup(UI_POPUP_INVALIDVARNAME, title=UI_POPUP_T_ERR, icon=XMARK_ICON)
            elif event == '-DELETE_LUAVAR-':
                if self._data['-LUAVAR_NAME-']:
                    r = list(e for e in self._results if e[0] != self._data['-LUAVAR_NAME-'])
                    self._results = r
            # ...
            self._data['-LUA_RESULTS-'] = []
            for l in self._results:
                self._data['-LUA_RESULTS-'].append(l.copy())
        else:
            return ret


# end.
