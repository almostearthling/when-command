# base condition form

import tkinter as tk
import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from ..i18n.strings import *
from .ui import *

from ..repocfg import AppConfig

from ..items.cond import Condition

from ..utility import (
    is_valid_item_name,
    clean_caption,
    is_private_item_name,
    whenever_has_lua_sync,
)
from ..internal import multi_conds_run_task as mcrt


# add a negated disabled to tk dictionary (please forgive me)
tk.NOT_DISABLED = f"!{tk.DISABLED}"  # type: ignore


# condition box base class: since this is the class that will be used in
# derived forms too, in order to avoid variable name conflicts, all variable
# names used here are prefixed with '@': agreeing that base values are
# prefixed and specific values are not, consistent names can be used in
# derived forms without conflicts
class form_Condition(ApplicationForm):

    def __init__(self, title, tasks_available, item=None):
        size = AppConfig.get("SIZE_EDITOR_FORM")
        assert isinstance(size, tuple)
        bbox = (BBOX_OK, BBOX_CANCEL)
        super().__init__(title, size, None, bbox)

        # only perform checks when the user presses OK
        self.set_autocheck(False)

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
        ck_mcrtActivateFurther = ttk.Checkbutton(
            area_common, text=UI_FORM_ACTIVATEFURTHERCONDS
        )
        sep1 = ttk.Separator(area_common)

        # disable confluence if confluence condition is not available
        if not mcrt.ConfluenceCondition.available:
            ck_mcrtActivateFurther.config(state=tk.DISABLED)

        l_tasks = ttk.Label(area_common, text=UI_FORM_ACTIVETASKS_SC)
        # build a scrolled frame for the treeview
        sftv_tasks = ttk.Frame(area_common)
        tv_tasks = ttk.Treeview(
            sftv_tasks,
            columns=("seq", "tasks"),
            show="",
            displaycolumns=(1,),
            height=5,
            bootstyle=ttkc.SECONDARY,
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

        # control flow section
        area_ctlflow = ttk.Frame(area_common)
        area_ctlflowL = ttk.Frame(area_ctlflow)
        area_ctlflowR = ttk.Frame(area_ctlflow)
        area_ctlflowRsub = ttk.Frame(area_ctlflowR)
        area_ctlflowL.grid(row=0, column=0, sticky=tk.W)
        area_ctlflowR.grid(row=0, column=1, sticky=tk.SE)
        area_ctlflowRsub.grid(row=0, column=0, sticky=tk.S)
        rb_noCheck = ttk.Radiobutton(
            area_ctlflowL, text=UI_FORM_BREAKNEVER, value="break_none"
        )
        rb_breakFailure = ttk.Radiobutton(
            area_ctlflowL, text=UI_FORM_BREAKONFAILURE, value="break_failure"
        )
        rb_breakSuccess = ttk.Radiobutton(
            area_ctlflowL, text=UI_FORM_BREAKONSUCCESS, value="break_success"
        )
        l_maxTasksRetries = ttk.Label(area_ctlflowRsub, text=UI_FORM_MAXTASKRETRIES_SC)
        e_maxTasksRetries = ttk.Entry(area_ctlflowRsub, width=10)

        # control flow section: arrange widgets
        rb_noCheck.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        rb_breakFailure.grid(row=1, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        rb_breakSuccess.grid(row=2, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        l_maxTasksRetries.grid(row=0, column=0, sticky=tk.E, padx=PAD, pady=PAD)
        e_maxTasksRetries.grid(row=0, column=1, sticky=tk.E, padx=PAD, pady=PAD)

        # arrange top items items in the appropriate notebook
        l_itemName.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_itemName.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        ck_itemRecurring.grid(row=1, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        ck_itemSuspended.grid(row=2, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        ck_mcrtActivateFurther.grid(row=3, column=1, sticky=tk.W, padx=PAD, pady=PAD)
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
        ck_mcrtActivateFurther.bind("<ButtonPress-1>", lambda _: self._mcrt_confluent())
        ck_mcrtActivateFurther.bind(
            "<KeyPress-space>", lambda _: self._mcrt_confluent()
        )

        # expand appropriate sections
        area_common.rowconfigure(index=11, weight=1)
        area_common.columnconfigure(1, weight=1)
        area_taskchoose.columnconfigure(1, weight=1)
        area_ctlflow.columnconfigure(0, weight=1)
        self._area_specific.rowconfigure(index=0, weight=1)
        self._area_specific.columnconfigure(index=0, weight=1)

        # bind data to widgets
        self.data_bind("@name", e_itemName, TYPE_STRING, is_valid_item_name)
        self.data_bind("@recurring", ck_itemRecurring)
        self.data_bind("@confluent", ck_mcrtActivateFurther)
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

        # keep a list of task related widget to disable them when needed
        self._task_elems = [
            # current list
            l_tasks,
            tv_tasks,
            sb_tasks,
            # chooser
            l_chooseTask,
            cb_chooseTask,
            b_addTask,
            b_delTask,
            # control flow
            ck_execSequence,
            rb_noCheck,
            rb_breakSuccess,
            rb_breakFailure,
            # retry control
            l_maxTasksRetries,
            e_maxTasksRetries,
        ]

        # propagate widgets that need to be accessed
        self._tv_tasks = tv_tasks
        self._max_retries = e_maxTasksRetries

        # finally set the item
        if item:
            self.set_item(item)
        else:
            self.reset_item()
        self._check_recurring()
        self.changed = False

    def add_task(self) -> None:
        elem = self.data_get("@choose_task")
        self._updatedata()
        if elem:
            self._tasks.append(elem)
        self._updateform()

    def del_task(self) -> None:
        elem = self.data_get("@tasks_selection")
        self._updatedata()
        if elem:
            idx = int(elem[0])
            del self._tasks[idx]
            self._updateform()

    def add_check_caption(self, dataname, caption) -> None:
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

    def _popup_invalid_data(self, captions) -> None:
        captions.sort()
        capts = "- " + "\n- ".join(captions)
        msg = UI_POPUP_INVALIDPARAMETERS_T % capts
        self.messagebox.showerror(UI_POPUP_T_ERR, msg)

    def _check_recurring(self) -> None:
        # we use the opposite of the value because of <ButtonPress-1>: anyway
        # the <ButtonRelease-1> counterpart does not work so well (same thing
        # for <KeyPress-space>, while <KeyRelease-space> does better)
        not_rec = not self.data_get("@recurring") or False
        if not_rec:
            self.data_set("@max_tasks_retries", 0)
            self._max_retries.config(state=tk.DISABLED)
        else:
            # before enabling, check that this is not a confluent condition
            if not self.data_get("@confluent"):
                self._max_retries.config(state=tk.NORMAL)

    def _mcrt_confluent(self, force=False) -> None:
        # same consideration as above; this function also disables all task
        # related form widgets when the condition is set to be confluent
        if force:
            confluent = True
        else:
            confluent = not self.data_get("@confluent") or False
        # retrieve the name of the MCRT updater task
        mcrt_updater = mcrt.updater_name()
        if confluent:
            self.data_set("@name", "")
            self.data_set("@control_flow", "break_none")
            self.data_set("@execute_sequence", True)
            self.data_set("@choose_task", "")
            self.data_set("@max_tasks_retries", 0)
            self._tv_tasks.delete(*self._tv_tasks.get_children())
            self._tasks = [mcrt_updater]
            for elem in self._task_elems:
                spec = list(elem.state())
                if tk.DISABLED not in spec:
                    spec.append(tk.DISABLED)
                if tk.NOT_DISABLED in spec:  # type:ignore
                    spec.remove(tk.NOT_DISABLED)  # type:ignore
                elem.state(spec)
                # TODO: there must be a better way to achieve this
                if "config" in elem.__dict__:
                    elem.config(state=tk.DISABLED)
        else:
            for elem in self._task_elems:
                spec = list(elem.state())
                if tk.DISABLED in spec:
                    spec.remove(tk.DISABLED)
                if tk.NOT_DISABLED not in spec:  # type:ignore
                    spec.append(tk.NOT_DISABLED)  # type:ignore
                elem.state(spec)
                # TODO: there must be a better way to do this (same as above)
                if "config" in elem.__dict__:
                    elem.config(state=tk.NORMAL)
            if mcrt_updater in self._tasks:
                self._tasks.remove(mcrt_updater)

    # contents is the root for slave widgets
    @property
    def contents(self) -> ttk.Frame:
        return self._area_specific

    def _updateform(self) -> None:
        self._tv_tasks.delete(*self._tv_tasks.get_children())
        if self._item:
            assert isinstance(self._item, Condition)
            if not self._item.recurring:
                self._max_retries.config(state=tk.NORMAL)
            else:
                self._max_retries.config(state=tk.DISABLED)
            self.data_set("@name", self._item.name)
            self.data_set("@recurring", self._item.recurring or False)
            self.data_set("@suspended", self._item.suspended or False)
            if mcrt.is_confluent_cond(self._item):
                self.data_set("@confluent", True)
                self._mcrt_confluent(True)
            else:
                self.data_set("@confluent", False)
                self.data_set("@max_tasks_retries", self._item.max_tasks_retries or 0)
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
                    # this is correct and avoid listing possible confluent tasks
                    if not is_private_item_name(task):
                        self._tv_tasks.insert(
                            "",
                            iid="%s-%s" % (idx, task),
                            values=(idx, task),
                            index=tk.END,
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
            self.data_set("@max_tasks_retries", 0)
            self.data_set("@confluent", False)
        self.data_set("@choose_task", "")

    # the data update utility loads data into the item
    def _updatedata(self) -> None:
        assert isinstance(self._item, Condition)
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
    def set_item(self, item: Condition) -> None:
        assert isinstance(item, Condition)
        try:
            self._item = item.__class__(
                item.as_table()
            )  # get an exact copy to mess with
        except ValueError:
            self._item = item  # item was newly created: use it
        assert isinstance(self._item.tasks, list)
        # check if this is a confluent condition and set widgets accordingly
        if mcrt.is_confluent_cond(item):
            self._tasks = list()
            self.data_set("@confluent", True)
            self._mcrt_confluent(True)
        else:
            self._tasks = self._item.tasks.copy()
            self.data_set("@confluent", False)

    def reset_item(self) -> None:
        self._item = None
        self._tasks = []

    # command button reactions: cancel deletes the current item so that None
    # is returned upon dialog close, while ok finalizes item initialization
    # and lets the run() function return a configured item
    def exit_cancel(self) -> None:
        self._item = None
        return super().exit_cancel()

    def exit_ok(self) -> None:
        errs = self._invalid_data_captions()
        if errs is None:
            self._updatedata()
            return super().exit_ok()
        else:
            self._popup_invalid_data(errs)

    # main loop: returns the current item if any
    def run(self) -> Condition | None:
        super().run()
        return self._item


# end.
