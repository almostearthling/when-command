# Lua condition form

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import XMARK_ICON48 as XMARK_ICON

from lib.utility import guess_typed_value
from lib.forms.cond import form_Condition
from lib.items.cond_lua import LuaScriptCondition

import re


# regular expression for item name checking
_RE_VALIDNAME = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")


# (extra) layout generator
def _form_layout():
    return [
        [ sg.Frame(UI_FORM_EXTRADELAY, [[
            sg.T(UI_FORM_EXTRADELAYSPEC),
            sg.I(key='-CHECK_AFTER-', expand_x=True),
            sg.Combo([UI_TIME_SECONDS, UI_TIME_MINUTES, UI_TIME_HOURS], default_value=UI_TIME_SECONDS, key='-CHECK_AFTER_UNIT-'),
        ]], expand_x=True, expand_y=False) ],
        [ sg.Frame(UI_FORM_SCRIPT, [[
            sg.Multiline(key='-SCRIPT-', size=(None, 5), font='Courier 10', expand_x=True, expand_y=True),
        ]], expand_x=True, expand_y=True) ],
        [ sg.Frame(UI_FORM_EXPECTRESULTS, [
            [ sg.T(UI_FORM_VARIABLES_SC) ],
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
        ], expand_x=True)],
    ]


# specialized subform
class form_LuaScriptCondition(form_Condition):
    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, LuaScriptCondition))
        else:
            item = LuaScriptCondition()
        extra_layout = _form_layout()
        form_Condition.__init__(self, UI_TITLE_LUACOND, tasks_available, extra_layout, item)
        self._form['-LUA_RESULTS-'].bind('<Double-Button-1>' , '+-dblclick-')
        self._results = []
        if item:
            self.set_item(item)
        else:
            self.reset_item()
        self.add_checks(
            ('-CHECK_AFTER-', UI_FORM_EXTRADELAYSPEC, lambda x: int(x) > 0),
        )

    def _updatedata(self):
        form_Condition._updatedata(self)
        self._data['-LUAVAR_NAME-'] = ''
        self._data['-LUAVAR_VALUE-'] = ''
        if self._item:
            self._data['-SCRIPT-'] = self._item.script
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
            self._data['-LUAVAR_MATCH_ALL-'] = self._item.expect_all
            self._data['-LUA_RESULTS-'] = []
            self._results = []
            for k in self._item.expected_results:
                self._data['-LUA_RESULTS-'].append([k, self._item.expected_results[k]])
                self._results.append([k, self._item.expected_results[k]])
        else:
            self._data['-SCRIPT-'] = ''
            self._data['-LUAVAR_MATCH_ALL-'] = False
            self._data['-LUA_RESULTS-'] = []

    def _updateitem(self):
        form_Condition._updateitem(self)
        self._item.script = self._data['-SCRIPT-']
        self._item.expect_all = self._data['-LUAVAR_MATCH_ALL-']
        self._item.expected_results = {}
        for l in self._results:
            self._item.expected_results[l[0]] = guess_typed_value(str(l[1]))
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
            self._data['-LUA_RESULTS-'] = []
            for l in self._results:
                self._data['-LUA_RESULTS-'].append(l.copy())
        else:
            return ret


# end.
