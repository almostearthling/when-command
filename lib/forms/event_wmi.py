# DBus event form
# this form is here only for completeness and **must never** be displayed

import tkinter as tk
import ttkbootstrap as ttk

import pygments.lexers
from chlorophyll import CodeView

from ..i18n.strings import *
from .ui import *

from ..utility import get_editor_theme

from .event import form_Event
from ..items.event_wmi import WMIEvent


# specialized subform
class form_WMIEvent(form_Event):

    def __init__(self, conditions_available, item=None):
        if item:
            assert isinstance(item, WMIEvent)
        else:
            item = WMIEvent()
        super().__init__(UI_TITLE_WMIEVENT, conditions_available, item)
        assert isinstance(self._item, WMIEvent)

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # TODO: choose an appropriate lexer (although `bash` seems to be OK)
        l_wmiQuery = ttk.Label(area, text=UI_FORM_WMI_QUERY_SC)
        cv_wmiQuery = CodeView(
            area,
            pygments.lexers.SqlLexer,
            font="TkFixedFont",
            height=2,
            color_scheme=get_editor_theme(),
        )

        l_wmiQuery.grid(row=1, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cv_wmiQuery.grid(row=2, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.rowconfigure(2, weight=1)
        area.columnconfigure(0, weight=1)

        # bind data to widgets
        self.data_bind("query", cv_wmiQuery, TYPE_STRING, lambda x: bool(x))

        # propagate widgets that need to be accessed
        # NOTE: no data to propagate

        # update the form
        self._updateform()

    def _updateform(self):
        assert isinstance(self._item, WMIEvent)
        self.data_set("query", self._item.query)
        return super()._updateform()

    def _updatedata(self):
        assert isinstance(self._item, WMIEvent)
        self._item.query = self.data_get("query")
        return super()._updatedata()


# end.
