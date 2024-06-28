# form to select what type of new item should be created

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from ..i18n.strings import *
from .ui import *

from ..repocfg import AppConfig
from ..items.item import ALL_AVAILABLE_ITEMS, ALL_AVAILABLE_ITEMS_D


# form class: this form is fixed and will not be derived
class form_NewItem(ApplicationForm):

    def __init__(self):
        size = AppConfig.get('SIZE_NEWITEM_FORM')
        bbox = (BBOX_OK, BBOX_CANCEL)
        super().__init__(UI_TITLE_NEWITEM, size, None, bbox)

        # form data
        self._subtypes_display = []
        self._type = 'task'
        self._ret = None

        subtypes = list(x for x in ALL_AVAILABLE_ITEMS
                        if x[0].startswith('%s:' % self._type)
                        and x[3].available)
        self._subtypes_display = list([x[1], x[0]] for x in subtypes)
        self._subtypes_display.sort(key=lambda x: x[0])

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(self.contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # type section
        l_itemType = ttk.Label(area, text=UI_FORM_ITEMTYPE)
        rb_itemTask = ttk.Radiobutton(area, text=ITEM_TASK, value='task', command=lambda : self.set_itemtype())
        rb_itemCond = ttk.Radiobutton(area, text=ITEM_COND, value='cond', command=lambda : self.set_itemtype())
        rb_itemEvent = ttk.Radiobutton(area, text=ITEM_EVENT, value='event', command=lambda : self.set_itemtype())

        # subtype section
        l_itemSubTypes = ttk.Label(area, text=UI_FORM_ITEMSUBTYPES)
        # build a scrolled frame for the treeview
        sftv_itemSubTypes = ttk.Frame(area)
        tv_itemSubTypes = ttk.Treeview(sftv_itemSubTypes, columns=('type', 'code'), displaycolumns=('type',), show='', height=5)
        tv_itemSubTypes.heading('type', anchor=tk.W, text=UI_FORM_ITEM)
        sb_itemSubTypes = ttk.Scrollbar(sftv_itemSubTypes, orient=tk.VERTICAL, command=tv_itemSubTypes.yview)
        tv_itemSubTypes.configure(yscrollcommand=sb_itemSubTypes.set)
        tv_itemSubTypes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_itemSubTypes.pack(side=tk.RIGHT, fill=tk.Y)

        # arrange items in the grid
        l_itemType.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        rb_itemTask.grid(row=1, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        rb_itemCond.grid(row=2, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        rb_itemEvent.grid(row=3, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        l_itemSubTypes.grid(row=10, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        sftv_itemSubTypes.grid(row=11, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        # bind double click to variable recall
        tv_itemSubTypes.bind('<Double-Button-1>', lambda _: self.exit_ok())

        # expand appropriate sections
        area.columnconfigure(0, weight=1)
        area.rowconfigure(11, weight=1)

        # bind data to widgets
        self.data_bind('item_type', (rb_itemTask, rb_itemCond, rb_itemEvent), TYPE_STRING)
        self.data_bind('item_selection', tv_itemSubTypes)

        # propagate widgets that need to be accessed
        self._tv_itemtypes = tv_itemSubTypes

        # update the form
        self._updateform()


    def set_itemtype(self):
        self._type = self.data_get('item_type')
        subtypes = list(x for x in ALL_AVAILABLE_ITEMS
                        if x[0].startswith('%s:' % self._type)
                        and x[3].available)
        self._subtypes_display = list([x[1], x[0]] for x in subtypes)
        self._subtypes_display.sort(key=lambda x: x[0])
        self._updateform()

    def _updateform(self):
        self.data_set('item_type', self._type)
        self._tv_itemtypes.delete(*self._tv_itemtypes.get_children())
        for entry in self._subtypes_display:
            self._tv_itemtypes.insert('', iid=entry[1], values=entry, index=ttk.END)

    def exit_ok(self):
        choice = self.data_get('item_selection')
        if choice:
            self._ret = self._type, ALL_AVAILABLE_ITEMS_D[choice[1]][1]
        return super().exit_ok()

    def run(self):
        super().run()
        return self._ret


# end.
