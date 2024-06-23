# DBus event form 
# this form is here only for completeness and **must never** be displayed

from ..i18n.strings import *

import tkinter as tk
import ttkbootstrap as ttk

from .ui import *

from .event import form_Event
from ..items.event_dbus import DBusEvent


# specialized subform
class form_DBusEvent(form_Event):

    def __init__(self, conditions_available, item=None):
        if item:
            assert(isinstance(item, DBusEvent))
        else:
            item = DBusEvent()
        super().__init__(UI_TITLE_DBUSEVENT, conditions_available, item)

        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        l_unsupported = ttk.Label(area, text=UI_CAPTION_NOTSUPPORTED)
        l_unsupported.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        self._updateform()


# end.
