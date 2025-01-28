# DBus condition form (unsupported)
# this form is here only for completeness and **must never** be displayed

import tkinter as tk
import ttkbootstrap as ttk

import pygments.lexers
from chlorophyll import CodeView

from ..i18n.strings import *
from .ui import *

from ..utility import get_editor_theme

from .cond import form_Condition
from ..items.cond_dbus import DBusCondition


_DBUS_BUS_VALUES = [':session', ':system']


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

        # DBus context section
        l_dbusBus = ttk.Label(area, text=UI_FORM_DBUS_BUS_SC)
        cb_dbusBus = ttk.Combobox(area, values=_DBUS_BUS_VALUES, width=15, state='readonly')
        l_dbusService = ttk.Label(area, text=UI_FORM_DBUS_SERVICE_SC)
        e_dbusService = ttk.Entry(area)
        l_dbusObjectPath = ttk.Label(area, text=UI_FORM_DBUS_OBJPATH_SC)
        e_dbusObjectPath = ttk.Entry(area)
        l_dbusInterface = ttk.Label(area, text=UI_FORM_DBUS_INTERFACE_SC)
        e_dbusInterface = ttk.Entry(area)

        sep1 = ttk.Separator(area)

        # extra delay section
        area_commonparams = ttk.Frame(area)
        l_checkAfter = ttk.Label(area_commonparams, text=UI_FORM_EXTRADELAY_SC)
        e_checkAfter = ttk.Entry(area_commonparams)
        l_checkAfterSeconds = ttk.Label(area_commonparams, text=UI_TIME_SECONDS)
        ck_ignorePersistentSuccess = ttk.Checkbutton(area_commonparams, text=UI_FORM_IGNOREPERSISTSUCCESS)

        # arrange items in frame
        l_checkAfter.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_checkAfter.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        l_checkAfterSeconds.grid(row=0, column=2, sticky=tk.W, padx=PAD, pady=PAD)
        ck_ignorePersistentSuccess.grid(row=2, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        area_commonparams.columnconfigure(1, weight=1)

        sep2 = ttk.Separator(area)

        # DBus method call section
        l_dbusMethod = ttk.Label(area, text=UI_FORM_DBUS_METHOD_SC)
        e_dbusMethod = ttk.Entry(area)
        l_dbusParamsCall = ttk.Label(area, text=UI_FORM_DBUS_PARAMS_CALL_SC)
        cv_dbusParamsCall = CodeView(area, pygments.lexers.JsonLexer, font='TkFixedFont', height=2, color_scheme=get_editor_theme())
        
        sep3 = ttk.Separator(area)

        l_dbusParamsCheck = ttk.Label(area, text=UI_FORM_DBUS_PARAMS_CHECK_SC)
        cv_dbusParamsCheck = CodeView(area, pygments.lexers.JsonLexer, font='TkFixedFont', height=2, color_scheme=get_editor_theme())
        ck_dbusCheckAll = ttk.Checkbutton(area, text=UI_FORM_MATCHALLRESULTS)

        # arrange items in the grid
        l_dbusBus.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cb_dbusBus.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        l_dbusService.grid(row=0, column=2, sticky=tk.W, padx=PAD, pady=PAD)
        e_dbusService.grid(row=0, column=3, sticky=tk.EW, padx=PAD, pady=PAD)
        l_dbusObjectPath.grid(row=1, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_dbusObjectPath.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=PAD, pady=PAD)
        l_dbusInterface.grid(row=2, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_dbusInterface.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=PAD, pady=PAD)

        sep1.grid(row=10, column=0, sticky=tk.EW, columnspan=4, pady=PAD)
        area_commonparams.grid(row=11, column=0, sticky=tk.NSEW, columnspan=4)

        sep2.grid(row=20, column=0, columnspan=4, sticky=tk.EW, pady=PAD)
        l_dbusMethod.grid(row=21, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_dbusMethod.grid(row=21, column=1, sticky=tk.EW, columnspan=3, padx=PAD, pady=PAD)
        l_dbusParamsCall.grid(row=22, column=0, sticky=tk.W, columnspan=4, padx=PAD, pady=PAD)
        cv_dbusParamsCall.grid(row=23, column=0, sticky=tk.NSEW, columnspan=4, padx=PAD, pady=PAD)

        sep3.grid(row=30, column=0, columnspan=4, sticky=tk.EW, pady=PAD)
        l_dbusParamsCheck.grid(row=31, column=0, sticky=tk.W, columnspan=4, padx=PAD, pady=PAD)
        cv_dbusParamsCheck.grid(row=32, column=0, sticky=tk.NSEW, columnspan=4, padx=PAD, pady=PAD)
        ck_dbusCheckAll.grid(row=33, column=0, sticky=tk.W, columnspan=4, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.rowconfigure(23, weight=1)
        area.rowconfigure(32, weight=1)
        area.columnconfigure(3, weight=1)

        # bind data to widgets
        self.data_bind('bus', cb_dbusBus, TYPE_STRING)
        self.data_bind('service', e_dbusService, TYPE_STRING)
        self.data_bind('object_path', e_dbusObjectPath, TYPE_STRING)
        self.data_bind('interface', e_dbusInterface, TYPE_STRING)
        self.data_bind('method', e_dbusMethod, TYPE_STRING)
        self.data_bind('parameter_call', cv_dbusParamsCall, TYPE_STRING)
        self.data_bind('parameter_check', cv_dbusParamsCheck, TYPE_STRING)
        self.data_bind('parameter_check_all', ck_dbusCheckAll)
        self.data_bind('check_after', e_checkAfter, TYPE_INT, lambda x: x >= 0)
        self.data_bind('ignore_persistent_success', ck_ignorePersistentSuccess)

        # propagate widgets that need to be accessed
        # NOTE: no data to propagate

        # update the form
        self._updateform()


    def _updateform(self):
        self.data_set('bus', self._item.bus)
        self.data_set('service', self._item.service)
        self.data_set('object_path', self._item.object_path)
        self.data_set('interface', self._item.interface)
        self.data_set('method', self._item.method)
        self.data_set('parameter_call', self._item.parameter_call or None)
        self.data_set('parameter_check', self._item.parameter_check or None)
        self.data_set('parameter_check_all', self._item.parameter_check_all or False)
        self.data_set('check_after', self._item.check_after or 0)
        self.data_set('ignore_persistent_success', self._item.recur_after_failed_check or False)
        return super()._updateform()
    
    def _updatedata(self):
        self._item.bus = self.data_get('bus')
        self._item.service = self.data_get('service')
        self._item.object_path = self.data_get('object_path')
        self._item.interface = self.data_get('interface')
        self._item.method = self.data_get('method')
        self._item.parameter_call = self.data_get('parameter_call') or None
        self._item.parameter_check = self.data_get('parameter_check') or None
        self._item.parameter_check_all = self.data_get('parameter_check_all') or False
        self._item.check_after = self.data_get('check_after') or None
        self._item.recur_after_failed_check = self.data_get('ignore_persistent_success') or None
        return super()._updatedata()


# end.
