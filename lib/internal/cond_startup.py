# interval condition item

from lib.i18n.strings import *

from tomlkit import items, table

import tkinter as tk
import ttkbootstrap as ttk

from ..forms.ui import *

# since a condition is defined, the base form is the one for conditions
from ..forms.cond import form_Condition

from ..items.cond_interval import IntervalCondition
from ..items.itemhelp import CheckedTable, ConfigurationError


# an interval based condition
class StartupCondition(IntervalCondition):

    # availability at class level
    item_type = "interval"
    item_subtype = "startup"
    item_hrtype = ITEM_COND_STARTUP
    available = False

    def __init__(self, t: items.Table | None = None):
        # first initialize the base class
        IntervalCondition.__init__(self, t)

        # then set type (same as base), subtype and human readable name
        self.type = self.item_type
        self.subtype = self.item_subtype
        self.hrtype = self.item_hrtype
        if t:
            assert t.get("type") == self.type
            self.tags = t.get("tags", table())
            assert isinstance(self.tags, items.Table)
            assert self.tags.get("subtype") == self.subtype
        else:
            self.tags = table()
            self.tags.append("subtype", self.subtype)
        self.interval_seconds = 0

    def load_checking(
        self, item: items.Table, item_line: int, tasks: list[str] | None = None
    ):
        try:
            super().load_checking(item, item_line, tasks)
        # ignore the erro on `interval_seconds`
        except ConfigurationError as e:
            if e.entry_name != "interval_seconds":
                raise e
        self.type = self.item_type
        self.subtype = self.item_subtype
        self.hrtype = self.item_hrtype
        tab = CheckedTable(item, item_line)
        assert tab.get_str("type") == self.type
        # since this is used for checks only, check that this is still zero
        self.interval_seconds = tab.get_int_between(
            "interval_seconds", 0, 0, mandatory=True
        )

    @classmethod
    def check_tags(cls, tags):
        missing = []
        errors = []
        if errors or missing:
            return (errors, missing)
        return None

    def as_table(self):
        return IntervalCondition.as_table(self)


# specialized subform: it will never be shown because the item is not available
class form_StartupCondition(form_Condition):

    def __init__(self, tasks_available, item=None):
        if item:
            assert isinstance(item, StartupCondition)
        else:
            item = StartupCondition()
        super().__init__(UI_TITLE_EVENTCOND, tasks_available, item)
        assert isinstance(self._item, StartupCondition)

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # widgets section
        l_noParams = ttk.Label(area, text=UI_CAPTION_NOSPECIFICPARAMS)

        # arrange items in the grid
        l_noParams.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        # update the form
        self._updateform()


# end.
