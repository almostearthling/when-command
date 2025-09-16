# hibernate

# this header is common to all extra modules
from tomlkit import items, table

import tkinter as tk
import ttkbootstrap as ttk

from ..i18n.strings import *

from ..forms.ui import *


# since a task is defined, the base form is the one for tasks
from ..forms.task import form_Task

# import item to derive from
from ..items.task_command import CommandTask


# imports specific to this module
import shutil
import sys


# resource strings (not internationalized for the moment)
ITEM_HR_NAME = "Hibernate Task"

UI_FORM_TITLE = f"{UI_APP}: Hibernate Task Editor"

# default values


# localize the aforementioned constants: this pattern is the same in every
# extra module
from .i18n.extra_locale import localized_strings

m = localized_strings(__name__)
if m is not None:
    ITEM_HR_NAME = m.ITEM_HR_NAME
    UI_FORM_TITLE = m.UI_FORM_TITLE


# check for availability (at the moment Windows only)
def _available():
    if sys.platform.startswith("win"):
        if shutil.which("shutdown.exe"):
            return True
        return False
    # elif sys.platform == 'linux':
    #     global ITEM_HR_NAME, UI_FORM_TITLE
    #     ITEM_HR_NAME += " (Gnome)"
    #     UI_FORM_TITLE += " (Gnome)"
    #     if shutil.which("gnome-session-quit"):
    #         return True
    #     return False
    return False


# the specific item is derived from the actual parent item
class HibernateTask(CommandTask):

    # availability at class level: these variables *MUST* be set for all items
    item_type = "command"
    item_subtype = "hibernate"
    item_hrtype = ITEM_HR_NAME
    available = _available()

    def __init__(self, t: items.Table | None = None):
        # first initialize the base class (mandatory)
        CommandTask.__init__(self, t)

        # then set type (same as base), subtype and human readable name: this
        # is mandatory in order to correctly display the item in all forms
        self.type = self.item_type
        self.subtype = self.item_subtype
        self.hrtype = self.item_hrtype

        # initializing from a table should always have this form:
        if t:
            assert t.get("type") == self.type
            self.tags = t.get("tags")
            assert isinstance(self.tags, items.Table)
            assert self.tags.get("subtype") == self.subtype

        # while creating a new item must always initialize specific parameters
        else:
            self.tags = table()
            self.tags.append("subtype", self.subtype)

        self.updateitem()

    def updateitem(self):
        # set base item properties according to specific parameters in `tags`
        if sys.platform.startswith("win"):
            self.command = "shutdown.exe"
            self.command_arguments = ["/s"]
        # elif sys.platform == 'linux':
        #     self.command = "gnome-session-quit"
        #     self.command_arguments = [
        #         # "--no-prompt",
        #         # "--hibernate",
        #     ]
        self.startup_path = "."

    @classmethod
    def check_tags(cls, tags):
        if tags is None:
            return "required specific parameters (`tags`) not found"
        else:
            missing = []
            errors = []
            subtype = tags.get("subtype")
            if subtype is None:
                missing.append("subtype")
            elif subtype != cls.item_subtype:
                errors.append("subtype")
            if errors or missing:
                return (errors, missing)
        return None


# dedicated form definition derived directly from one of the base forms
class form_HibernateTask(form_Task):

    def __init__(self, item=None):

        # check that item is the expected one for safety, build one by default
        if item:
            assert isinstance(item, HibernateTask)
        else:
            item = HibernateTask()
        super().__init__(UI_FORM_TITLE, item)

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # build the UI elements as needed and configure the layout
        l_noparams = ttk.Label(area, text=UI_CAPTION_NOSPECIFICPARAMS)
        l_noparams.configure(anchor=tk.CENTER)
        pad = ttk.Frame(area)

        l_noparams.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        pad.grid(row=10, column=0, sticky=tk.NSEW)

        area.columnconfigure(0, weight=1)
        area.rowconfigure(10, weight=1)

        # always update the form at the end of initialization
        self._updateform()

    # no need actually for this  definition
    # def _updateform(self):
    #     return super()._updateform()

    # no need actually for this  definition
    # def _updatedata(self):
    #     return super()._updatedata()


# function common to all extra modules to declare class items as factories
def factories():
    return (HibernateTask, form_HibernateTask)


# end.
