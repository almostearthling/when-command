# history box

from ..i18n.strings import *
from ..repocfg import AppConfig

import tkinter as tk
import ttkbootstrap as ttk

from .ui import *
from ..utility import get_ui_image

from ..icons import OUTCOME_OK_ICON16x16 as OK_ICON
from ..icons import OUTCOME_FAIL_ICON16x16 as FAIL_ICON
from ..icons import OUTCOME_UNKNOWN_ICON16x16 as UNK_ICON


# form class: this form is fixed and will not be derived
class form_History(ApplicationForm):

    def __init__(self, wrapper, main=False):

        # the main tree view has an increased row size
        style = ttk.Style()
        style.configure("History.Treeview", rowheight=24)

        size = AppConfig.get("SIZE_HISTORY_FORM")
        assert isinstance(size, tuple)
        bbox = (BBOX_RELOAD, BBOX_CLOSE)
        super().__init__(UI_TITLE_HISTORY, size, None, bbox, main)

        # list box icons
        self._icon_ok = get_ui_image(OK_ICON)
        self._icon_fail = get_ui_image(FAIL_ICON)
        self._icon_unknown = get_ui_image(UNK_ICON)

        # form data
        self._wrapper = wrapper
        self._history = []
        self.set_history(self._wrapper.get_history())

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(self.contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # history list section
        l_history = ttk.Label(area, text=UI_FORM_HISTORYITEMS_SC)
        # build a scrolled frame for the treeview
        sftv_history = ttk.Frame(area)
        tv_history = ttk.Treeview(
            sftv_history,
            columns=("time", "task", "trigger", "duration", "success", "message"),
            show="tree headings",
            style="History.Treeview",
            height=5,
        )
        sb_history = ttk.Scrollbar(
            sftv_history, orient=tk.VERTICAL, command=tv_history.yview
        )
        tv_history.configure(yscrollcommand=sb_history.set)
        tv_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_history.pack(side=tk.RIGHT, fill=tk.Y)

        tv_history.column("#0", anchor=tk.CENTER, width=30, stretch=tk.NO)
        tv_history.heading("#0", anchor=tk.CENTER, text="")

        # NOTE: widths are empirically determined, should be tested on
        # other platform to verify that they are suitable anyway
        tv_history.column("time", anchor=tk.CENTER, width=15)
        tv_history.column("task", anchor=tk.W, width=16)
        tv_history.column("trigger", anchor=tk.W, width=16)
        tv_history.column("duration", anchor=tk.W, width=7)
        tv_history.column("success", anchor=tk.CENTER, width=4)
        tv_history.column("message", anchor=tk.W, width=38)

        tv_history.heading("time", anchor=tk.CENTER, text=UI_FORM_HS_TIME)
        tv_history.heading("task", anchor=tk.W, text=UI_FORM_HS_TASK)
        tv_history.heading("trigger", anchor=tk.W, text=UI_FORM_HS_TRIGGER)
        tv_history.heading("duration", anchor=tk.W, text=UI_FORM_HS_DURATION)
        tv_history.heading("success", anchor=tk.CENTER, text=UI_FORM_HS_SUCCESS)
        tv_history.heading("message", anchor=tk.W, text=UI_FORM_HS_MESSAGE)

        # arrange items in the grid
        l_history.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        sftv_history.grid(row=1, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.rowconfigure(1, weight=1)
        area.columnconfigure(0, weight=1)

        # bind data to widgets
        # NOTE: no data to bind

        # propagate widgets that need to be accessed
        self._tv_history = tv_history

        self._updateform()

    def set_history(self, history) -> None:
        h = list(
            (
                [
                    x["time"][:-7].replace("T", " "),
                    x["task"],
                    x["trigger"],
                    ("%.2fs" % x["duration"].total_seconds()).ljust(7),
                    (
                        SYM_OK
                        if x["success"] == "OK"
                        else SYM_UNKNOWN if x["success"] == "IND" else SYM_FAIL
                    ),
                    x["message"],
                ],
                x["success"],
            )
            for x in history
        )
        h.reverse()
        self._history = h

    def _updateform(self) -> None:
        self._tv_history.delete(*self._tv_history.get_children())
        for entry, outcome in self._history:
            icon = (
                self._icon_ok
                if outcome == "OK"
                else self._icon_unknown if outcome == "IND" else self._icon_fail
            )
            self._tv_history.insert("", values=entry, index=ttk.END, image=icon)

    # reload history data when the `reload` button is clicked
    def reload(self) -> None:
        self.set_history(self._wrapper.get_history())
        self._updateform()
        return super().reload()


# end.
