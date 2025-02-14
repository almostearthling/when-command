#!/usr/bin/env python
# application launcher and command line interpreter

import sys
import os
import os.path
import argparse
import shutil

import tkinter as tk
import ttkbootstrap as ttk
from PIL import ImageTk


BASEDIR = os.path.dirname(os.path.dirname(sys.argv[0]))
if not BASEDIR:
    BASEDIR = '.'
sys.path.append(BASEDIR)

from lib.i18n.strings import *
from lib.icons import APP_ICON32 as APP_ICON
from lib.utility import (
    get_default_configdir,
    get_scriptsdir,
    get_logfile,
    get_configfile,
    is_whenever_running,
    get_image,
    get_UI_theme,
    get_tkroot,
    )
from lib.repocfg import AppConfig

from lib.runner.process import Wrapper
from lib.trayapp import set_tray_icon_gray, set_tray_icon_normal

from lib.forms.about import show_about_box
from lib.forms.menubox import form_MenuBox
from lib.forms.cfgform import form_Config
from lib.forms.history import form_History


# main root window, to be withdrawn
_root = None


# this is used to enable exception handling too
DEBUG = AppConfig.get('DEBUG')



# the following class is used to create an invisible window that actually
# implements the tkinter main loop, and that reads virtual events to display
# the application forms: being the main window it also sets the ttk style
# and reacts to events that cause actions to be performed
class App(object):

    # an invisible root window is created, the other ones are all toplevels:
    # the icon is created **after** creating the root window, because a root
    # is needed to be active for this purpose
    def __init__(self):
        self._window = get_tkroot()
        self._window.withdraw()
        self._icon = ImageTk.PhotoImage(get_image(APP_ICON))
        self._window.iconphoto(True, self._icon)
        style = ttk.Style()
        style.theme_use(get_UI_theme())
        self._window.bind('<<OpenHistory>>', self.open_history)
        self._window.bind('<<OpenCfgApp>>', self.open_cfgapp)
        self._window.bind('<<OpenAboutBox>>', self.open_aboutbox)
        self._window.bind('<<OpenMenuBox>>', self.open_menubox)
        self._window.bind('<<SchedPause>>', self.sched_pause)
        self._window.bind('<<SchedResume>>', self.sched_resume)
        self._window.bind('<<SchedResetConditions>>', self.sched_reset_conditions)
        self._window.bind('<<SchedReloadConfig>>', self.sched_reload_configuration)
        self._window.bind('<<ExitApplication>>', self.exit_app)
        self._wrapper = None
        self._trayicon = None


    # the main loop is mandatory to react to events
    def run(self):
        self._window.mainloop()

    # the scheduler wrapper is needed as it provides access to task history
    def set_wrapper(self, wrapper):
        self._wrapper = wrapper

    # the tray icon if any
    def set_trayicon(self, icon):
        self._trayicon = icon

    # send an event to the main loop asynchronously
    def send_event(self, event: str):
        if self._window:
            self._window.update()
            self._window.event_generate(event)

    # shortcut to send an EXIT event
    def send_exit(self):
        if self._window:
            self._window.update()
            self._window.event_generate('<<ExitApplication>>')

    # destroy the window, stop whenever, and cleanup internals
    def destroy(self):
        if self._wrapper:
            self._wrapper.whenever_exit()
            self._wrapper = None
        if self._window:
            self._window.destroy()
            del self._window
            self._window = None
        if self._trayicon:
            if sys.platform == "linux":
                # something's wrong wit pystray in this case
                os._exit(os.EX_OK)
            else:
                self._trayicon.stop()
                self._trayicon = None

    # event reactions: these are called by the systray app that runs in a
    # separate, detached thread so that it does not slow down the main loop
    def open_history(self, _):
        if self._window and self._wrapper:
            form = form_History(self._wrapper.get_history())
            form.run()
            del form

    def sched_pause(self, _):
        if self._window and self._wrapper:
            if self._wrapper.whenever_pause():
                if self._icon:
                    set_tray_icon_gray(self._trayicon)

    def sched_resume(self, _):
        if self._window and self._wrapper:
            if self._wrapper.whenever_resume():
                if self._icon:
                    set_tray_icon_normal(self._trayicon)

    def sched_reset_conditions(self, _):
        if self._window and self._wrapper:
            self._wrapper.whenever_reset_conditions()

    def sched_reload_configuration(self, _):
        if self._window and self._wrapper:
            self._wrapper.whenever_reload_configuration()

    def open_cfgapp(self, _):
        if self._window:
            form = form_Config(self)
            form.run()
            del form

    def open_menubox(self, _):
        if self._window and self._wrapper:
            form = form_MenuBox()
            form.set_root(self)
            form.run()
            del form

    def open_aboutbox(self, _):
        if self._window:
            show_about_box()

    def exit_app(self, _):
        self.destroy()



# set up the main window which is the event receiver: since the root window
# is only created by instantiating App, this is needed in every command that
# displays a window, because all other forms are just non-root toplevels;
# NOTE: every windowed subprogram *must* receive a reference to the root
# window and take care of sending a `send_exit()` event when finishing
def setup_windows():
    global _root
    _root = App()


# utility to bail out with a consistent error message
def exiterror(s, code=2):
    sys.stderr.write("%s error: %s\n" % (UI_APP, s))
    sys.exit(code)



# main program: perform CLI parsing and run the appropriate subcommand
def main():
    global _root

    default_appdata = get_default_configdir()
    default_whenever = shutil.which('whenever')

    parser = argparse.ArgumentParser(
        description=CLI_APP_DESCRIPTION,
        epilog=CLI_APP_HELP_EPILOG,
        )
    parser.add_argument(
        "command",
        help=CLI_ARG_HELP_COMMAND,
        choices=['start', 'config', 'version'],
        )
    parser.add_argument(
        "-D", "--dir-appdata",
        help=CLI_ARG_HELP_DIR_APPDATA,
        type=str,
        default=default_appdata,
    )
    parser.add_argument(
        "-W", "--whenever",
        help=CLI_ARG_HELP_WHENEVER,
        type=str,
        default=default_whenever,
    )
    parser.add_argument(
        "-L", "--log-level",
        help=CLI_ARG_HELP_LOGLEVEL,
        type=str,
        choices=['trace', 'debug', 'info', 'warn', 'error'],
        default='info',
    )

    args = parser.parse_args()

    # set some global configuration values according to CLI options
    AppConfig.set('APPDATA', args.dir_appdata)
    AppConfig.set('LOGLEVEL', args.log_level)
    AppConfig.set('WHENEVER', args.whenever)

    # create the application data directory if it does not exist
    datadir = AppConfig.get('APPDATA')
    if not os.path.isdir(datadir):
        try:
            os.makedirs(datadir)
        except Exception as e:
            exiterror(CLI_ERR_DATADIR_UNACCESSIBLE)

    # create the defaullt scritps directory now that the data directory exists
    scriptsdir = get_scriptsdir()
    if not os.path.isdir(scriptsdir):
        exiterror(CLI_ERR_SCRIPTSDIR_UNACCESSIBLE)

    # run the selected action
    command = args.command

    # display the version and exit
    if command == 'version':
        print("%s: v%s" % (UI_APP, UI_APP_VERSION))

    # open the configuration utility and exit after its use
    elif command == 'config':
        if DEBUG:
            configfile = get_configfile()
            if not os.path.exists(configfile):
                try:
                    with open(configfile, 'w') as f:
                        f.write("# Created by: %s v%s" % (UI_APP, UI_APP_VERSION))
                except Exception as e:
                    exiterror(CLI_ERR_CONFIG_UNACCESSIBLE)
            setup_windows()
            from lib.cfgapp import main
            main(_root)
        else:
            try:
                configfile = get_configfile()
                if not os.path.exists(configfile):
                    try:
                        with open(configfile, 'w') as f:
                            f.write("# Created by: %s v%s" % (UI_APP, UI_APP_VERSION))
                    except Exception as e:
                        exiterror(CLI_ERR_CONFIG_UNACCESSIBLE)
                setup_windows()
                from lib.cfgapp import main
                main(_root)
            except Exception as e:
                exiterror("unexpected exception '%s'" % e)

    # start the resident application and display an icon on the tray area
    elif command == 'start':
        # exit if the scheduler is already running
        if is_whenever_running():
            exiterror(CLI_ERR_ALREADY_RUNNING)
        # get configuration options
        log_level = AppConfig.get('LOGLEVEL')
        log_file = get_logfile()
        config_file = get_configfile()
        if DEBUG:
            # setup the scheduler and associate it to the application
            whenever = AppConfig.get('WHENEVER')
            if whenever is None or not os.path.exists(whenever) or not os.access(whenever, os.X_OK):
                exiterror(CLI_ERR_WHENEVER_NOT_FOUND)
            wrapper = Wrapper(config_file, whenever, log_file, log_level)
            setup_windows()

            # start the scheduler in a separate thread
            if not wrapper.start():
                raise Exception("an error occurred starting the scheduler")
            _root.set_wrapper(wrapper)

            # run the tray icon application main loop
            from lib.trayapp import main
            main(_root)
            _root.run()
        else:
            try:
                # setup the scheduler and associate it to the application
                whenever = AppConfig.get('WHENEVER')
                if whenever is None or not os.path.exists(whenever) or not os.access(whenever, os.X_OK):
                    exiterror(CLI_ERR_WHENEVER_NOT_FOUND)
                wrapper = Wrapper(config_file, whenever, log_file, log_level)
                setup_windows()

                # start the scheduler in a separate thread
                if not wrapper.start():
                    raise Exception("an error occurred starting the scheduler")
                _root.set_wrapper(wrapper)

                # run the tray icon application main loop
                from lib.trayapp import main
                main(_root)
                _root.run()
            except Exception as e:
                exiterror("unexpected exception '%s'" % e)

    else:
        exiterror("unknown command: %s" % command)


# standard startup
if __name__ == '__main__':
    main()


# end