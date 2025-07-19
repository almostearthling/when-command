# about box

import tkinter as tk
import ttkbootstrap as ttk
from tkhtmlview import HTMLLabel
from PIL import ImageTk

from ..i18n.strings import *
from ..icons import APP_ICON64 as APP_BITMAP
from .ui import *

from ..repocfg import AppConfig
from ..utility import get_whenever_version, get_UI_theme, get_image


# the last paragraphs are to fiull the background in gray
_htmlabout = """
<div style="font-size:13px;"><b>{title}</b></div>
<div style="font-size:9px;">{text}</div>
<div style="font-size:8px;">{copyright}</div>
<div style="font-size:9px;">
{about_app_version}: <b>{appversion}</b><br>
{about_sched_version}: <b>{schedversion}</b>
</div>
"""


class AboutBox(ApplicationForm):

    def __init__(self, main=False):
        version = get_whenever_version()
        appversion = UI_APP_VERSION
        size = AppConfig.get("SIZE_ABOUT_BOX")
        assert isinstance(size, tuple)
        if version:
            text = _htmlabout.format(
                title=UI_APP,
                text=UI_ABOUT_TEXT,
                copyright=UI_APP_COPYRIGHT,
                about_app_version=UI_ABOUT_APP_VERSION,
                appversion=appversion,
                about_sched_version=UI_ABOUT_WHENEVER_VERSION,
                schedversion=version,
            )
        else:
            text = UI_ABOUT_TEXT
        super().__init__(
            UI_ABOUT_TITLE,
            size,
            None,
            (BBOX_CLOSE,),
            main
        )
        self._image = ImageTk.PhotoImage(get_image(APP_BITMAP))

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(self.contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # widgets section
        l_aboutTxt = HTMLLabel(area, html=text)
        l_aboutImg = ttk.Label(area, image=self._image)

        # arrange items in the grid
        l_aboutImg.grid(row=0, column=0, sticky=tk.N, padx=PAD, pady=PAD)
        l_aboutTxt.grid(row=0, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.columnconfigure(1, weight=1)


# display a simple about box
def show_about_box(main=False) -> None:
    box = AboutBox(main)
    box.run()
    del box


# end.
