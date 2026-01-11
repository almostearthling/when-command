# main
# the application main form

import os

import tkinter as tk
import ttkbootstrap as ttk

from ..i18n.strings import *
from ..icons import APP_ICON32 as APP_ICON
from ..icons import TASK_ICON20x20 as TASK_ICON
from ..icons import CONDITION_ICON20x20 as COND_ICON
from ..icons import EVENT_ICON20x20 as EVENT_ICON
from ..icons import UNKNOWN_ICON20x20 as UNKNOWN_ICON
from .ui import *

from ..repocfg import AppConfig
from ..utility import get_configfile, get_ui_image, is_private_item_name
from ..items.item import ALL_AVAILABLE_ITEMS_D

from ..configurator.reader import read_whenever_config
from ..configurator.writer import write_whenever_config
from ..configurator.defaults import *

from .newitem import form_NewItem


# configuration box class
class form_Config(ApplicationForm):

    def __init__(self, app=None, main=False):

        # the root window: if not set this runs as the main app
        # and is aware that no scheduler is under control of this
        # application
        self._app = app

        # the main tree view has an increased row size
        style = ttk.Style()
        style.configure("Items.Treeview", rowheight=30)

        size = AppConfig.get("SIZE_MAIN_FORM")
        assert isinstance(size, tuple)

        if self._app:
            bbox = (
                BBOX_NEW,
                BBOX_EDIT,
                BBOX_DELETE,
                BBOX_RELOAD,
                BBOX_SEPARATOR,
                BBOX_SAVE,
                BBOX_CLOSE,
            )
        else:
            bbox = (
                BBOX_NEW,
                BBOX_EDIT,
                BBOX_DELETE,
                BBOX_SEPARATOR,
                BBOX_SAVE,
                BBOX_CLOSE,
            )
        super().__init__(UI_APP, size, None, bbox, main)

        # the following buttons may change state according to current pane
        bbox_changing = [
            BBOX_NEW,
            BBOX_EDIT,
            BBOX_DELETE,
        ]

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
            "scheduler_tick_seconds": DEFAULT_SCHEDULER_TICK_SECONDS,
            "randomize_checks_within_ticks": DEFAULT_RANDOMIZE_CHECKS_WITHIN_TICKS,
            "tags": {
                "reset_conditions_on_resume": AppConfig.get("RESET_CONDS_ON_RESUME"),
                # ...
            },
        }
        self._changed = False

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(self.contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)
        PAD = WIDGET_PADDING_PIXELS

        # notebook for items pane and global configuration pane
        nb_config = ttk.Notebook(area)
        area_items = ttk.Frame(nb_config)
        area_globals = ttk.Frame(nb_config)

        nb_config.add(area_items, text=UI_FORM_ITEMS_PANE)
        nb_config.add(area_globals, text=UI_FORM_GLOBALS_PANE)
        nb_config.grid(row=0, column=0, sticky=tk.NSEW)

        # enable/disable appropriate buttons when changing tab
        def tab_change():
            if nb_config.index(nb_config.select()) == 0:
                self.enable_buttons(*bbox_changing)
            else:
                self.disable_buttons(*bbox_changing)

        nb_config.bind("<<NotebookTabChanged>>", lambda _: tab_change())

        # globals pane
        # configuration file section
        l_cfgFile = ttk.Label(area_globals, text=UI_FORM_FILELOCATION_SC)
        e_cfgFile = ttk.Entry(area_globals, state="disabled")
        # sep1 = ttk.Separator(area)

        # global flags and parameters
        l_tickSeconds = ttk.Label(area_globals, text=UI_FORM_TICKDURATION_SC)
        e_tickSeconds = ttk.Entry(area_globals, width=5)
        ck_randChecks = ttk.Checkbutton(area_globals, text=UI_FORM_RANDOMCHECKS)
        fill1 = ttk.Frame(area_globals)
        # sep2 = ttk.Separator(area_globals)
        ck_resetOnResume = ttk.Checkbutton(area_globals, text=UI_FORM_RESETONRESUME)
        sep3 = ttk.Separator(area_globals)
        fill2 = ttk.Frame(area_globals)

        # arrange items in the grid
        l_cfgFile.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.W)
        e_cfgFile.grid(row=0, column=1, columnspan=4, sticky=tk.EW, padx=PAD, pady=PAD)
        # sep1.grid(row=1, column=0, columnspan=5, pady=PAD, sticky=tk.EW)
        ck_randChecks.grid(row=10, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        l_tickSeconds.grid(row=10, column=3, padx=PAD, pady=PAD)
        e_tickSeconds.grid(row=10, column=4, sticky=tk.W, padx=PAD, pady=PAD)
        fill1.grid(row=10, column=2, sticky=tk.NSEW)
        # sep2.grid(row=11, column=0, columnspan=5, pady=PAD, sticky=tk.EW)
        ck_resetOnResume.grid(row=12, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        sep3.grid(row=13, column=0, columnspan=5, pady=PAD, sticky=tk.EW)
        fill2.grid(row=20, column=0, columnspan=5, sticky=tk.NSEW)

        # expand appropriate sections
        area_globals.rowconfigure(index=20, weight=1)
        area_globals.columnconfigure(1, weight=1)

        # items pane
        # item list box
        l_items = ttk.Label(area_items, text=UI_FORM_ITEMS_SC)
        # build a scrolled frame for the treeview
        sftv_items = ttk.Frame(area_items)
        tv_items = ttk.Treeview(
            sftv_items,
            columns=("name", "type", "signature"),
            displaycolumns=("name", "type"),
            show="tree headings",
            style="Items.Treeview",
            height=5,
        )
        tv_items.column("#0", anchor=tk.CENTER, width=40, stretch=tk.NO)
        tv_items.heading("#0", anchor=tk.CENTER, text="")
        tv_items.heading("name", anchor=tk.W, text=UI_FORM_LHD_NAME)
        tv_items.heading("type", anchor=tk.W, text=UI_FORM_LHD_TYPE)
        sb_items = ttk.Scrollbar(sftv_items, orient=tk.VERTICAL, command=tv_items.yview)
        tv_items.configure(yscrollcommand=sb_items.set)
        tv_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_items.pack(side=tk.RIGHT, fill=tk.Y)

        l_items.grid(row=20, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        sftv_items.grid(row=21, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        # expand appropriate sections
        area_items.rowconfigure(index=21, weight=1)
        area_items.columnconfigure(0, weight=1)

        # bind data to widgets
        self.data_bind("config_file", e_cfgFile, TYPE_STRING)
        self.data_bind(
            "scheduler_tick_seconds",
            e_tickSeconds,
            TYPE_INT,
            lambda x: x is None or x > 0,
        )
        self.data_bind("randomize_checks_within_ticks", ck_randChecks)
        self.data_bind("reset_conditions_on_resume", ck_resetOnResume)
        self.data_bind("item_selection", tv_items)

        # bind double click in list to item editor
        tv_items.bind("<Double-Button-1>", lambda _: self.edit())

        # bind changes to global params so that the _changed flag becomes true
        ck_randChecks.configure(command=self._set_changed)
        ck_resetOnResume.configure(command=self._set_changed)

        # propagate widgets that need to be accessed
        self._tv_items = tv_items

        # load the configuration file and update the form
        config_file = get_configfile()
        self.data_set("config_file", config_file)
        self._load_config(config_file)
        self._updateform()

    # update the associated data according to what is in the form
    def _updatedata(self) -> None:
        self._itemlistentries = []
        # encode the invisible list field with the same signature that is used in
        # the _item_ module, so that the corresponding form and item factories can
        # be retrieved dynamically
        for key in self._tasks:
            item = self._tasks[key]
            if not item.private:
                self._itemlistentries.append([item.name, item.hrtype, item.signature])
        for key in self._conditions:
            item = self._conditions[key]
            if not item.private:
                self._itemlistentries.append([item.name, item.hrtype, item.signature])
        for key in self._events:
            item = self._events[key]
            if not item.private:
                self._itemlistentries.append([item.name, item.hrtype, item.signature])
        self._itemlistentries.sort(key=lambda x: x[0])
        # set the changed flag when tick seconds have changed: this is not
        # necessary for the check box based parameters, because the flag is
        # updated every time they get clicked
        tick_secs = self.data_get(
            "scheduler_tick_seconds", DEFAULT_SCHEDULER_TICK_SECONDS
        )
        if tick_secs != self._globals["scheduler_tick_seconds"]:
            self._globals["scheduler_tick_seconds"] = tick_secs
            self._changed = True
        self._globals["randomize_checks_within_ticks"] = self.data_get(
            "randomize_checks_within_ticks", DEFAULT_RANDOMIZE_CHECKS_WITHIN_TICKS
        )
        self._globals["tags"]["reset_conditions_on_resume"] = self.data_get(
            "reset_conditions_on_resume", AppConfig.get("RESET_CONDS_ON_RESUME")
        )

    # update the form fields according to the associated actual data
    def _updateform(self) -> None:
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
            self._tv_items.insert(
                "",
                iid="%s-%s" % (entry[0], entry[2]),
                image=icon,
                values=entry,
                index=tk.END,
            )
        self.data_set(
            "scheduler_tick_seconds",
            self._globals["scheduler_tick_seconds"] or DEFAULT_SCHEDULER_TICK_SECONDS,
        )
        self.data_set(
            "randomize_checks_within_ticks",
            self._globals["randomize_checks_within_ticks"],
        )
        self.data_set(
            "reset_conditions_on_resume",
            self._globals["tags"]["reset_conditions_on_resume"],
        )

    # reset all associated data in the form (does not update fields)
    def _resetdata(self):
        self._tasks = {}
        self._conditions = {}
        self._events = {}
        self._globals = {
            "scheduler_tick_seconds": DEFAULT_SCHEDULER_TICK_SECONDS,
            "randomize_checks_within_ticks": DEFAULT_RANDOMIZE_CHECKS_WITHIN_TICKS,
            "tags": {
                "reset_conditions_on_resume": AppConfig.get("RESET_CONDS_ON_RESUME"),
                # ...
            },
        }
        self._changed = False

    # load the configuration from a TOML file, only display non-private items
    def _load_config(self, fn) -> None:
        self._resetdata()
        default_globals = self._globals.copy()
        tasks, conditions, events, self._globals = read_whenever_config(fn)
        # rebuild default globals that might be missing
        for k in default_globals.keys():
            if k not in self._globals:
                self._globals[k] = default_globals[k]
        for k in default_globals["tags"].keys():
            if k not in self._globals["tags"]:
                self._globals["tags"][k] = default_globals["tags"][k]
        # retrieve items for display and management
        for item in tasks:
            self._tasks[item.name] = item
        for item in conditions:
            self._conditions[item.name] = item
        for item in events:
            self._events[item.name] = item
        # do the same stuff as self._updatedata, without updating globals
        for key in self._tasks:
            item = self._tasks[key]
            if not item.private:
                self._itemlistentries.append([item.name, item.hrtype, item.signature])
        for key in self._conditions:
            item = self._conditions[key]
            if not item.private:
                self._itemlistentries.append([item.name, item.hrtype, item.signature])
        for key in self._events:
            item = self._events[key]
            if not item.private:
                self._itemlistentries.append([item.name, item.hrtype, item.signature])
        self._itemlistentries.sort(key=lambda x: x[0])
        # also set global parameters which belong to app configuration
        AppConfig.delete("RESET_CONDS_ON_RESUME")
        AppConfig.set(
            "RESET_CONDS_ON_RESUME", self._globals["tags"]["reset_conditions_on_resume"]
        )
        self._changed = False

    # save the configuration to a TOML file: add private items when required
    def _save_config(self, fn) -> None:
        # 0. set configuration globals as retrieved from the form
        AppConfig.delete("RESET_CONDS_ON_RESUME")
        AppConfig.set(
            "RESET_CONDS_ON_RESUME", self._globals["tags"]["reset_conditions_on_resume"]
        )
        # 1. reset conditions on resume
        if AppConfig.get("RESET_CONDS_ON_RESUME"):
            from ..internal.reset_conds_on_resume import (
                task_ResetConditionsOnResume,
                condition_ResetConditionsOnResume,
                event_ResetConditionsOnResume,
                name_ResetConditionsOnResume,
            )

            name = name_ResetConditionsOnResume()
            if name not in self._tasks.keys():
                self._tasks[name] = task_ResetConditionsOnResume
            if name not in self._conditions.keys():
                self._conditions[name] = condition_ResetConditionsOnResume
            if name not in self._events.keys():
                self._events[name] = event_ResetConditionsOnResume
        else:
            from ..internal.reset_conds_on_resume import (
                name_ResetConditionsOnResume,
            )

            name = name_ResetConditionsOnResume()
            if name in self._tasks.keys():
                del self._tasks[name]
            if name in self._conditions.keys():
                del self._conditions[name]
            if name in self._events.keys():
                del self._events[name]
        # ...

        # finally write the configuration fle
        write_whenever_config(
            fn,
            [self._tasks[k] for k in self._tasks],
            [self._conditions[k] for k in self._conditions],
            [self._events[k] for k in self._events],
            self._globals,
        )

    # to be called when one of the global parameters has been changed
    def _set_changed(self, changed=True) -> None:
        self._changed = changed

    # check currently loaded items for signature coherence
    def _check_items(self) -> bool:
        signatures = ALL_AVAILABLE_ITEMS_D.keys()
        for k in self._tasks:
            if self._tasks[k].signature not in signatures:
                return False
        for k in self._conditions:
            if self._conditions[k].signature not in signatures:
                return False
        for k in self._events:
            if self._events[k].signature not in signatures:
                return False
        return True

    # command button reactions
    def delete(self) -> None:
        # TODO: do not ignore type error
        item_name, _, item_signature = self.data_get("item_selection")  # type: ignore
        item_type = item_signature.split(":", 1)[0]
        if self.messagebox.askyesno(UI_POPUP_T_CONFIRM, UI_POPUP_DELETEITEM_Q):
            if item_type == "task":
                del self._tasks[item_name]
            elif item_type == "cond":
                del self._conditions[item_name]
            elif item_type == "event":
                del self._events[item_name]
            self._updatedata()
            self._updateform()
            self._changed = True

    def save(self) -> None:
        self._updatedata()
        fn = self.data_get("config_file")
        if fn and self._changed:
            if os.path.exists(fn):
                if self.messagebox.askyesno(UI_POPUP_T_CONFIRM, UI_POPUP_OVERWRITEFILE_Q):
                    self._save_config(fn)
                    self._changed = False
            else:
                self._save_config(fn)
                self._changed = False

    # edit a specific item: to be complete, this is also bound
    # to the double click event for an element of the list
    def edit(self) -> None:
        # TODO: do not ignore type error
        item_name, _, item_signature = self.data_get("item_selection")  # type: ignore
        item_type = item_signature.split(":", 1)[0]

        # task items
        if item_type == "task":
            available_item = ALL_AVAILABLE_ITEMS_D.get(item_signature)
            assert available_item is not None
            _, fform, fitem = available_item
            if fform and fitem.available:
                e = fform(self._tasks[item_name])
                if e is not None:
                    new_item = e.run()
                    if new_item:
                        if new_item.name != item_name:
                            # adjust dependencies
                            for name in self._conditions:
                                cond = self._conditions[name]
                                if item_name in cond.tasks:
                                    tasks = []
                                    for t in cond.tasks:
                                        if t == item_name:
                                            tasks.append(new_item.name)
                                        else:
                                            tasks.append(t)
                                    cond.tasks = tasks
                                    self._conditions[name] = cond
                            # remove the task with old name
                            del self._tasks[item_name]
                        # add the new item or replace the existing one
                        self._tasks[new_item.name] = new_item
                        self._changed = True

        # condition items
        elif item_type == "cond":
            available_item = ALL_AVAILABLE_ITEMS_D.get(item_signature)
            assert available_item is not None
            _, fform, fitem = available_item
            if fform and fitem.available:
                available_tasks = list(
                    x for x in self._tasks.keys() if not is_private_item_name(x)
                )
                e = fform(available_tasks, self._conditions[item_name])
                if e is not None:
                    new_item = e.run()
                    if new_item:
                        if new_item.name != item_name:
                            # adjust dependencies
                            if new_item.type in ("event", "bucket"):
                                for name in self._events:
                                    event = self._events[name]
                                    if event.condition == item_name:
                                        event.condition = new_item.name
                                        self._events[name] = event
                            # remove the condition with old name
                            del self._conditions[item_name]
                        # add the new item or replace the existing one
                        self._conditions[new_item.name] = new_item
                        self._changed = True

        # event items
        elif item_type == "event":
            event_conds = list(
                x
                for x in self._conditions
                if self._conditions[x].type == "event"
                and not is_private_item_name(x)
            )
            available_item = ALL_AVAILABLE_ITEMS_D.get(item_signature)
            assert available_item is not None
            _, fform, fitem = available_item
            if fform and fitem.available:
                e = fform(event_conds, self._events[item_name])
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
    def new(self) -> None:
        e = form_NewItem()
        if e is not None:
            r = e.run()
            if r:
                t, form_class = r
                if t == "task":
                    form = form_class()
                elif t == "cond":
                    available_tasks = [
                        x for x in self._tasks.keys() if not is_private_item_name(x)
                    ]
                    form = form_class(list(available_tasks))
                # note that, since providing a suitable event based
                # condition is mandatory for an event, the form will
                # refuse to create a new event
                elif t == "event":
                    event_conds = list(
                        x
                        for x in self._conditions
                        if self._conditions[x].type == "event"
                        and not is_private_item_name(x)
                    )
                    if event_conds:
                        form = form_class(event_conds)
                    else:
                        self.messagebox.showerror(
                            UI_POPUP_T_ERR, message=UI_POPUP_NOEVENTCONDITIONS_ERR
                        )
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
                    if t == "task":
                        self._tasks[new_item.name] = new_item
                    elif t == "cond":
                        self._conditions[new_item.name] = new_item
                    elif t == "event":
                        self._events[new_item.name] = new_item
                    self._changed = True

        # in the end, update the form on changes
        if self._changed:
            self._updatedata()
            self._updateform()

    # reload the configuration by sending the appropriate message to the
    # main (hidden) application form
    def reload(self) -> None:
        if self.messagebox.askyesno(UI_POPUP_T_CONFIRM, UI_POPUP_RELOADCONFIG_Q):
            if self._app:
                self._app.send_event("<<SchedReloadConfig>>")
        return super().reload()

    # modify the reaction to the quit button so that if the configuration
    # has changed the user is asked whether or not he wants to discard it
    def exit_close(self) -> None:
        if self._changed:
            if self.messagebox.askokcancel(UI_POPUP_T_CONFIRM, UI_POPUP_DISCARDCONFIG_Q):
                return super().exit_close()
        else:
            return super().exit_close()


# end.
