# history box

from ..i18n.strings import *
from ..repocfg import AppConfig

import tkinter as tk
import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from ttkbootstrap import tableview
from ttkbootstrap.icons import Emoji

from .ui import *


# form class: this form is fixed and will not be derived
class form_History(ApplicationForm):

    def __init__(self, wrapper, main=False):

        size = AppConfig.get("SIZE_HISTORY_FORM")
        assert isinstance(size, tuple)
        bbox = (BBOX_RELOAD, BBOX_CLOSE)
        super().__init__(UI_TITLE_HISTORY, size, None, bbox, main)

        # list box icons
        self._icon_ok = Emoji.get("HEAVY CHECK MARK")
        self._icon_fail = Emoji.get("CROSS MARK")
        self._icon_unknown = Emoji.get("BLACK QUESTION MARK ORNAMENT")

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

        cols = [
            {
                "text": "",
                "width": 30,
                "anchor": ttkc.CENTER,
            },
            {
                "text": UI_FORM_HS_TIME,
                "width": 130,
                "anchor": ttkc.CENTER,
            },
            {
                "text": UI_FORM_HS_TASK,
                "width": 240,
                "anchor": ttkc.W,
            },
            {
                "text": UI_FORM_HS_TRIGGER,
                "width": 240,
                "anchor": ttkc.W,
            },
            {
                "text": UI_FORM_HS_DURATION,
                "width": 70,
                "anchor": ttkc.CENTER,
            },
            # { "text": UI_FORM_HS_MESSAGE, "width": 20, "anchor": "w", },
        ]
        messsage_width = size[0] - (10 * PAD) - (sum(x["width"] for x in cols))
        cols.append(
            {
                "text": UI_FORM_HS_MESSAGE,
                "width": messsage_width,
                "anchor": ttkc.W,
            }
        )

        tab_history = tableview.Tableview(
            area,
            coldata=cols,
            paginated=False,
            yscrollbar=True,
            # disable_right_click=True,
        )

        # arrange items in the grid
        l_history.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        tab_history.grid(row=1, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.rowconfigure(1, weight=1)
        area.columnconfigure(0, weight=1)

        # bind data to widgets
        # NOTE: no data to bind

        # propagate widgets that need to be accessed
        self._tv_history = tab_history

        self._updateform()

    def set_history(self, history) -> None:
        h = list(
            (
                [
                    x["time"][:-7].replace("T", " "),
                    x["task"],
                    x["trigger"],
                    ("%.2fs" % x["duration"].total_seconds()).ljust(7),
                    x["message"],
                ],
                x["success"],
            )
            for x in history
        )
        h.reverse()
        self._history = h

    def _updateform(self) -> None:
        self._tv_history.delete_rows()
        for entry, outcome in self._history:
            icon = (
                self._icon_ok
                if outcome == "OK"
                else self._icon_unknown if outcome == "IND" else self._icon_fail
            )
            entry.insert(0, icon)
            self._tv_history.insert_row("end", values=entry)

    # reload history data when the `reload` button is clicked
    def reload(self) -> None:
        self.set_history(self._wrapper.get_history())
        self._updateform()
        return super().reload()


# end.
