# system tray resident application: implements the `start` command

from lib.i18n.strings import *

import pystray

from lib.utility import get_image, get_configfile, get_logfile

# from lib.icons import APP_ICON64 as APP_ICON
from lib.icons import CLOCK_ICON48 as CLOCK_ICON
from lib.icons import CLOCK_ICON_GRAY48 as CLOCK_ICON_GRAY

from lib.forms.about import show_about_box
from lib.forms.cfgform import form_Config
from lib.forms.history import form_History

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
def on_configure(icon, item):
    form = form_Config()
    form.run()
    del form

def on_about(icon, item):
    show_about_box()

def on_pause_scheduler(icon, item):
    # if successful, also gray out the icon
    if wrapper.whenever_pause():
        icon.icon = tray_icon_gray
        # unfortunately, menu items are immutable
        # icon.menu.items[0].enabled = False
        # icon.menu.items[1].enabled = True

def on_resume_scheduler(icon, item):
    # if successful, also color up the icon
    if wrapper.whenever_resume():
        icon.icon = tray_icon
        # unfortunately, menu items are immutable
        # icon.menu.items[0].enabled = True
        # icon.menu.items[1].enabled = False

def on_reset_conditions(icon, item):
    wrapper.whenever_reset_conditions()

def on_history(icon, item):
    form = form_History(wrapper.get_history())
    form.run()
    del form

def on_exit(icon, item):
    wrapper.whenever_exit()
    icon.stop()


# entry point for the tray resident application
def main():
    # create the menu
    menu = pystray.Menu(
        pystray.MenuItem(
            UI_TRAY_MENU_PAUSESCHEDULER,
            on_pause_scheduler,
        ),
        pystray.MenuItem(
            UI_TRAY_MENU_RESUMESCHEDULER,
            on_resume_scheduler,
            # unfortunately it cannot be enabled dynamically
            # enabled=False,
        ),
        pystray.MenuItem(
            UI_TRAY_MENU_RESETCONDITIONS,
            on_reset_conditions,
        ),
        pystray.MenuItem(
            UI_TRAY_MENU_HISTORY,
            on_history,
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            UI_TRAY_MENU_CONFIGURE,
            on_configure,
        ),
        pystray.MenuItem(
            UI_TRAY_MENU_ABOUT,
            on_about,
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            UI_TRAY_MENU_EXIT,
            on_exit,
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
    wrapper.start()

    # show the tray icon
    tray.run()


# end.
