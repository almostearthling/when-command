# main
# the application main form

import os

from ..i18n.strings import *
from ..repocfg import AppConfig

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from .ui import *

from ..utility import get_configfile, get_UI_theme

from ..items.item import ALL_AVAILABLE_ITEMS_D

from ..icons import APP_ICON32 as APP_ICON

from .newitem import form_NewItem

from ..configurator.reader import read_whenever_config
from ..configurator.writer import write_whenever_config
from ..configurator.defaults import *


# configuration box class
class form_Config(ApplicationForm):

    def __init__(self, main=False):
        size = AppConfig.get('SIZE_MAIN_FORM')
        bbox = (BBOX_NEW, BBOX_EDIT, BBOX_DELETE, BBOX_SEPARATOR, BBOX_SAVE, BBOX_QUIT)
        super().__init__(UI_APP, size, APP_ICON, bbox, main)

        self._tasks = {}
        self._conditions = {}
        self._events = {}
        self._data = {}
        self._itemlistentries = []
        self._globals = {
            'scheduler_tick_seconds': DEFAULT_SCHEDULER_TICK_SECONDS,
            'randomize_checks_within_ticks': DEFAULT_RANDOMIZE_CHECKS_WITHIN_TICKS,
        }
        self._changed = False

        # build the UI
        area = ttk.Frame(self.contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        l_cfgFile = ttk.Label(area, text=CONFIGFORM_LBL_FILELOCATION_SC)
        e_cfgFile = ttk.Entry(area, state=['disabled'])
        l_cfgFile.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.W)
        e_cfgFile.grid(row=0, column=1, columnspan=4, sticky=tk.EW, padx=PAD, pady=PAD)
        self.data_bind('config_file', e_cfgFile, TYPE_STRING)
        # sep1 = ttk.Separator(area)
        # sep1.grid(row=1, column=0, columnspan=4, pady=PAD, sticky=tk.EW)

        l_tickSeconds = ttk.Label(area, text=CONFIGFORM_LBL_TICKDURATION_SC)
        e_tickSeconds = ttk.Entry(area, width=5)
        self.data_bind('scheduler_tick_seconds', e_tickSeconds, TYPE_INT, lambda x: x is None or x > 0)
        ck_randChecks = ttk.Checkbutton(area, text=CONFIGFORM_LBL_RANDOMCHECKS)
        self.data_bind('randomize_checks_within_ticks', ck_randChecks)
        fill1 = ttk.Frame(area)
        l_tickSeconds.grid(row=10, column=0, padx=PAD, pady=PAD)
        e_tickSeconds.grid(row=10, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        fill1.grid(row=10, column=2, sticky=tk.NSEW)
        ck_randChecks.grid(row=10, column=3, sticky=tk.W, padx=PAD, pady=PAD)
        sep2 = ttk.Separator(area)
        sep2.grid(row=11, column=0, columnspan=4, pady=PAD, sticky=tk.EW)

        l_items = ttk.Label(area, text=CONFIGFORM_LBL_ITEMS_SC)
        tv_items = ttk.Treeview(area, columns=('name', 'type', 'signature'), displaycolumns=('name', 'type'), show='headings', height=5)
        self.data_bind('item_selection', tv_items)
        tv_items.heading('name', anchor=tk.W, text=CONFIGFORM_LHD_NAME)
        tv_items.heading('type', anchor=tk.W, text=CONFIGFORM_LHD_TYPE)
        l_items.grid(row=20, column=0, columnspan=4, sticky=tk.W, padx=PAD, pady=PAD)
        tv_items.grid(row=21, column=0, columnspan=4, sticky=tk.NSEW, padx=PAD, pady=PAD)

        area.rowconfigure(index=21, weight=1)
        area.columnconfigure(2, weight=1)

        # propagate the items list so that it can be used outside from here
        self._tv_items = tv_items

        # bind double click to item editor
        self._tv_items.bind('<Double-Button-1>', lambda _: self.edit())

        # load the configuration file and update the form
        config_file = get_configfile()
        self.data_set('config_file', config_file)
        self._load_config(config_file)
        self._updatedata()
        self._updateform()


    # update the associated data according to what is in the form
    def _updatedata(self):
        self._itemlistentries = []
        # encode the invisible list field with the same signature that is used in
        # the _item_ module, so that the corresponding form and item factories can
        # be retrieved dynamically
        for key in self._tasks:
            item = self._tasks[key]
            if item.tags:
                signature = "task:%s:%s" % (item.type, item.tags.get('subtype'))
            else:
                signature = "task:%s" % item.type
            self._itemlistentries.append([item.name, item.hrtype, signature])
        for key in self._conditions:
            item = self._conditions[key]
            if item.tags:
                signature = "cond:%s:%s" % (item.type, item.tags.get('subtype'))
            else:
                signature = "cond:%s" % item.type
            self._itemlistentries.append([item.name, item.hrtype, signature])
        for key in self._events:
            item = self._events[key]
            if item.tags:
                signature = "event:%s:%s" % (item.type, item.tags.get('subtype'))
            else:
                signature = "event:%s" % item.type
            self._itemlistentries.append([item.name, item.hrtype, signature])
        self._itemlistentries.sort(key=lambda x: x[0])
        self._globals['scheduler_tick_seconds'] = self.data_get('scheduler_tick_seconds', DEFAULT_SCHEDULER_TICK_SECONDS)
        self._globals['randomize_checks_within_ticks'] = self.data_get('randomize_checks_within_ticks', DEFAULT_RANDOMIZE_CHECKS_WITHIN_TICKS)

    # update the form fields according to the associated actual data
    def _updateform(self):
        self._tv_items.delete(*self._tv_items.get_children())
        for entry in self._itemlistentries:
            self._tv_items.insert("", iid="%s-%s" % (entry[0], entry[2]), values=entry, index=tk.END)
        self.data_set('scheduler_tick_seconds', self._globals['scheduler_tick_seconds'] or DEFAULT_SCHEDULER_TICK_SECONDS)
        self.data_set('randomize_checks_within_ticks', self._globals['randomize_checks_within_ticks'])

    # reset all associated data in the form (does not update fields)
    def _resetdata(self):
        self._tasks = {}
        self._conditions = {}
        self._events = {}
        self._globals = {
            'scheduler_tick_seconds': DEFAULT_SCHEDULER_TICK_SECONDS,
            'randomize_checks_within_ticks': DEFAULT_RANDOMIZE_CHECKS_WITHIN_TICKS,
        }
        self._changed = False


    # load the configuration from a TOML file
    def _load_config(self, fn):
        self._resetdata()
        tasks, conditions, events, self._globals = read_whenever_config(fn)
        for item in tasks:
            self._tasks[item.name] = item
        for item in conditions:
            self._conditions[item.name] = item
        for item in events:
            self._events[item.name] = item
        self._changed = False

    # save the configuration to a TOML file
    def _save_config(self, fn):
        write_whenever_config(
            fn,
            [self._tasks[k] for k in self._tasks],
            [self._conditions[k] for k in self._conditions],
            [self._events[k] for k in self._events],
            self._globals,
        )


    # command button reactions
    def delete(self):
        item_name, _, item_signature = self.data_get('item_selection')
        item_type = item_signature.split(':', 1)[0]
        if messagebox.askyesno(UI_POPUP_T_CONFIRM, UI_POPUP_DELETEITEM_Q):
            if item_type == 'task':
                del self._tasks[item_name]
            elif item_type == 'cond':
                del self._conditions[item_name]
            elif item_type == 'event':
                del self._events[item_name]
            self._updatedata()
            self._updateform()
            self._changed = True

    def save(self):
        fn = self.data_get('config_file')
        if fn and self._changed:
            if os.path.exists(fn):
                if messagebox.askyesno(UI_POPUP_T_CONFIRM, UI_POPUP_OVERWRITEFILE_Q):
                    self._save_config(fn)
            else:
                self._save_config(fn)


    # edit a specific item: to be complete, this is also bound
    # to the double click event for an element of the list
    def edit(self):
        item_name, _, item_signature = self.data_get('item_selection')
        item_type = item_signature.split(':', 1)[0]

        # task items
        if item_type == 'task':
            _, fform, fitem = ALL_AVAILABLE_ITEMS_D.get(item_signature)
            if fform and fitem.available:
                e = fform(self._tasks[item_name])
                if e is not None:
                    new_item = e.run()
                    if new_item:
                        if new_item.name != item_name:
                            del self._tasks[item_name]
                        self._tasks[new_item.name] = new_item
                        self._changed = True

        # condition items
        elif item_type == 'cond':
            _, fform, fitem = ALL_AVAILABLE_ITEMS_D.get(item_signature)
            if fform and fitem.available:
                e = fform(list(self._tasks.keys()), self._conditions[item_name])
                if e is not None:
                    new_item = e.run()
                    if new_item:
                        if new_item.name != item_name:
                            del self._conditions[item_name]
                        self._conditions[new_item.name] = new_item
                        self._changed = True

        # event items
        elif item_type == 'event':
            event_conds = list(x for x in self._conditions if self._conditions[x].type == 'event')
            _, fform, fitem = ALL_AVAILABLE_ITEMS_D.get(item_signature)
            if fform and fitem.available:
                e =  fform(event_conds, self._events[item_name])
                if e is not None:
                    new_item = e.run()
                    if new_item:
                        if new_item.name != item_name:
                            del self._events[item_name]
                        self._events[new_item.name] = new_item
                        self._changed = True


    def new(self):
        e = form_NewItem()
        if e is not None:
            r = e.run()
            if r:
                t, form_class = r
                if t == 'task':
                    form = form_class()
                elif t == 'cond':
                    form = form_class(list(self._tasks.keys()))
                # note that, since providing a suitable event based
                # condition is mandatory for an event, the form will
                # refuse to create a new event
                elif t == 'event':
                    event_conds = list(x for x in self._conditions if self._conditions[x].type == 'event')
                    if event_conds:
                        form = form_class(event_conds)
                    else:
                        messagebox.showerror(UI_POPUP_T_ERR, message=UI_POPUP_NOEVENTCONDITIONS_ERR)
                        form = None
                try:
                    if form is not None:
                        new_item = form.run()
                except ValueError:
                    new_item = None
                if form is not None:
                    del form
                if new_item:
                    if t == 'task':
                        self._tasks[new_item.name] = new_item
                    elif t == 'cond':
                        self._conditions[new_item.name] = new_item
                    elif t == 'event':
                        self._events[new_item.name] = new_item
                    self._changed = True


# end.