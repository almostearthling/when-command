# history box

from ..i18n.strings import *
from ..repocfg import AppConfig

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from ..utility import get_UI_theme

from .ui import *

from ..icons import APP_ICON32 as APP_ICON


# form class: this form is fixed and will not be derived
class form_History(ApplicationForm):

    def __init__(self, history=None, main=False):
        size = AppConfig.get('SIZE_HISTORY_FORM')
        bbox = (BBOX_CLOSE,)
        super().__init__(UI_APP, size, APP_ICON, bbox, main)

        # form data
        self._history = []
        if history:
            self.set_history(history)

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(self.contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # history list section
        l_history = ttk.Label(area, text=UI_FORM_HISTORYITEMS_SC)
        # build a scrolled frame for the treeview
        sftv_history = ttk.Frame(area)
        tv_history = ttk.Treeview(
            sftv_history,
            columns=('time', 'task', 'trigger', 'duration', 'success', 'message'),
            show='headings',
            height=5,
        )
        sb_history = ttk.Scrollbar(sftv_history, orient=tk.VERTICAL, command=tv_history.yview)
        tv_history.configure(yscrollcommand=sb_history.set)
        tv_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_history.pack(side=tk.RIGHT, fill=tk.Y)

        # NOTE: widths are empirically determined, should be tested on
        # other platform to verify that they are suitable anyway
        tv_history.column(0, anchor=tk.CENTER, width=15)
        tv_history.column(1, anchor=tk.W, width=16)
        tv_history.column(2, anchor=tk.W, width=16)
        tv_history.column(3, anchor=tk.W, width=7)
        tv_history.column(4, anchor=tk.CENTER, width=4)
        tv_history.column(5, anchor=tk.W, width=38)

        tv_history.heading(0, anchor=tk.CENTER, text=UI_FORM_HS_TIME)
        tv_history.heading(1, anchor=tk.W, text=UI_FORM_HS_TASK)
        tv_history.heading(2, anchor=tk.W, text=UI_FORM_HS_TRIGGER)
        tv_history.heading(3, anchor=tk.W, text=UI_FORM_HS_DURATION)
        tv_history.heading(4, anchor=tk.CENTER, text=UI_FORM_HS_SUCCESS)
        tv_history.heading(5, anchor=tk.W, text=UI_FORM_HS_MESSAGE)

        # arrange items in the grid
        l_history.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        # tv_history.grid(row=1, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        sftv_history.grid(row=1, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.rowconfigure(1, weight=1)
        area.columnconfigure(0, weight=1)

        # bind data to widgets
        # NOTE: no data to bind

        # propagate widgets that need to be accessed
        self._tv_history = tv_history

        self._updateform()


    def set_history(self, history):
        h = list(
            [
                x['time'][:-7].replace("T", " "),
                x['task'],
                x['trigger'],
                ("%.2fs" % x['duration'].total_seconds()).ljust(7),
                SYM_OK if x['success'] == 'OK' else SYM_UNKNOWN if x['success'] == 'IND' else SYM_FAIL,
                x['message'],
            ]
            for x in history
        )
        h.reverse()
        self._history = h

    def _updateform(self):
        self._tv_history.delete(*self._tv_history.get_children())
        for entry in self._history:
            self._tv_history.insert('', values=entry, index=ttk.END)


# end.
