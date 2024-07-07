# Lua condition form

import re
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

import pygments.lexers
from chlorophyll import CodeView

from ..i18n.strings import *
from .ui import *

from ..utility import guess_typed_value, get_editor_theme

from .cond import form_Condition
from ..items.cond_lua import LuaScriptCondition


# regular expression for item name checking
_RE_VALIDNAME = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")


class form_LuaScriptCondition(form_Condition):

    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, LuaScriptCondition))
        else:
            item = LuaScriptCondition()
        super().__init__(UI_TITLE_LUACOND, tasks_available, item)

        # form data
        self._results = []

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # script section
        l_luaScript = ttk.Label(area, text=UI_FORM_SCRIPT)
        cv_luaScript = CodeView(area, pygments.lexers.LuaLexer, font='TkFixedFont', height=10, color_scheme=get_editor_theme())
        sep1 = ttk.Separator(area)

        # results section
        l_luaVars = ttk.Label(area, text=UI_FORM_EXPECTRESULTS)
        # build a scrolled frame for the treeview
        sftv_luaVars = ttk.Frame(area)
        tv_luaVars = ttk.Treeview(sftv_luaVars, columns=('variable', 'value'), show='headings', height=10)
        tv_luaVars.heading('variable', anchor=tk.W, text=UI_FORM_VARNAME)
        tv_luaVars.heading('value', anchor=tk.W, text=UI_FORM_VARVALUE)
        sb_luaVars = ttk.Scrollbar(sftv_luaVars, orient=tk.VERTICAL, command=tv_luaVars.yview)
        tv_luaVars.configure(yscrollcommand=sb_luaVars.set)
        tv_luaVars.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_luaVars.pack(side=tk.RIGHT, fill=tk.Y)
        l_varName = ttk.Label(area, text=UI_FORM_VARNAME_SC)
        e_varName = ttk.Entry(area)
        l_varValue = ttk.Label(area, text=UI_FORM_NEWVALUE_SC)
        e_varValue = ttk.Entry(area)
        b_addVar = ttk.Button(area, text=UI_UPDATE, width=BUTTON_STANDARD_WIDTH, command=self.add_var)
        b_delVar = ttk.Button(area, text=UI_DEL, width=BUTTON_STANDARD_WIDTH, command=self.del_var)
        ck_expectAll = ttk.Checkbutton(area, text=UI_FORM_MATCHALLRESULTS)

        # extra delay section
        area_checkafter = ttk.Frame(area)
        l_checkAfter = ttk.Label(area_checkafter, text=UI_FORM_EXTRADELAY_SC)
        e_checkAfter = ttk.Entry(area_checkafter)
        l_checkAfterSeconds = ttk.Label(area_checkafter, text=UI_TIME_SECONDS)

        # bind double click to variable recall
        tv_luaVars.bind('<Double-Button-1>', lambda _: self.recall_var())

        # arrange items in frame
        l_checkAfter.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_checkAfter.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        l_checkAfterSeconds.grid(row=0, column=2, sticky=tk.W, padx=PAD, pady=PAD)
        area_checkafter.columnconfigure(1, weight=1)

        sep2 = ttk.Separator(area)

        # arrange top items in the grid
        l_luaScript.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=PAD, pady=PAD)
        cv_luaScript.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW, padx=PAD, pady=PAD)
        sep1.grid(row=2, column=0, columnspan=4, sticky=tk.EW, pady=PAD)
        area_checkafter.grid(row=3, column=0, columnspan=4, sticky=tk.EW)
        sep2.grid(row=4, column=0, columnspan=4, sticky=tk.EW, pady=PAD)
        l_luaVars.grid(row=10, column=0, columnspan=4, sticky=tk.W, padx=PAD, pady=PAD)
        sftv_luaVars.grid(row=11, column=0, columnspan=4, sticky=tk.NSEW, padx=PAD, pady=PAD)
        l_varName.grid(row=12, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        l_varValue.grid(row=12, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        e_varName.grid(row=13, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        e_varValue.grid(row=13, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_addVar.grid(row=13, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        b_delVar.grid(row=13, column=3, sticky=tk.EW, padx=PAD, pady=PAD)
        ck_expectAll.grid(row=20, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.rowconfigure(1, weight=1)
        area.rowconfigure(11, weight=1)
        area.columnconfigure(0, weight=1)
        area.columnconfigure(1, weight=1)

        # bind data to widgets
        self.data_bind('luavar_selection', tv_luaVars)
        self.data_bind('script', cv_luaScript, TYPE_STRING)
        self.data_bind('varname', e_varName, TYPE_STRING, lambda x: x == '' or _RE_VALIDNAME.match(x))
        self.data_bind('newvalue', e_varValue, TYPE_STRING)
        self.data_bind('expect_all', ck_expectAll)
        self.data_bind('check_after', e_checkAfter, TYPE_INT, lambda x: x >= 0)

        # propagate widgets that need to be accessed
        self._tv_vars = tv_luaVars

        # update the form
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
                self._updatedata()
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
        self._updatedata()
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
        self._item.script = self.data_get('script').strip() or ""
        self._item.expect_all = self.data_get('expect_all') or None
        self._item.check_after = self.data_get('check_after') or None
        e = {}
        for l in self._results:
            e[l[0]] = guess_typed_value(str(l[1]))
        self._item.expected_results = e or None
        return super()._updatedata()

    def _updateform(self):
        self.data_set('script', self._item.script)
        self.data_set('expect_all', self._item.expect_all or False)
        self.data_set('check_after', self._item.check_after or '')
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
