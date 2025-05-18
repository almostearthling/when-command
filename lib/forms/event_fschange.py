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
            assert isinstance(item, FilesystemChangeEvent)
        else:
            item = FilesystemChangeEvent()
        super().__init__(UI_TITLE_FSCHANGEEVENT, conditions_available, item)

        # form data
        self._watch = self._item.watch.copy() if self._item.watch else []

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # parameters section
        ck_recursive = ttk.Checkbutton(area, text=UI_FORM_RECURSIVE_DIRSCAN)
        l_monitored = ttk.Label(area, text=UI_FORM_MONITOREDFSITEMS_SC)
        # build a scrolled frame for the treeview
        sftv_monitored = ttk.Frame(area)
        tv_monitored = ttk.Treeview(
            sftv_monitored,
            columns=("seq", "items"),
            show="",
            displaycolumns=(1,),
            height=5,
        )
        sb_monitored = ttk.Scrollbar(
            sftv_monitored, orient=tk.VERTICAL, command=tv_monitored.yview
        )
        tv_monitored.configure(yscrollcommand=sb_monitored.set)
        tv_monitored.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_monitored.pack(side=tk.RIGHT, fill=tk.Y)
        # the add-entry section
        l_monEntry = ttk.Label(area, text=UI_FORM_ITEM_SC)
        e_monEntry = ttk.Entry(area)
        b_browse = ttk.Button(area, text=UI_BROWSE, command=self.browse_fsitem)
        b_addEntry = ttk.Button(
            area, text=UI_ADD, width=BUTTON_STANDARD_WIDTH, command=self.add_fsitem
        )
        b_delEntry = ttk.Button(
            area, text=UI_DEL, width=BUTTON_STANDARD_WIDTH, command=self.del_fsitem
        )
        ck_selectDir = ttk.Checkbutton(area, text=UI_FORM_SELECT_DIRECTORY)

        # arrange top items in the grid
        ck_recursive.grid(
            row=0, column=0, columnspan=5, sticky=tk.W, padx=PAD, pady=PAD
        )
        l_monitored.grid(row=1, column=0, columnspan=5, sticky=tk.W, padx=PAD, pady=PAD)
        sftv_monitored.grid(
            row=2, column=0, columnspan=5, sticky=tk.NSEW, padx=PAD, pady=PAD
        )
        l_monEntry.grid(row=3, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_monEntry.grid(row=3, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_browse.grid(row=3, column=2, sticky=tk.EW, padx=PAD, pady=PAD)
        b_addEntry.grid(row=3, column=3, sticky=tk.EW, padx=PAD, pady=PAD)
        b_delEntry.grid(row=3, column=4, sticky=tk.EW, padx=PAD, pady=PAD)
        ck_selectDir.grid(
            row=4, column=2, columnspan=3, sticky=tk.W, padx=PAD, pady=PAD
        )

        tv_monitored.bind("<ButtonRelease-1>", lambda _: self.recall_fsitem())

        # expand appropriate sections
        area.columnconfigure(1, weight=1)
        area.rowconfigure(2, weight=1)

        # bind data to widgets
        # the following might be actually too strict
        # self.data_bind('item_monitor', e_monEntry, TYPE_STRING, exists)
        self.data_bind("recursive", ck_recursive)
        self.data_bind("item_monitor", e_monEntry, TYPE_STRING)
        self.data_bind("item_selection", tv_monitored)
        self.data_bind("select_dir", ck_selectDir)

        # propagate widgets that need to be accessed
        self._tv_monitored = tv_monitored

        # update the form
        self._updateform()

    def _updateform(self):
        self.data_set("recursive", self._item.recursive or False)
        self._tv_monitored.delete(*self._tv_monitored.get_children())
        idx = 0
        for entry in self._watch:
            self._tv_monitored.insert("", iid=idx, values=(idx, entry), index=tk.END)
            idx += 1
        return super()._updateform()

    def _updatedata(self):
        self._item.recursive = self.data_get("recursive") or None
        e = []
        for entry in self._watch:
            e.append(entry)
        self._item.watch = e or None
        return super()._updatedata()

    def recall_fsitem(self):
        e = self.data_get("item_selection")
        if e:
            entry = e[1]
            try:
                self.data_set("item_monitor", entry)
            except ValueError:
                # in this case a non-existing item is selected
                self.data_set("item_monitor")

    def browse_fsitem(self):
        if self.data_get("select_dir"):
            entry = filedialog.askdirectory(parent=self.dialog)
        else:
            entry = filedialog.askopenfilename(parent=self.dialog)
        if entry:
            self.data_set("item_monitor", entry)

    def add_fsitem(self):
        item = normpath(self.data_get("item_monitor"))
        if item and item not in self._watch:
            self._watch.append(item)
            self._updateform()

    def del_fsitem(self):
        e = self.data_get("item_monitor")
        if e:
            idx = self._watch.index(e)
            del self._watch[idx]
            self._updateform()


# end.
