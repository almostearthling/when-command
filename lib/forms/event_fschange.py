# filesystem monitor event form

from os.path import normpath, exists

from ..i18n.strings import *

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog

from .ui import *

from .event import form_Event
from ..items.event_fschange import FilesystemChangeEvent


# specialized subform
class form_FilesystemChangeEvent(form_Event):

    def __init__(self, conditions_available, item=None):
        if item:
            assert(isinstance(item, FilesystemChangeEvent))
        else:
            item = FilesystemChangeEvent()
        super().__init__(UI_TITLE_FSCHANGEEVENT, conditions_available, item)

        self._watch = self._item.watch.copy() if self._item.watch else []

        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        ck_recursive = ttk.Checkbutton(area, text=UI_FORM_RECURSIVE)
        l_monitored = ttk.Label(area, text=UI_FORM_MONITOREDFSITEMS_SC)
        tv_monitored = ttk.Treeview(area, columns=('seq', 'items'), show='', displaycolumns=(1,), height=5)
        l_monEntry = ttk.Label(area, text=UI_FORM_ITEM_SC)
        e_monEntry = ttk.Entry(area)
        b_browse = ttk.Button(area, text=UI_BROWSE, command=self.browse_fsitem)
        b_addEntry = ttk.Button(area, text=UI_ADD, width=BUTTON_STANDARD_WIDTH, command=self.add_fsitem)
        b_delEntry = ttk.Button(area, text=UI_DEL, width=BUTTON_STANDARD_WIDTH, command=self.del_fsitem)

        ck_recursive.grid(row=0, column=0, columnspan=5, sticky=tk.W, padx=PAD, pady=PAD)
        l_monitored.grid(row=1, column=0, columnspan=5, sticky=tk.W, padx=PAD, pady=PAD)
        tv_monitored.grid(row=2, column=0, columnspan=5, sticky=tk.NSEW, padx=PAD, pady=PAD)
        l_monEntry.grid(row=3, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_monEntry.grid(row=3, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_browse.grid(row=3, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        b_addEntry.grid(row=3, column=3, sticky=tk.EW, padx=PAD, pady=PAD)
        b_delEntry.grid(row=3, column=4, sticky=tk.EW, padx=PAD, pady=PAD)
        self._tv_monitored = tv_monitored
        self._tv_monitored.bind('<ButtonRelease-1>', lambda _: self.recall_fsitem())
        self.data_bind('recursive', ck_recursive)
        # the following might be actually too strict
        # self.data_bind('item_monitor', e_monEntry, TYPE_STRING, exists)
        self.data_bind('item_monitor', e_monEntry, TYPE_STRING)
        self.data_bind('item_selection', tv_monitored)

        area.columnconfigure(1, weight=1)
        area.rowconfigure(2, weight=1)

        self._updateform()


    def _updateform(self):
        self.data_set('recursive', self._item.recursive)
        self._tv_monitored.delete(*self._tv_monitored.get_children())
        idx = 0
        for entry in self._watch:
            self._tv_monitored.insert('', iid=idx, values=(idx, entry), index=tk.END)
            idx += 1
        return super()._updateform()

    def _updatedata(self):
        self._item.recursive = self.data_get('recursive')
        e = []
        for entry in self._watch:
            e.append(entry)
        self._item.watch = e or None
        return super()._updatedata()

    def recall_fsitem(self):
        e = self.data_get('item_selection')
        if e:
            entry = e[1]
            try:
                self.data_set('item_monitor', entry)
            except ValueError:
                # in this case a non-existing item is selected
                self.data_set('item_monitor')

    def browse_fsitem(self):
        entry = filedialog.askopenfilename(parent=self.dialog)
        if entry:
            self.data_set('item_monitor', entry)

    def add_fsitem(self):
        item = self.data_get('item_monitor')
        if item and item not in self._watch:
            self._watch.append(item)
            self._updateform()

    def del_fsitem(self):
        e = self.data_get('item_monitor')
        if e:
            idx = e[0]
            del self._watch[idx]
            self._updateform()


# end.
