# event condition form

import tkinter as tk
import ttkbootstrap as ttk

from ..i18n.strings import *
from .ui import *

from .cond import form_Condition
from ..items.cond_event import EventCondition


# specialized subform
class form_EventCondition(form_Condition):

    def __init__(self, tasks_available, item=None):
        if item:
            assert isinstance(item, EventCondition)
        else:
            item = EventCondition()
        super().__init__(UI_TITLE_EVENTCOND, tasks_available, item)
        assert isinstance(self._item, EventCondition)

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # widgets section
        l_noParams = ttk.Label(area, text=UI_CAPTION_NOSPECIFICPARAMS)

        # arrange items in the grid
        l_noParams.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        # update the form
        self._updateform()


# end.
