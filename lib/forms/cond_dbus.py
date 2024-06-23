# DBus condition form (unsupported)
# this form is here only for completeness and **must never** be displayed

from ..i18n.strings import *

import tkinter as tk
import ttkbootstrap as ttk

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

        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        l_unsupported = ttk.Label(area, text=UI_CAPTION_NOTSUPPORTED)
        l_unsupported.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        self._updateform()


# end.
