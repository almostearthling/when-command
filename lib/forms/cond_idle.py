# idle session condition form

import tkinter as tk
import ttkbootstrap as ttk

from ..i18n.strings import *
from .ui import *

from .cond import form_Condition
from ..items.cond_idle import IdleCondition


DEFAULT_INTERVAL_TIME = 5
DEFAULT_INTERVAL_UNIT = UI_TIME_MINUTES


# specialized subform
class form_IdleCondition(form_Condition):

    def __init__(self, tasks_available, item=None):
        if item:
            assert isinstance(item, IdleCondition)
        else:
            item = IdleCondition()
        super().__init__(UI_TITLE_IDLECOND, tasks_available, item)

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # parameters section
        l_intervalTime = ttk.Label(area, text=UI_FORM_IDLEDURATION)
        e_intervalTime = ttk.Entry(area)
        cb_timeUnit = ttk.Combobox(
            area,
            values=[UI_TIME_SECONDS, UI_TIME_MINUTES, UI_TIME_HOURS],
            state="readonly",
        )
        pad = ttk.Frame(area)

        # arrange top items in the grid
        l_intervalTime.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_intervalTime.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        cb_timeUnit.grid(row=0, column=2, sticky=tk.E, padx=PAD, pady=PAD)
        pad.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW)

        # expand appropriate sections
        area.columnconfigure(1, weight=1)
        area.rowconfigure(1, weight=1)

        # bind data to widgets
        self.data_bind("idle_time", e_intervalTime, TYPE_INT, lambda x: x > 0)
        self.data_bind("time_unit", cb_timeUnit, TYPE_STRING)

        # add captions of data to be checked
        self.add_check_caption("idle_time", UI_FORM_IDLEDURATION)

        # propagate widgets that need to be accessed
        # NOTE: no data to propagate

        # update the form
        self._updateform()

    def _updateform(self):
        try:
            if self._item:
                if (
                    self._item.idle_seconds is not None
                    and self._item.idle_seconds % 3600 == 0
                ):
                    intv = int(self._item.idle_seconds / 3600)
                    intvu = UI_TIME_HOURS
                elif (
                    self._item.idle_seconds is not None
                    and self._item.idle_seconds % 60 == 0
                ):
                    intv = int(self._item.idle_seconds / 60)
                    intvu = UI_TIME_MINUTES
                else:
                    intv = self._item.idle_seconds
                    intvu = UI_TIME_SECONDS
                self.data_set("idle_time", intv)
                self.data_set("time_unit", intvu)
            else:
                self.data_set("idle_time", DEFAULT_INTERVAL_TIME)
                self.data_set("time_unit", DEFAULT_INTERVAL_UNIT)
        # the real check will be performed when the user presses `OK`
        except ValueError:
            pass
        return super()._updateform()

    def _updatedata(self):
        super()._updatedata()
        intv = self.data_get("idle_time")
        intvu = self.data_get("time_unit")
        if intv is not None:
            if intvu == UI_TIME_HOURS:
                self._item.idle_seconds = intv * 3600
            elif intvu == UI_TIME_MINUTES:
                self._item.idle_seconds = intv * 60
            else:
                self._item.idle_seconds = intv


# end.
