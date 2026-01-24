# system tray resident application: implements the `start` command

from lib.i18n.strings import *

import pystray
import sys
import threading

from .utility import get_image
from .platform import is_windows, is_linux, is_mac

from .icons import CLOCK_ICON48 as CLOCK_ICON
from .icons import CLOCK_ICON_GRAY48 as CLOCK_ICON_GRAY
from .icons import CLOCK_ICON_BUSY48 as CLOCK_ICON_BUSY

from .repocfg import AppConfig


# icons
_tray_icon = get_image(CLOCK_ICON)
_tray_icon_gray = get_image(CLOCK_ICON_GRAY)
_tray_icon_busy = get_image(CLOCK_ICON_BUSY)


# menu reactions: all events are managed by the main application, and
# therefore they are implemented as messages passed to the root window
def on_configure(root) -> None:
    root.send_event("<<OpenCfgApp>>")


def on_about(root) -> None:
    root.send_event("<<OpenAboutBox>>")


def on_menu_box(root) -> None:
    root.send_event("<<OpenMenuBox>>")


def on_pause_scheduler(root) -> None:
    root.send_event("<<SchedPause>>")


def on_resume_scheduler(root) -> None:
    root.send_event("<<SchedResume>>")


def on_reset_conditions(root) -> None:
    root.send_event("<<SchedResetConditions>>")


def on_history(root) -> None:
    root.send_event("<<OpenHistory>>")


# this sends an EXIT event to the main loop, so that the invisible
# main window is destroyed and all the cleanup is performed
def on_exit(root) -> None:
    root.send_exit()


# set icon color to gray/color: these functions are called by the main
# application to change the icon status when pausing/resuming the scheduler
def set_tray_icon_gray(icon) -> None:
    icon.icon = _tray_icon_gray


def set_tray_icon_normal(icon) -> None:
    icon.icon = _tray_icon


def set_tray_icon_busy(icon) -> None:
    icon.icon = _tray_icon_busy


# entry point for the tray resident application
def main(root) -> None:
    # create the menu: this menu is OK for Windows and for Linux environments
    # that implement the `AppIndicator` protocol; unfortunately this protocol
    # seems to be deprecated by teh folks at Gnome, together with almost
    # everything related to the system tray area, so we fallback to X and tray
    # applications that may not support a right-click context menu
    entries = [
        pystray.MenuItem(
            UI_TRAY_MENU_PAUSESCHEDULER,
            lambda _1, _2: on_pause_scheduler(root),
        ),
        pystray.MenuItem(
            UI_TRAY_MENU_RESUMESCHEDULER,
            lambda _1, _2: on_resume_scheduler(root),
        ),
        pystray.MenuItem(
            UI_TRAY_MENU_RESETCONDITIONS,
            lambda _1, _2: on_reset_conditions(root),
        ),
        pystray.MenuItem(
            UI_TRAY_MENU_HISTORY,
            lambda _1, _2: on_history(root),
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            UI_TRAY_MENU_CONFIGURE,
            lambda _1, _2: on_configure(root),
        ),
        pystray.MenuItem(
            UI_TRAY_MENU_ABOUT,
            lambda _1, _2: on_about(root),
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            UI_TRAY_MENU_EXIT,
            lambda _1, _2: on_exit(root),
        ),
    ]

    # on Linux enable the menu box, since the right-click context menu
    # is unlikely to be available: since this is a default action, which
    # reacts to the left-click on the icon, and its entry is invisible
    # in the menu, a dummy text is used for it
    if is_linux():
        if pystray.Icon.HAS_DEFAULT_ACTION:
            # in this case `AppIndicator` is not running, so it would be
            # worth only to enable the action for icon left click: for
            # example by removing all contents from the `entries` list
            entries = []
            entries.append(
                pystray.MenuItem(
                    "---",
                    lambda _1, _2: on_menu_box(root),
                    default=True,
                    visible=False,
                ),
            )
    # also enable the menu box when debugging - even on Windows
    elif AppConfig.get("DEBUG"):
        if pystray.Icon.HAS_DEFAULT_ACTION:
            entries.append(
                pystray.MenuItem(
                    "---",
                    lambda _1, _2: on_menu_box(root),
                    default=True,
                    visible=False,
                ),
            )

    menu = pystray.Menu(*entries)

    # create the icon
    tray = pystray.Icon(
        UI_APP,
        _tray_icon,
        UI_APP_LABEL,
        menu=menu,
    )

    # the root also must know the tray icon entity in order to stop its
    # main loop when the application is requested to exit
    root.set_trayicon(tray)

    # show the tray icon
    if is_linux():
        threading.Thread(target=tray.run).start()
    else:
        tray.run_detached()


# end.
