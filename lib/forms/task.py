# base task form

from ..i18n.strings import *
from ..repocfg import AppConfig

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from .ui import *

from ..items.task import Task

import re


# regular expression for item name checking
_RE_VALIDNAME = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")


# task box base class: since this is the class that will be used in derived
# forms too, in order to avoid variable name conflicts, all variable names
# used here are prefixed with '@': agreeing that base values are prefixed
# and specific values are not, consistent names can be used in derived forms
# without conflicts
class form_Task(ApplicationForm):

    def __init__(self, title, item=None):
        size = AppConfig.get('SIZE_EDITOR_FORM')
        bbox = (BBOX_OK, BBOX_CANCEL)
        super().__init__(title, size, None, bbox)

        # build the UI
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        l_itemName = ttk.Label(area, text=UI_FORM_NAME_SC)
        e_itemName = ttk.Entry(area)
        sep = ttk.Separator(area)
        self._sub_contents = ttk.Frame(area)
        self._sub_contents.rowconfigure(0, weight=1)
        self._sub_contents.columnconfigure(0, weight=1)
        l_itemName.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_itemName.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        sep.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=PAD)
        self._sub_contents.grid(row=99, column=0, columnspan=2, sticky=tk.EW)
        area.rowconfigure(index=99, weight=1)
        area.columnconfigure(1, weight=1)
        self.data_bind('@name', e_itemName, TYPE_STRING, lambda x: _RE_VALIDNAME.match(x))

        if item:
            self.set_item(item)
        else:
            self.reset_item()
        self.changed = False


    # contents is the root for slave widgets
    @property
    def contents(self):
        return self._sub_contents


    def _updateform(self):
        if self._item:
            self.data_set('@name', self._item.name)
        else:
            self.data_set('@name', '')


    # the data update utility loads data into the item
    def _updatedata(self):
        name = self.data_get('@name')
        if name is not None:
            self._item.name = name


    # set and remove the associated item
    def set_item(self, item):
        assert(isinstance(item, Task))
        try:
            self._item = item.__class__(item.as_table())    # get an exact copy to mess with
        except ValueError:
            self._item = item                               # item was newly created: use it

    def reset_item(self):
        self._item = None


    # command button reactions: cancel deletes the current item so that None
    # is returned upon dialog close, while ok finalizes item initialization
    # and lets the run() function return a configured item
    def exit_cancel(self):
        self._item = None
        return super().exit_cancel()

    def exit_ok(self):
        name = self.data_get('@name')
        if name is not None:
            self._updatedata()
            return super().exit_ok()
        else:
            messagebox.showerror(UI_POPUP_T_ERR, UI_POPUP_INVALIDITEMNAME)


    # main loop: returns the current item if any
    def run(self):
        super().run()
        return self._item


# end.
