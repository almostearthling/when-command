# about form

from ..i18n.strings import *
from ..repocfg import AppConfig

import tkinter as tk
import ttkbootstrap as ttk

from PIL import ImageTk

from ..utility import get_whenever_version, get_UI_theme, get_image
from ..icons import APP_ICON32 as APP_ICON
from ..icons import APP_ICON64 as APP_BITMAP

from .ui import *

class AboutBox(ApplicationForm):

    def __init__(self, main=False):
        version = get_whenever_version()
        if version:
            text = "%s\n\n%s %s" % (UI_ABOUT_TEXT, UI_ABOUT_WHENEVER_VERSION, version)
        else:
            text = UI_ABOUT_TEXT
        super().__init__(UI_ABOUT_TITLE, AppConfig.get('SIZE_ABOUT_BOX'), APP_ICON, (BBOX_CLOSE,), main)
        
        # build the UI
        area = ttk.Frame(self.contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        self._image = ImageTk.PhotoImage((get_image(APP_BITMAP)))

        l_aboutTxt = ttk.Label(area, text=text)
        l_aboutImg = ttk.Label(area, image=self._image)

        l_aboutImg.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        l_aboutTxt.grid(row=0, column=1, sticky=tk.W, padx=PAD, pady=PAD)

        area.columnconfigure(1, weight=1)


# display a simple about box
def show_about_box(main=False):
    box = AboutBox(main)
    box.run()

# end.
