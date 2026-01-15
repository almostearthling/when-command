# about box
#
# this menu box mimics the menu, for use on systems that do not support
# a proper tray icon menu: activated by a left click on the icon

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.icons import Icon
from ttkbootstrap_icons_mat import MatIcon as Icons

from PIL import ImageTk

from ..i18n.strings import *
from ..icons import APP_ICON64 as APP_BITMAP
# from ..icons import (
#     PAUSE_SQUARED_B_ICON32,
#     SETTINGS_B_ICON32,
#     CIRCLED_PLAY_B_ICON32,
#     RESET_B_ICON32,
#     INDEX_B_ICON32,
#     PAUSE_SQUARED_B_ICON32,
#     QUESTION_MARK_B_ICON32,
#     EXIT_B_ICON32,
# )
from .ui import *   # type: ignore

from ..repocfg import AppConfig
from ..utility import get_image, get_icon


# colors for buttons
BLACK = '#000000'
DKGRAY = '#444444'
MDGRAY = '#777777'
LTGRAY = '#BBBBBB'
WHITE = '#FFFFFF'
RED = '#FF0000'
DKRED = '#990000'
GREEN = '#00FF00'
DKGREEN = '#007500'
BLUE = '#0000FF'
DKBLUE = '#000099'
YELLOW = '#FFFF00'
DKYELLOW = '#997700'
ORANGE = '#FF5500'
CYAN = '#00FFFF'
DKCYAN = '#007799'
FUCHSIA = '#FF00FF'
MAGENTA = '#990099'
PURPLE = '#5500BB'


# default UI values
WIDGET_PADDING_PIXELS = 5


# menu box buttons
class _btn_MenuEntry(ttk.Button):
    def __init__(self, master, text, icon_bytes, command, enabled):
        self._image = get_icon(icon_bytes)
        if command is None:
            command = ""
        super().__init__(
            master,
            text=text,
            image=self._image,
            compound=tk.LEFT,
            command=command,
            style="menubutton.TButton",
        )
        self.enable(enabled)

    def enable(self, enabled=True):
        if enabled:
            active = ["!disabled"]
        else:
            active = ["disabled"]
        self.state(active)


class BtnAbout(_btn_MenuEntry):
    def __init__(self, master, text=BTN_ABOUT_D, command=None, enabled=True):
        icon = Icons("information", color=FUCHSIA).image
        super().__init__(
            master,
            text=text,
            icon_bytes=icon,
            command=command,
            enabled=enabled,
        )


class BtnConfig(_btn_MenuEntry):
    def __init__(self, master, text=BTN_CONFIG_D, command=None, enabled=True):
        icon = Icons("cog", color=MDGRAY).image
        super().__init__(
            master,
            text=text,
            icon_bytes=icon,
            command=command,
            enabled=enabled,
        )


class BtnPause(_btn_MenuEntry):
    def __init__(self, master, text=BTN_PAUSE, command=None, enabled=True):
        icon = Icons("pause", color=LTGRAY).image
        super().__init__(
            master,
            text=text,
            icon_bytes=icon,
            command=command,
            enabled=enabled,
        )


class BtnResume(_btn_MenuEntry):
    def __init__(self, master, text=BTN_RESUME, command=None, enabled=True):
        icon = Icons("play", color=GREEN).image
        super().__init__(
            master,
            text=text,
            icon_bytes=icon,
            command=command,
            enabled=enabled,
        )


class BtnReset(_btn_MenuEntry):
    def __init__(self, master, text=BTN_RESETCONDS, command=None, enabled=True):
        icon = Icons("stop-circle", color=FUCHSIA).image
        super().__init__(
            master,
            text=text,
            icon_bytes=icon,
            command=command,
            enabled=enabled,
        )


class BtnHistory(_btn_MenuEntry):
    def __init__(self, master, text=BTN_HISTORY_D, command=None, enabled=True):
        icon = Icons("stop-circle", color=FUCHSIA).image
        super().__init__(
            master,
            text=text,
            icon_bytes=icon,
            command=command,
            enabled=enabled,
        )


class BtnLeave(_btn_MenuEntry):
    def __init__(self, master, text=BTN_EXIT, command=None, enabled=True):
        icon = Icons("stop-circle", color=FUCHSIA).image
        super().__init__(
            master,
            text=text,
            icon_bytes=icon,
            command=command,
            enabled=enabled,
        )


# this window mimics the menu, for use on systems that do not support
# a proper tray icon menu: activated by a left click on the icon
class form_MenuBox(ApplicationForm):

    def __init__(self, app=None, main=False):

        style = ttk.Style()
        style.configure(style="menubutton.TButton", anchor=tk.W)
        size = AppConfig.get("SIZE_MENU_BOX")
        assert isinstance(size, tuple)

        super().__init__(
            UI_TITLE_MENU, size, None, (BBOX_CANCEL,), main
        )
        self._image = ImageTk.PhotoImage(get_image(APP_BITMAP))
        self._app = app

        # build the UI: build widgets, arrange them in the box, bind data
        # client area
        area = ttk.Frame(self.contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        btn_Pause = BtnPause(area, command=self.on_pause_scheduler)
        btn_Resume = BtnResume(area, command=self.on_resume_scheduler)
        btn_Reset = BtnReset(area, command=self.on_reset_conditions)
        btn_History = BtnHistory(area, command=self.on_history)
        sep1 = ttk.Separator(area)

        btn_Config = BtnConfig(area, command=self.on_configure)
        btn_About = BtnAbout(area, command=self.on_about)
        sep2 = ttk.Separator(area)

        btn_Exit = BtnLeave(area, command=self.on_exit)

        btn_Pause.grid(row=1, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        btn_Resume.grid(row=2, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        btn_Reset.grid(row=3, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        btn_History.grid(row=4, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        sep1.grid(row=10, column=1, sticky=tk.EW, padx=PAD, pady=PAD)

        btn_Config.grid(row=11, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        btn_About.grid(row=12, column=1, sticky=tk.EW, padx=PAD, pady=PAD)
        sep2.grid(row=20, column=1, sticky=tk.EW, padx=PAD, pady=PAD)

        btn_Exit.grid(row=21, column=1, sticky=tk.EW, padx=PAD, pady=PAD)

        # expand appropriate sections
        area.columnconfigure(1, weight=1)

    # menu reactions: all events are managed by the main application, and
    # therefore they are implemented as messages passed to the root window
    def on_configure(self):
        if self._app:
            self._app.send_event("<<OpenCfgApp>>")

    def on_about(self):
        if self._app:
            self._app.send_event("<<OpenAboutBox>>")

    def on_menu_box(self):
        if self._app:
            self._app.send_event("<<OpenMenuBox>>")

    def on_pause_scheduler(self):
        if self._app:
            self._app.send_event("<<SchedPause>>")

    def on_resume_scheduler(self):
        if self._app:
            self._app.send_event("<<SchedResume>>")

    def on_reset_conditions(self):
        if self._app:
            self._app.send_event("<<SchedResetConditions>>")

    def on_history(self):
        if self._app:
            self._app.send_event("<<OpenHistory>>")

    # this sends an EXIT event to the main loop, so that the invisible
    # main window is destroyed and all the cleanup is performed
    def on_exit(self):
        if self._app:
            self._app.send_exit()


# end.
