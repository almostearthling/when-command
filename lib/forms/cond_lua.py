# Lua condition form

from ..i18n.strings import *

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

import pygments.lexers
from chlorophyll import CodeView

from ..utility import guess_typed_value, get_editor_theme

from .ui import *

from .cond import form_Condition
from ..items.cond_lua import LuaScriptCondition

import re


# regular expression for item name checking
_RE_VALIDNAME = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")


class form_LuaScriptCondition(form_Condition):

    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, LuaScriptCondition))
        else:
            item = LuaScriptCondition()
        super().__init__(UI_TITLE_LUACOND, tasks_available, item)

        self._results = []

        # this area hosts other panes, each with custom grid layout, and the
        # separators that act as borders between the sections
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        area.columnconfigure(0, weight=1)
        PAD = WIDGET_PADDING_PIXELS

        # script
        l_luaScript = ttk.Label(area, text=UI_FORM_SCRIPT)
        cv_luaScript = CodeView(area, pygments.lexers.LuaLexer, font='TkFixedFont', height=8, color_scheme=get_editor_theme())
        self.data_bind('script', cv_luaScript, TYPE_STRING)
        sep1 = ttk.Separator(area)

        l_luaVars = ttk.Label(area, text=UI_FORM_EXPECTRESULTS)
        tv_luaVars = ttk.Treeview(area, columns=('variable', 'value'), show='headings', height=5)
        tv_luaVars.heading('variable', anchor=tk.W, text=UI_FORM_VARNAME)
        tv_luaVars.heading('value', anchor=tk.W, text=UI_FORM_VARVALUE)
        self._tv_vars = tv_luaVars
        self.data_bind('luavar_selection', tv_luaVars)

        # bind double click to variable recall
        self._tv_vars.bind('<Double-Button-1>', lambda _: self.recall_var())

        l_varName = ttk.Label(area, text=UI_FORM_VARNAME_SC)
        e_varName = ttk.Entry(area)
        l_varValue = ttk.Label(area, text=UI_FORM_NEWVALUE_SC)
        e_varValue = ttk.Entry(area)
        b_addVar = ttk.Button(area, text=UI_UPDATE, width=BUTTON_STANDARD_WIDTH, command=self.add_var)
        b_delVar = ttk.Button(area, text=UI_DEL, width=BUTTON_STANDARD_WIDTH, command=self.del_var)
        self.data_bind('varname', e_varName, TYPE_STRING, lambda x: x == '' or _RE_VALIDNAME.match(x))
        self.data_bind('newvalue', e_varValue, TYPE_STRING)

        ck_expectAll = ttk.Checkbutton(area, text=UI_FORM_MATCHALLRESULTS)
        self.data_bind('expect_all', ck_expectAll)

        l_luaScript.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=PAD, pady=PAD)
        cv_luaScript.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW, padx=PAD, pady=PAD)
        sep1.grid(row=2, column=0, columnspan=4, sticky=tk.EW, padx=PAD, pady=PAD)

        l_luaVars.grid(row=10, column=0, columnspan=4, sticky=tk.W, padx=PAD, pady=PAD)
        tv_luaVars.grid(row=11, column=0, columnspan=4, sticky=tk.NSEW, padx=PAD, pady=PAD)
        
        l_varName.grid(row=12, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        l_varValue.grid(row=12, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        e_varName.grid(row=13, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        e_varValue.grid(row=13, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_addVar.grid(row=13, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        b_delVar.grid(row=13, column=3, sticky=tk.EW, padx=PAD, pady=PAD)

        ck_expectAll.grid(row=20, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        area.rowconfigure(1, weight=1)
        area.rowconfigure(11, weight=1)
        area.columnconfigure(0, weight=1)
        area.columnconfigure(1, weight=1)

        self._updateform()

    def add_var(self):
        name = self.data_get('varname')
        value = self.data_get('newvalue')
        if _RE_VALIDNAME.match(name):
            if not value:
                messagebox.showerror(UI_POPUP_T_ERR, UI_POPUP_EMPTYVARVALUE)
            else:
                self._results = list(entry for entry in self._results if entry[0] != name)
                self._results.append([name, value])
                e = {}
                for l in self._results:
                    e[l[0]] = str(l[1])
                self._item.expected_results = e or None
                self._results.sort(key=lambda x: x[0])
                self._updateform()
        else:
            messagebox.showerror(UI_POPUP_T_ERR, UI_POPUP_INVALIDVARNAME)

    def del_var(self):
        entry = self.data_get('luavar_selection')
        name = entry[0]
        value = entry[1]
        self._results = list(entry for entry in self._results if entry[0] != name)
        e = {}
        for l in self._results:
            e[l[0]] = str(l[1])
        self._item.expected_results = e or None
        # first update the form data, then recall the variable in the input
        # fields, so that the user can re-add the variable again if needed
        self._updateform()
        self.data_set('varname', name)
        self.data_set('newvalue', value)

    def recall_var(self):
        entry = self.data_get('luavar_selection')
        name = entry[0]
        value = entry[1]
        self.data_set('varname', name)
        self.data_set('newvalue', value)


    def _updatedata(self):
        self._item.script = self.data_get('script') or ""
        self._item.expect_all = self.data_get('expect_all') or None
        e = {}
        for l in self._results:
            e[l[0]] = guess_typed_value(str(l[1]))
        self._item.expected_results = e or None
        return super()._updatedata()
    
    def _updateform(self):
        self.data_set('script', self._item.script)
        self.data_set('expect_all', self._item.expect_all)
        self.data_set('varname')
        self.data_set('newvalue')
        self._results = []
        if self._item.expected_results:
            for k in self._item.expected_results:
                self._results.append([k, self._item.expected_results[k]])
        self._results.sort(key=lambda x: x[0])
        self._tv_vars.delete(*self._tv_vars.get_children())
        for entry in self._results:
            self._tv_vars.insert('', iid="%s-%s" % (entry[0], entry[1]), values=entry, index=tk.END)
        return super()._updateform()


# end.
