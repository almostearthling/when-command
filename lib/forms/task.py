# base task form

import re
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from ..i18n.strings import *
from .ui import *

from ..repocfg import AppConfig

from ..items.task import Task

from ..utility import is_valid_item_name, clean_caption


# task box base class: since this is the class that will be used in derived
# forms too, in order to avoid variable name conflicts, all variable names
# used here are prefixed with '@': agreeing that base values are prefixed
# and specific values are not, consistent names can be used in derived forms
# without conflicts
class form_Task(ApplicationForm):

    def __init__(self, title, item=None):
        size = AppConfig.get("SIZE_EDITOR_FORM")
        assert isinstance(size, tuple)
        bbox = (BBOX_OK, BBOX_CANCEL)
        super().__init__(title, size, None, bbox)

        # only perform checks when the user presses OK
        self.set_autocheck(False)

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # common widgets
        l_itemName = ttk.Label(area, text=UI_FORM_NAME_SC)
        e_itemName = ttk.Entry(area)
        sep = ttk.Separator(area)

        # the following is the client area that is exposed to derived forms
        self._sub_contents = ttk.Frame(area)
        self._sub_contents.rowconfigure(0, weight=1)
        self._sub_contents.columnconfigure(0, weight=1)

        # arrange top items in the grid
        l_itemName.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_itemName.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        sep.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=PAD)
        self._sub_contents.grid(row=99, column=0, columnspan=2, sticky=tk.NSEW)

        # expand appropriate sections
        area.rowconfigure(index=99, weight=1)
        area.columnconfigure(1, weight=1)

        # bind data to widgets
        self.data_bind("@name", e_itemName, TYPE_STRING, is_valid_item_name)

        # keep a database of captions associated to data subject to check
        self._captions = {
            "@name": clean_caption(UI_FORM_NAME_SC),
        }

        # finally set the item
        if item:
            self.set_item(item)
        else:
            self.reset_item()
        self.changed = False

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
        messagebox.showerror(UI_POPUP_T_ERR, msg)

    # contents is the root for slave widgets
    @property
    def contents(self) -> ttk.Frame:
        return self._sub_contents

    def _updateform(self) -> None:
        if self._item:
            assert isinstance(self._item, Task)
            self.data_set("@name", self._item.name)
        else:
            self.data_set("@name", "")

    # the data update utility loads data into the item
    def _updatedata(self) -> None:
        assert isinstance(self._item, Task)
        name = self.data_get("@name")
        if name is not None:
            self._item.name = name

    # set and remove the associated item
    def set_item(self, item) -> None:
        assert isinstance(item, Task)
        try:
            self._item = item.__class__(
                item.as_table()
            )  # get an exact copy to mess with
        except ValueError:
            self._item = item  # item was newly created: use it

    def reset_item(self) -> None:
        self._item = None

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
    def run(self) -> Task | None:
        super().run()
        return self._item


# end.
