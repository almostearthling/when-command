# event condition form

from ..i18n.strings import *

import tkinter as tk
import ttkbootstrap as ttk

from .ui import *

from ..forms.cond import form_Condition
from ..items.cond_event import EventCondition


# specialized subform
class form_EventCondition(form_Condition):
    
    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, EventCondition))
        else:
            item = EventCondition()
        super().__init__(UI_TITLE_EVENTCOND, tasks_available, item)

        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        l_noParams = ttk.Label(area, text=UI_CAPTION_NOSPECIFICPARAMS)
        l_noParams.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        self._updateform()


# end.
