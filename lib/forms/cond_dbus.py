# DBus condition form (unsupported)
# this form is here only for completeness and **must never** be displayed

import tkinter as tk
import ttkbootstrap as ttk

from ..i18n.strings import *
from .ui import *

from .cond import form_Condition
from ..items.cond_dbus import DBusCondition


# specialized subform
class form_DBusCondition(form_Condition):

    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, DBusCondition))
        else:
            item = DBusCondition()
        super().__init__(UI_TITLE_DBUSCOND, tasks_available, item)

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # widgets section
        l_unsupported = ttk.Label(area, text=UI_CAPTION_NOTSUPPORTED)

        # arrange items in the grid
        l_unsupported.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        # update the form
        self._updateform()


# end.
