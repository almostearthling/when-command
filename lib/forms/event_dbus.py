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
from ..items.event_dbus import DBusEvent


_DBUS_BUS_VALUES = [':session', ':system']


# specialized subform
class form_DBusEvent(form_Event):

    def __init__(self, conditions_available, item=None):
        if item:
            assert(isinstance(item, DBusEvent))
        else:
            item = DBusEvent()
        super().__init__(UI_TITLE_DBUSEVENT, conditions_available, item)

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # widgets section
        l_dbusBus = ttk.Label(area, text=UI_FORM_DBUS_BUS_SC)
        cb_dbusBus = ttk.Combobox(area, values=_DBUS_BUS_VALUES, state='readonly')

        # TODO: choose an appropriate lexer (although `bash` seems to be OK)
        sep1 = ttk.Separator(area)
        l_dbusRule = ttk.Label(area, text=UI_FORM_DBUS_RULE_SC)
        cv_dbusRule = CodeView(area, pygments.lexers.BashLexer, font='TkFixedFont', height=2, color_scheme=get_editor_theme())

        sep2 = ttk.Separator(area)
        l_dbusParamsCheck = ttk.Label(area, text=UI_FORM_DBUS_PARAMS_CHECK_SC)
        cv_dbusParamsCheck = CodeView(area, pygments.lexers.JsonLexer, font='TkFixedFont', height=2, color_scheme=get_editor_theme())
        ck_dbusCheckAll = ttk.Checkbutton(area, text=UI_FORM_MATCHALLRESULTS)

        # arrange items in the grid
        l_dbusBus.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cb_dbusBus.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        
        sep1.grid(row=20, column=0, columnspan=4, sticky=tk.EW, pady=PAD)
        l_dbusRule.grid(row=21, column=0, sticky=tk.W, columnspan=2, padx=PAD, pady=PAD)
        cv_dbusRule.grid(row=22, column=0, sticky=tk.NSEW, columnspan=2, padx=PAD, pady=PAD)

        sep2.grid(row=30, column=0, columnspan=4, sticky=tk.EW, pady=PAD)
        l_dbusParamsCheck.grid(row=31, column=0, sticky=tk.W, columnspan=2, padx=PAD, pady=PAD)
        cv_dbusParamsCheck.grid(row=32, column=0, sticky=tk.NSEW, columnspan=2, padx=PAD, pady=PAD)
        ck_dbusCheckAll.grid(row=33, column=0, sticky=tk.W, columnspan=4, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.rowconfigure(22, weight=1)
        area.rowconfigure(32, weight=1)
        area.columnconfigure(1, weight=1)

        # bind data to widgets
        self.data_bind('bus', cb_dbusBus, TYPE_STRING)
        self.data_bind('rule', cv_dbusRule, TYPE_STRING)
        self.data_bind('parameter_check', cv_dbusParamsCheck, TYPE_STRING)
        self.data_bind('parameter_check_all', ck_dbusCheckAll)

        # propagate widgets that need to be accessed
        # NOTE: no data to propagate

        # update the form
        self._updateform()


    def _updateform(self):
        self.data_set('bus', self._item.bus)
        self.data_set('rule', self._item.rule)
        self.data_set('parameter_check', self._item.parameter_check or None)
        self.data_set('parameter_check_all', self._item.parameter_check_all or False)
        return super()._updateform()
    
    def _updatedata(self):
        self._item.bus = self.data_get('bus')
        self._item.rule = self.data_get('rule')
        self._item.parameter_check = self.data_get('parameter_check') or ''
        self._item.parameter_check_all = self.data_get('parameter_check_all') or False
        return super()._updatedata()


# end.
