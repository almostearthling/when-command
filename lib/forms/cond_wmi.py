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
from ..items.cond_wmi import WMICondition


# regular expression for field checking
_RE_VALIDNAME = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")
_XLATE_OPERATORS = {
    '=': 'eq',
    '==': 'eq',
    '!=': 'neq',
    '<>': 'neq',
    '>': 'gt',
    '<': 'lt',
    '>=': 'ge',
    '<=': 'le',
    '~': 'match',
    'eq': 'eq',
    'neq': 'neq',
    'gt': 'gt',
    'lt': 'lt',
    'ge': 'ge',
    'le': 'le',
    'match': 'match',
}
_ALLOWED_OPERATORS = _XLATE_OPERATORS.keys()


class form_WMICondition(form_Condition):

    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, WMICondition))
        else:
            item = WMICondition()
        super().__init__(UI_TITLE_LUACOND, tasks_available, item)

        # form data
        self._results = []

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = UI_TITLE_WMICOND

        # script section
        l_wmiQuery = ttk.Label(area, text=UI_FORM_WMI_QUERY_SC)
        cv_wmiQuery = CodeView(area, pygments.lexers.LuaLexer, font='TkFixedFont', height=10, color_scheme=get_editor_theme())
        sep1 = ttk.Separator(area)

        # results section
        l_wmiResults = ttk.Label(area, text=UI_FORM_EXPECTRESULTS)
        # build a scrolled frame for the treeview
        sftv_wmiResults = ttk.Frame(area)
        tv_wmiResults = ttk.Treeview(sftv_wmiResults, columns=('index', 'field', 'operator', 'value'), show='headings', height=10)
        tv_wmiResults.heading('index', anchor=tk.W, text=UI_FORM_INDEX)
        tv_wmiResults.heading('field', anchor=tk.W, text=UI_FORM_FIELD)
        tv_wmiResults.heading('operator', anchor=tk.W, text=UI_FORM_OPERATOR)
        tv_wmiResults.heading('value', anchor=tk.W, text=UI_FORM_VALUE)
        sb_wmiResults = ttk.Scrollbar(sftv_wmiResults, orient=tk.VERTICAL, command=tv_wmiResults.yview)
        tv_wmiResults.configure(yscrollcommand=sb_wmiResults.set)
        tv_wmiResults.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_wmiResults.pack(side=tk.RIGHT, fill=tk.Y)
        l_resultIndex = ttk.Label(area, text=UI_FORM_INDEX_SC)
        e_resultIndex = ttk.Entry(area)
        l_resultField = ttk.Label(area, text=UI_FORM_VALUE_SC)
        e_resultField = ttk.Entry(area)
        l_resultOperator = ttk.Label(area, text=UI_FORM_VALUE_SC)
        e_resultOperator = ttk.Entry(area)
        l_resultValue = ttk.Label(area, text=UI_FORM_VALUE_SC)
        e_resultValue = ttk.Entry(area)
        b_addCheck = ttk.Button(area, text=UI_UPDATE, width=BUTTON_STANDARD_WIDTH, command=self.add_var)
        b_delCheck = ttk.Button(area, text=UI_DEL, width=BUTTON_STANDARD_WIDTH, command=self.del_var)
        ck_checkAll = ttk.Checkbutton(area, text=UI_FORM_MATCHALLRESULTS)

        # extra delay section
        area_commonparams = ttk.Frame(area)
        l_checkAfter = ttk.Label(area_commonparams, text=UI_FORM_EXTRADELAY_SC)
        e_checkAfter = ttk.Entry(area_commonparams)
        l_checkAfterSeconds = ttk.Label(area_commonparams, text=UI_TIME_SECONDS)
        ck_ignorePersistentSuccess = ttk.Checkbutton(area_commonparams, text=UI_FORM_IGNOREPERSISTSUCCESS)

        # bind double click to variable recall
        tv_wmiResults.bind('<Double-Button-1>', lambda _: self.recall_var())

        # arrange items in frame
        l_checkAfter.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_checkAfter.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        l_checkAfterSeconds.grid(row=0, column=2, sticky=tk.W, padx=PAD, pady=PAD)
        ck_ignorePersistentSuccess.grid(row=2, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        area_commonparams.columnconfigure(1, weight=1)

        sep2 = ttk.Separator(area)

        # arrange top items in the grid
        l_wmiQuery.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=PAD, pady=PAD)
        cv_wmiQuery.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW, padx=PAD, pady=PAD)
        sep1.grid(row=2, column=0, columnspan=4, sticky=tk.EW, pady=PAD)
        area_commonparams.grid(row=3, column=0, columnspan=4, sticky=tk.EW)
        sep2.grid(row=4, column=0, columnspan=4, sticky=tk.EW, pady=PAD)
        l_wmiResults.grid(row=10, column=0, columnspan=4, sticky=tk.W, padx=PAD, pady=PAD)
        sftv_wmiResults.grid(row=11, column=0, columnspan=4, sticky=tk.NSEW, padx=PAD, pady=PAD)
        l_resultIndex.grid(row=12, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        l_resultField.grid(row=12, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        l_resultOperator.grid(row=12, column=2, sticky=tk.W, padx=PAD, pady=PAD)
        l_resultValue.grid(row=12, column=3, sticky=tk.W, padx=PAD, pady=PAD)
        e_resultIndex.grid(row=13, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        e_resultField.grid(row=13, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        e_resultOperator.grid(row=13, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        e_resultValue.grid(row=13, column=3, sticky=tk.EW, padx=PAD, pady=PAD)
        b_addCheck.grid(row=13, column=4, sticky=tk.EW, padx=PAD, pady=PAD)
        b_delCheck.grid(row=13, column=5, sticky=tk.EW, padx=PAD, pady=PAD)
        ck_checkAll.grid(row=20, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.rowconfigure(1, weight=1)
        area.rowconfigure(11, weight=1)
        area.columnconfigure(1, weight=1)
        area.columnconfigure(3, weight=2)

        # bind data to widgets
        self.data_bind('result_selection', tv_wmiResults)
        self.data_bind('query', cv_wmiQuery, TYPE_STRING)
        self.data_bind('index', e_resultIndex, TYPE_STRING, lambda x: x == "" or int(x) >= 0)
        self.data_bind('field', e_resultField, TYPE_STRING, lambda x: _RE_VALIDNAME.match(x))
        self.data_bind('operator', e_resultOperator, TYPE_STRING, lambda x: x in _ALLOWED_OPERATORS)
        self.data_bind('value', e_resultValue, TYPE_STRING)
        self.data_bind('check_all', ck_checkAll)
        self.data_bind('check_after', e_checkAfter, TYPE_INT, lambda x: x >= 0)
        self.data_bind('ignore_persistent_success', ck_ignorePersistentSuccess)

        # propagate widgets that need to be accessed
        self._tv_results = tv_wmiResults

        # update the form
        self._updateform()

    def add_check(self):
        if self.data_get('index') == "":
            index = None
        else:
            try:
                index = int(self.data_get('index'))
                if index < 0:
                    raise ValueError
            except ValueError:
                index = -1
        field = self.data_get('field')
        operator = _XLATE_OPERATORS.get(self.data_get('operator'), None)
        value = self.data_get('value')
        if index < 0:
            messagebox.showerror(UI_POPUP_T_ERR, UI_POPUP_INVALIDINDEX)
            return
        if not _RE_VALIDNAME.match(field):
            messagebox.showerror(UI_POPUP_T_ERR, UI_POPUP_INVALIDFIELD)
            return
        if operator is None:
            messagebox.showerror(UI_POPUP_T_ERR, UI_POPUP_INVALIDOPERATOR)
            return
        if not value:
            messagebox.showerror(UI_POPUP_T_ERR, UI_POPUP_EMPTYCHECKVALUE)
            return
        self._results = list(x for x in self._results if x[0] != index and x[1] != field)
        self._results.append([index, field, operator, value])
        self._results.sort(key=lambda x: (x[0], x[1]))
        e = []
        for x in self._results:
            e.append({
                'index': index,
                'field': field,
                'operator': operator,
                'value': value,
            })
        self._item.result_check = e or None
        self._updatedata()
        self._updateform()
    
    def del_check(self):
        entry = self.data_get('result_selection')
        index = entry[0]
        field = entry[1]
        operator = entry[2]
        value = entry[3]
        self._results = list(
            x for x in self._results
            if x[0] == index
            and x[1] == field
            # and x[2] == operator
            # and x[3] == value
        )
        e = []
        for x in self._results:
            e.append({
                'index': index,
                'field': field,
                'operator': operator,
                'value': value,
            })
        self._item.result_check = e or None
        self.data_set('index', index)
        self.data_set('field', field)
        self.data_set('operator', operator)
        self.data_set('value', value)
        self._updatedata()
        self._updateform()

    def recall_check(self):
        entry = self.data_get('result_selection')
        index = entry[0]
        field = entry[1]
        operator = entry[2]
        value = entry[3]
        self.data_set('index', index)
        self.data_set('field', field)
        self.data_set('operator', operator)
        self.data_set('value', value)

    def _updatedata(self):
        self._item.query = self.data_get('query').strip() or ""
        self._item.result_check_all = self.data_get('expect_all') or None
        self._item.check_after = self.data_get('check_after') or None
        self._item.recur_after_failed_check = self.data_get('ignore_persistent_success') or None
        e = []
        for l in self._results:
            e[l[0]] = guess_typed_value(str(l[1]))
        self._item.expected_results = e or None
        return super()._updatedata()

    def _updateform(self):
        self.data_set('query', self._item.query)
        self.data_set('check_all', self._item.result_check_all or False)
        self.data_set('check_after', self._item.check_after or 0)
        self.data_set('ignore_persistent_success', self._item.recur_after_failed_check or False)
        self.data_set('index')
        self.data_set('field')
        self.data_set('operator')
        self.data_set('value')
        self._results = []
        if self._item.result_check:
            for e in self._item.result_check:
                self._results.append([
                    e.get('index', ""),
                    e.get('field'),
                    e.get('operator'),
                    e.get('value', ""),
                ])
        self._results.sort(key=lambda x: (x[0], x[1]))
        self._tv_results.delete(*self._tv_results.get_children())
        for entry in self._results:
            self._tv_results.insert('', iid="%s-%s" % (entry[0], entry[1]), values=entry, index=tk.END)
        return super()._updateform()



# end.
