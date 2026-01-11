# base event form

import tkinter as tk
import ttkbootstrap as ttk

from ..i18n.strings import *
from .ui import *

from ..repocfg import AppConfig

from ..items.event import Event

from ..utility import is_valid_item_name, clean_caption


# event box base class: since this is the class that will be used in derived
# forms too, in order to avoid variable name conflicts, all variable names
# used here are prefixed with '@': agreeing that base values are prefixed
# and specific values are not, consistent names can be used in derived forms
class form_Event(ApplicationForm):

    def __init__(self, title, conditions_available, item=None):
        size = AppConfig.get("SIZE_EDITOR_FORM")
        assert isinstance(size, tuple)
        bbox = (BBOX_OK, BBOX_CANCEL)
        super().__init__(title, size, None, bbox)

        # only perform checks when the user presses OK
        self.set_autocheck(False)

        conditions_available = conditions_available.copy()
        conditions_available.sort()

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # common widgets
        l_itemName = ttk.Label(area, text=UI_FORM_NAME_SC)
        e_itemName = ttk.Entry(area)
        l_associatedCondition = ttk.Label(area, text=UI_FORM_COND_SC)
        cb_associatedCondition = ttk.Combobox(
            area, values=conditions_available, state="readonly"
        )
        sep = ttk.Separator(area)

        # the following is the client area that is exposed to derived forms
        self._sub_contents = ttk.Frame(area)
        self._sub_contents.rowconfigure(0, weight=1)
        self._sub_contents.columnconfigure(0, weight=1)
        self._sub_contents.grid(row=10, column=0, columnspan=2, sticky=tk.NSEW)

        # arrange top items in the grid
        l_itemName.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_itemName.grid(row=0, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        l_associatedCondition.grid(row=1, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cb_associatedCondition.grid(row=1, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        sep.grid(row=2, column=0, sticky=tk.EW, columnspan=2, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.columnconfigure(1, weight=1)
        area.rowconfigure(10, weight=1)

        # bind data to widgets
        self.data_bind("@name", e_itemName, TYPE_STRING, is_valid_item_name)
        self.data_bind(
            "@condition", cb_associatedCondition, TYPE_STRING, lambda x: bool(x)
        )

        # keep a database of captions associated to data subject to check
        self._captions = {
            "@name": clean_caption(UI_FORM_NAME_SC),
            "@condition": clean_caption(UI_FORM_COND_SC),
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
        self.messagebox.showerror(UI_POPUP_T_ERR, msg)

    # contents is the root for slave widgets
    @property
    def contents(self) -> ttk.Frame:
        return self._sub_contents

    def _updateform(self) -> None:
        if self._item:
            assert isinstance(self._item, Event)
            self.data_set("@name", self._item.name)
            self.data_set("@condition", self._item.condition or "")
        else:
            self.data_set("@name", "")
            self.data_set("@condition", "")

    # the data update utility loads data into the item
    def _updatedata(self) -> None:
        assert isinstance(self._item, Event)
        name = self.data_get("@name")
        if name is not None:
            self._item.name = name
            self._item.condition = self.data_get("@condition")

    # set and remove the associated item
    def set_item(self, item) -> None:
        assert isinstance(item, Event)
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
    def run(self) -> Event | None:
        super().run()
        return self._item


# end.
