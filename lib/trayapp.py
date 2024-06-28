# system tray resident application: implements the `start` command

from lib.i18n.strings import *

import pystray

from lib.utility import get_image, get_configfile, get_logfile

# from lib.icons import APP_ICON64 as APP_ICON
from lib.icons import CLOCK_ICON48 as CLOCK_ICON
from lib.icons import CLOCK_ICON_GRAY48 as CLOCK_ICON_GRAY

from lib.runner.process import Wrapper

from lib.repocfg import AppConfig


# log level as per CLI configuration
log_level = AppConfig.get('LOGLEVEL')

# file resources
log_file = get_logfile()
config_file = get_configfile()
whenever_path = AppConfig.get('WHENEVER')

# icons
tray_icon = get_image(CLOCK_ICON)
tray_icon_gray = get_image(CLOCK_ICON_GRAY)


# the global scheduler wrapper
wrapper = Wrapper(config_file, whenever_path, log_file, log_level)


# menu reactions
def on_configure(root):
    root.send_event('<<OpenCfgApp>>')

def on_about(root):
    root.send_event('<<OpenAboutBox>>')

def on_pause_scheduler(icon):
    # if successful, also gray out the icon
    if wrapper.whenever_pause():
        icon.icon = tray_icon_gray
        # unfortunately, menu items are immutable
        # icon.menu.items[0].enabled = False
        # icon.menu.items[1].enabled = True

def on_resume_scheduler(icon):
    # if successful, also color up the icon
    if wrapper.whenever_resume():
        icon.icon = tray_icon
        # unfortunately, menu items are immutable
        # icon.menu.items[0].enabled = True
        # icon.menu.items[1].enabled = False

def on_reset_conditions():
    wrapper.whenever_reset_conditions()

def on_history(root):
    root.send_event('<<OpenHistory>>')

# this also sends an EXIT event to the main loop, so that the invisible
# main window is destroyed
def on_exit(icon, root):
    wrapper.whenever_exit()
    root.send_exit()
    icon.stop()


# entry point for the tray resident application
def main(root):
    # create the menu
    menu = pystray.Menu(
        pystray.MenuItem(
            UI_TRAY_MENU_PAUSESCHEDULER,
            lambda icon, _: on_pause_scheduler(icon),
        ),
        pystray.MenuItem(
            UI_TRAY_MENU_RESUMESCHEDULER,
            lambda icon, _: on_resume_scheduler(icon),
            # unfortunately it cannot be enabled dynamically
            # enabled=False,
        ),
        pystray.MenuItem(
            UI_TRAY_MENU_RESETCONDITIONS,
            lambda _1, _2: on_reset_conditions(),
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
            lambda icon, _: on_exit(icon, root),
        ),
    )

    # create the icon
    tray = pystray.Icon(
        UI_APP,
        tray_icon,
        UI_APP_LABEL,
        menu=menu,
    )

    # start a _secondary_ thread to run **whenever** and read its stdout
    if not wrapper.start():
        raise Exception("could not launch the scheduler")

    # root is the main app and uses the wrapper to retrieve history
    # therefore it must be known to the main window that in turn
    # shows the history box
    root.set_wrapper(wrapper)

    # show the tray icon
    tray.run_detached()


# end.
