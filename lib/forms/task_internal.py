# internal command task form

import re
import os.path
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from ..i18n.strings import *
from .ui import *

from .task import form_Task
from ..items.task_internal import InternalCommandTask


# commands are checked for formal validity: no check on existing/not existing
# items is made; the dictionary associates all commands to a function that
# checks for formal validity
_RE_VALIDNAME = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")

_COMMANDS = {
    "pause": lambda s: s == "",
    "resume": lambda s: s == "",
    "exit": lambda s: s == "",
    "quit": lambda s: s == "",
    "kill": lambda s: s == "",
    "reset_conditions": lambda s: s == ""
    or len(list(x for x in s.split() if not _RE_VALIDNAME.match(x))) == 0,
    "suspend_condition": lambda s: _RE_VALIDNAME.match(s),
    "resume_condition": lambda s: _RE_VALIDNAME.match(s),
    "trigger": lambda s: _RE_VALIDNAME.match(s),
    "configure": lambda s: os.path.exists(s),
}


def _check_command(s: str):
    l = s.split(None, 1)
    if len(l) == 0:
        return False
    elif len(l) == 1:
        command, args = l[0], ""
    elif len(l) == 2:
        command, args = l[0], l[1]
    else:
        # unreachable
        return False
    if command in _COMMANDS.keys():
        f = _COMMANDS[command]
        return f(args)
    else:
        return False


class form_InternalCommandTask(form_Task):

    def __init__(self, item=None):
        if item:
            assert isinstance(item, InternalCommandTask)
        else:
            item = InternalCommandTask()
        super().__init__(UI_TITLE_INTERNALTASK, item)

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # script section
        l_command = ttk.Label(area, text=UI_FORM_COMMAND_SC)
        e_command = ttk.Entry(area)
        pad = ttk.Frame(area)

        l_command.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_command.grid(row=1, column=0, sticky=tk.EW, padx=PAD, pady=PAD)
        pad.grid(row=10, column=0, sticky=tk.NSEW)

        area.columnconfigure(0, weight=1)
        area.rowconfigure(10, weight=1)

        self.data_bind("command", e_command, TYPE_STRING, _check_command)

        # add captions of data to be checked
        self.add_check_caption("command", UI_FORM_COMMAND_SC)

        # update the form
        self._updateform()

    def _updatedata(self):
        self._item.command = self.data_get("command").strip() or ""
        return super()._updatedata()

    def _updateform(self):
        try:
            self.data_set("command", self._item.command)
        # the real check will be performed when the user presses `OK`
        except ValueError:
            pass
        return super()._updateform()


# end.
