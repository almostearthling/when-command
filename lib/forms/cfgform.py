# main
# the application main form

import os

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from ..i18n.strings import *
from ..icons import APP_ICON32 as APP_ICON
from ..icons import TASK_ICON20x20 as TASK_ICON
from ..icons import CONDITION_ICON20x20 as COND_ICON
from ..icons import EVENT_ICON20x20 as EVENT_ICON
from ..icons import UNKNOWN_ICON20x20 as UNKNOWN_ICON
from .ui import *

from ..repocfg import AppConfig
from ..utility import get_configfile, get_ui_image
from ..items.item import ALL_AVAILABLE_ITEMS_D

from ..configurator.reader import read_whenever_config
from ..configurator.writer import write_whenever_config
from ..configurator.defaults import *

from .newitem import form_NewItem


# configuration box class
class form_Config(ApplicationForm):

    def __init__(self, root=None, main=False):
        
        # the root window: if not set this runs as the main app
        # and is aware that no scheduler is under control of this
        # application
        self._root = root

        # the main tree view has an increased row size
        style = ttk.Style()
        style.configure('Items.Treeview', rowheight=30)

        size = AppConfig.get('SIZE_MAIN_FORM')
        if self._root:
            bbox = (BBOX_NEW, BBOX_EDIT, BBOX_DELETE, BBOX_RELOAD, BBOX_SEPARATOR, BBOX_SAVE, BBOX_CLOSE)
        else:
            bbox = (BBOX_NEW, BBOX_EDIT, BBOX_DELETE, BBOX_SEPARATOR, BBOX_SAVE, BBOX_CLOSE)
        super().__init__(UI_APP, size, None, bbox, main)

        # list box icons
        self._icon_task = get_ui_image(TASK_ICON)
        self._icon_condition = get_ui_image(COND_ICON)
        self._icon_event = get_ui_image(EVENT_ICON)
        self._icon_unknown = get_ui_image(UNKNOWN_ICON)

        # form data
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

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(self.contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # configuration file section
        l_cfgFile = ttk.Label(area, text=CONFIGFORM_LBL_FILELOCATION_SC)
        e_cfgFile = ttk.Entry(area, state=['disabled'])
        # sep1 = ttk.Separator(area)

        # global flags and parameters
        l_tickSeconds = ttk.Label(area, text=CONFIGFORM_LBL_TICKDURATION_SC)
        e_tickSeconds = ttk.Entry(area, width=5)
        ck_randChecks = ttk.Checkbutton(area, text=CONFIGFORM_LBL_RANDOMCHECKS)
        fill1 = ttk.Frame(area)
        sep2 = ttk.Separator(area)

        # item list box
        l_items = ttk.Label(area, text=CONFIGFORM_LBL_ITEMS_SC)
        # build a scrolled frame for the treeview
        sftv_items = ttk.Frame(area)
        tv_items = ttk.Treeview(
            sftv_items,
            columns=('name', 'type', 'signature'),
            displaycolumns=('name', 'type'),
            show='tree headings',
            style='Items.Treeview',
            height=5,
        )
        tv_items.column('#0', anchor=tk.CENTER, width=40, stretch=tk.NO)
        tv_items.heading('#0', anchor=tk.CENTER, text="")
        tv_items.heading('name', anchor=tk.W, text=CONFIGFORM_LHD_NAME)
        tv_items.heading('type', anchor=tk.W, text=CONFIGFORM_LHD_TYPE)
        sb_items = ttk.Scrollbar(sftv_items, orient=tk.VERTICAL, command=tv_items.yview)
        tv_items.configure(yscrollcommand=sb_items.set)
        tv_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_items.pack(side=tk.RIGHT, fill=tk.Y)

        # arrange items in the grid
        l_cfgFile.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.W)
        e_cfgFile.grid(row=0, column=1, columnspan=4, sticky=tk.EW, padx=PAD, pady=PAD)
        # sep1.grid(row=1, column=0, columnspan=4, pady=PAD, sticky=tk.EW)
        l_tickSeconds.grid(row=10, column=0, padx=PAD, pady=PAD)
        e_tickSeconds.grid(row=10, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        ck_randChecks.grid(row=10, column=3, sticky=tk.W, padx=PAD, pady=PAD)
        fill1.grid(row=10, column=2, sticky=tk.NSEW)
        sep2.grid(row=11, column=0, columnspan=4, pady=PAD, sticky=tk.EW)
        l_items.grid(row=20, column=0, columnspan=4, sticky=tk.W, padx=PAD, pady=PAD)
        sftv_items.grid(row=21, column=0, columnspan=4, sticky=tk.NSEW, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.rowconfigure(index=21, weight=1)
        area.columnconfigure(2, weight=1)

        # bind data to widgets
        self.data_bind('config_file', e_cfgFile, TYPE_STRING)
        self.data_bind('scheduler_tick_seconds', e_tickSeconds, TYPE_INT, lambda x: x is None or x > 0)
        self.data_bind('randomize_checks_within_ticks', ck_randChecks)
        self.data_bind('item_selection', tv_items)

        # bind double click in list to item editor
        tv_items.bind('<Double-Button-1>', lambda _: self.edit())

        # bind changes to global params so that the _changed flag becomes true
        ck_randChecks.configure(command=self._set_changed)

        # propagate widgets that need to be accessed
        self._tv_items = tv_items

        # load the configuration file and update the form
        config_file = get_configfile()
        self.data_set('config_file', config_file)
        self._load_config(config_file)
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
        # set the changed flag when tick seconds have changed: this is not
        # necessary for the check box based parameter, because the flag is
        # updated every time it gets clicked
        tick_secs = self.data_get('scheduler_tick_seconds', DEFAULT_SCHEDULER_TICK_SECONDS)
        if tick_secs != self._globals['scheduler_tick_seconds']:
            self._globals['scheduler_tick_seconds'] = tick_secs
            self._changed = True
        self._globals['randomize_checks_within_ticks'] = self.data_get('randomize_checks_within_ticks', DEFAULT_RANDOMIZE_CHECKS_WITHIN_TICKS)

    # update the form fields according to the associated actual data
    def _updateform(self):
        self._tv_items.delete(*self._tv_items.get_children())
        for entry in self._itemlistentries:
            t = entry[2].split(":", 1)[0]
            if t == "task":
                icon = self._icon_task
            elif t == "cond":
                icon = self._icon_condition
            elif t == "event":
                icon = self._icon_event
            # the following actually never happens
            else:
                icon = self._icon_unknown
            self._tv_items.insert("", iid="%s-%s" % (entry[0], entry[2]), image=icon, values=entry, index=tk.END)
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
        # do the same stuff as self._updatedata, without updating globals
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


    # to be called when one of the global parameters has been changed
    def _set_changed(self, changed=True):
        self._changed = changed


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
        self._updatedata()
        fn = self.data_get('config_file')
        if fn and self._changed:
            if os.path.exists(fn):
                if messagebox.askyesno(UI_POPUP_T_CONFIRM, UI_POPUP_OVERWRITEFILE_Q):
                    self._save_config(fn)
                    self._changed = False
            else:
                self._save_config(fn)
                self._changed = False

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

        # in the end, update the form on changes
        if self._changed:
            self._updatedata()
            self._updateform()

    # create a new item: open the item type selection dialog and, if an
    # item type is chosen, open the appropriate form with default values
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
                    else:
                        new_item = None
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

        # in the end, update the form on changes
        if self._changed:
            self._updatedata()
            self._updateform()

    # reload the configuration by sending the appropriate message to the
    # main (hidden) application form
    def reload(self):
        if messagebox.askyesno(UI_POPUP_T_CONFIRM, UI_POPUP_RELOADCONFIG_Q):
            if self._root:
                self._root.send_event('<<SchedReloadConfig>>')
        return super().reload()

    # modify the reaction to the quit button so that if the configuration
    # has changed the user is asked whether or not he wants to discard it
    def exit_close(self):
        if self._changed:
            if messagebox.askokcancel(UI_POPUP_T_CONFIRM, UI_POPUP_DISCARDCONFIG_Q):
                return super().exit_close()
        else:
            return super().exit_close()


# end.
