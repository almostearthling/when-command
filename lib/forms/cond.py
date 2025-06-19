# base condition form

import re
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from ..i18n.strings import *
from .ui import *

from ..repocfg import AppConfig

from ..items.cond import Condition

from ..utility import is_valid_item_name, clean_caption


# condition box base class: since this is the class that will be used in
# derived forms too, in order to avoid variable name conflicts, all variable
# names used here are prefixed with '@': agreeing that base values are
# prefixed and specific values are not, consistent names can be used in
# derived forms without conflicts
class form_Condition(ApplicationForm):

    def __init__(self, title, tasks_available, item=None):
        size = AppConfig.get("SIZE_EDITOR_FORM")
        bbox = (BBOX_OK, BBOX_CANCEL)
        super().__init__(title, size, None, bbox)

        tasks_available = tasks_available.copy()
        tasks_available.sort()

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)
        PAD = WIDGET_PADDING_PIXELS

        # enclosing notebook
        nb_item = ttk.Notebook(area)
        area_common = ttk.Frame(nb_item)

        # the following is the client area that is exposed to derived forms
        self._area_specific = ttk.Frame(nb_item)

        # feed the notebook
        nb_item.add(area_common, text=UI_FORM_COMMON_PARAMS)
        nb_item.add(self._area_specific, text=UI_FORM_SPECIFIC_PARAMS)
        nb_item.grid(row=0, column=0, sticky=tk.NSEW)

        # top level widgets section
        l_itemName = ttk.Label(area_common, text=UI_FORM_NAME_SC)
        e_itemName = ttk.Entry(area_common)
        ck_itemRecurring = ttk.Checkbutton(area_common, text=UI_FORM_CHECKCONDRECURRENT)
        ck_itemSuspended = ttk.Checkbutton(
            area_common, text=UI_FORM_SUSPENDCONDATSTARTUP
        )
        l_maxTasksRetries = ttk.Label(area_common, text=UI_FORM_MAXTASKRETRIES_SC)
        e_maxTasksRetries = ttk.Entry(area_common)
        sep1 = ttk.Separator(area_common)

        l_tasks = ttk.Label(area_common, text=UI_FORM_ACTIVETASKS_SC)
        # build a scrolled frame for the treeview
        sftv_tasks = ttk.Frame(area_common)
        tv_tasks = ttk.Treeview(
            sftv_tasks, columns=("seq", "tasks"), show="", displaycolumns=(1,), height=5
        )
        sb_tasks = ttk.Scrollbar(sftv_tasks, orient=tk.VERTICAL, command=tv_tasks.yview)
        tv_tasks.configure(yscrollcommand=sb_tasks.set)
        tv_tasks.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_tasks.pack(side=tk.RIGHT, fill=tk.Y)
        ck_execSequence = ttk.Checkbutton(
            area_common, text=UI_FORM_RUNTASKSSEQUENTIALLY
        )

        # choose task section
        area_taskchoose = ttk.Frame(area_common)
        l_chooseTask = ttk.Label(area_taskchoose, text=UI_FORM_TASK_SC)
        cb_chooseTask = ttk.Combobox(
            area_taskchoose, values=tasks_available, state="readonly"
        )
        b_addTask = ttk.Button(
            area_taskchoose,
            text=UI_ADD,
            width=BUTTON_STANDARD_WIDTH,
            command=self.add_task,
        )
        b_delTask = ttk.Button(
            area_taskchoose,
            text=UI_DEL,
            width=BUTTON_STANDARD_WIDTH,
            command=self.del_task,
        )

        # choose task section: arrange items
        l_chooseTask.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cb_chooseTask.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        b_addTask.grid(row=0, column=2, sticky=tk.E, padx=PAD, pady=PAD)
        b_delTask.grid(row=0, column=3, sticky=tk.E, padx=PAD, pady=PAD)

        # self._tv_tasks.bind('<Double-Button-1>', lambda _: self.recall_task())

        # control flow section
        area_ctlflow = ttk.Frame(area_common)
        rb_noCheck = ttk.Radiobutton(
            area_ctlflow, text=UI_FORM_BREAKNEVER, value="break_none"
        )
        rb_breakFailure = ttk.Radiobutton(
            area_ctlflow, text=UI_FORM_BREAKONFAILURE, value="break_failure"
        )
        rb_breakSuccess = ttk.Radiobutton(
            area_ctlflow, text=UI_FORM_BREAKONSUCCESS, value="break_success"
        )

        # control flow section: arrange widgets
        rb_noCheck.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        rb_breakFailure.grid(row=1, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        rb_breakSuccess.grid(row=2, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        # arrange top items items in the appropriate notebook
        l_itemName.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_itemName.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        ck_itemRecurring.grid(row=1, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        ck_itemSuspended.grid(row=2, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        l_maxTasksRetries.grid(row=4, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_maxTasksRetries.grid(row=4, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        sep1.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=PAD)
        l_tasks.grid(row=10, column=0, columnspan=2, sticky=tk.W, padx=PAD, pady=PAD)
        sftv_tasks.grid(
            row=11, column=0, columnspan=2, sticky=tk.NSEW, padx=PAD, pady=PAD
        )
        area_taskchoose.grid(row=12, column=0, columnspan=2, sticky=tk.EW)
        ck_execSequence.grid(
            row=13, column=0, columnspan=2, sticky=tk.EW, padx=PAD, pady=PAD
        )
        area_ctlflow.grid(row=14, column=0, columnspan=2, sticky=tk.EW)

        ck_itemRecurring.bind("<ButtonPress-1>", lambda _: self._check_recurring())
        ck_itemRecurring.bind("<KeyPress-space>", lambda _: self._check_recurring())

        # expand appropriate sections
        area_common.rowconfigure(index=11, weight=1)
        area_common.columnconfigure(1, weight=1)
        area_taskchoose.columnconfigure(1, weight=1)
        self._area_specific.rowconfigure(index=0, weight=1)
        self._area_specific.columnconfigure(index=0, weight=1)

        # bind data to widgets
        self.data_bind("@name", e_itemName, TYPE_STRING, is_valid_item_name)
        self.data_bind("@recurring", ck_itemRecurring)
        self.data_bind(
            "@max_tasks_retries", e_maxTasksRetries, TYPE_INT, lambda x: x >= -1
        )
        self.data_bind("@suspended", ck_itemSuspended)
        self.data_bind("@tasks_selection", tv_tasks)
        self.data_bind("@choose_task", cb_chooseTask, TYPE_STRING)
        self.data_bind("@execute_sequence", ck_execSequence)
        self.data_bind(
            "@control_flow", (rb_noCheck, rb_breakFailure, rb_breakSuccess), TYPE_STRING
        )

        # keep a database of captions associated to data subject to check
        self._captions = {
            "@name": clean_caption(UI_FORM_NAME_SC),
            "@max_tasks_retries": clean_caption(UI_FORM_MAXTASKRETRIES_SC),
        }

        # propagate widgets that need to be accessed
        self._tv_tasks = tv_tasks
        self._max_retries = e_maxTasksRetries

        # finally set the item
        if item:
            self.set_item(item)
        else:
            self.reset_item()
        self._check_recurring()
        # self._max_retries.config(state=tk.NORMAL)
        self.changed = False

    def add_task(self):
        task = self.data_get("@choose_task")
        if task:
            self._tasks.append(task)
        self._updatedata()
        self._updateform()

    def del_task(self):
        elem = self.data_get("@tasks_selection")
        if elem:
            idx = int(elem[0])
            del self._tasks[idx]
            self._updatedata()
            self._updateform()

    def add_check_caption(self, dataname, caption):
        assert self.data_exists(dataname)
        self._captions[dataname] = clean_caption(caption)

    def _invalid_data_captions(self):
        res = []
        for k in self._captions:
            if not self.data_valid(k):
                res.append(self._captions[k])
        if not res:
            return None
        else:
            return res

    def _popup_invalid_data(self, captions):
        captions.sort()
        capts = "- " + "\n- ".join(captions)
        msg = UI_POPUP_INVALIDPARAMETERS_T % capts
        messagebox.showerror(UI_POPUP_T_ERR, msg)

    def _check_recurring(self):
        # we use the opposite of the value because of <ButtonPress-1>: anyway
        # the <ButtonRelease-1> counterpart does not work so well (same thing
        # for <KeyPress-space>, while <KeyRelease-space> does better)
        not_rec = not self.data_get("@recurring") or False
        if not_rec:
            self._max_retries.config(state=tk.DISABLED)
        else:
            self._max_retries.config(state=tk.NORMAL)

    # contents is the root for slave widgets
    @property
    def contents(self):
        return self._area_specific

    def _updateform(self):
        self._tv_tasks.delete(*self._tv_tasks.get_children())
        try:
            if self._item:
                if not self._item.recurring:
                    self._max_retries.config(state=tk.NORMAL)
                else:
                    self._max_retries.config(state=tk.DISABLED)
                self.data_set("@name", self._item.name)
                self.data_set("@recurring", self._item.recurring or False)
                self.data_set("@max_tasks_retries", self._item.max_tasks_retries or 0)
                self.data_set("@suspended", self._item.suspended or False)
                self.data_set(
                    "@execute_sequence",
                    (
                        self._item.execute_sequence
                        if self._item.execute_sequence is False
                        else True
                    ),
                )
                idx = 0
                for task in self._tasks:
                    self._tv_tasks.insert(
                        "", iid="%s-%s" % (idx, task), values=(idx, task), index=tk.END
                    )
                    idx += 1
                if self._item.break_on_failure:
                    self.data_set("@control_flow", "break_failure")
                elif self._item.break_on_success:
                    self.data_set("@control_flow", "break_success")
                else:
                    self.data_set("@control_flow", "break_none")
            else:
                self._max_retries.config(state=tk.DISABLED)
                self.data_set("@name", "")
                self.data_set("@control_flow", "break_none")
                self.data_set("@recurring", True)
                self.data_set("@suspended", False)
                self.data_set("@execute_sequence", True)
            self.data_set("@choose_task", "")
        # the real check will be performed when the user presses `OK`
        except ValueError:
            pass

    # the data update utility loads data into the item
    def _updatedata(self):
        name = self.data_get("@name")
        if name is not None:
            self._item.name = name
        self._item.recurring = self.data_get("@recurring") or None
        if self._item.recurring:
            self._item.max_tasks_retries = None
        else:
            self._item.max_tasks_retries = self.data_get("@max_tasks_retries") or None
        self._item.suspended = self.data_get("@suspended") or None
        self._item.execute_sequence = (
            False if not self.data_get("@execute_sequence") else None
        )
        control_flow = self.data_get("@control_flow")
        if control_flow == "break_failure":
            self._item.break_on_failure = True
            self._item.break_on_success = None
        elif control_flow == "break_success":
            self._item.break_on_failure = None
            self._item.break_on_success = True
        else:
            self._item.break_on_failure = None
            self._item.break_on_success = None
        self._item.tasks = self._tasks.copy()

    # set and remove the associated item
    def set_item(self, item):
        assert isinstance(item, Condition)
        try:
            self._item = item.__class__(
                item.as_table()
            )  # get an exact copy to mess with
        except ValueError:
            self._item = item  # item was newly created: use it
        self._tasks = self._item.tasks.copy()

    def reset_item(self):
        self._item = None
        self._tasks = []

    # command button reactions: cancel deletes the current item so that None
    # is returned upon dialog close, while ok finalizes item initialization
    # and lets the run() function return a configured item
    def exit_cancel(self):
        self._item = None
        return super().exit_cancel()

    def exit_ok(self):
        errs = self._invalid_data_captions()
        if errs is None:
            self._updatedata()
            return super().exit_ok()
        else:
            self._popup_invalid_data(errs)

    # main loop: returns the current item if any
    def run(self):
        super().run()
        return self._item


# end.
