#!/usr/bin/env python
# application launcher and command line interpreter

import sys
import os
import os.path
import argparse
import gc

import ttkbootstrap as ttk
from PIL import ImageTk


BASEDIR = os.path.dirname(os.path.dirname(sys.argv[0]))
if not BASEDIR:
    BASEDIR = "."
sys.path.append(BASEDIR)

from lib.i18n.strings import *
from lib.icons import APP_ICON32 as APP_ICON
from lib.utility import (
    retrieve_whenever_options,
    get_default_configdir,
    get_default_whenever,
    get_scriptsdir,
    get_appdata,
    get_logfile,
    get_configfile,
    is_whenever_running,
    get_image,
    get_UI_theme,
    get_tkroot,
    get_rich_console,
    exit_error,
    write_warning,
    init_logger,
    get_logger,
)
from lib.repocfg import AppConfig

from lib.runner.process import Wrapper


# main root window, to be withdrawn
_root = None


# this is used to enable exception handling too
DEBUG = AppConfig.get("DEBUG")


# the following class is used to create an invisible window that actually
# implements the tkinter main loop, and that reads virtual events to display
# the application forms: being the main window it also sets the ttk style
# and reacts to events that cause actions to be performed
class App(object):

    # an invisible root window is created, the other ones are all toplevels:
    # the icon is created **after** creating the root window, because a root
    # is needed to be active for this purpose
    def __init__(self):
        # the following lines solve the wrong icon problem on Windows
        if sys.platform.startswith("win"):
            import ctypes

            myappid = "when.python.application"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self._window = get_tkroot()
        self._window.withdraw()
        self._icon = ImageTk.PhotoImage(get_image(APP_ICON))
        self._paused = False
        self._window.iconphoto(True, self._icon)    # type: ignore

        # load forms and application related functions *after* initialization,
        # and take property of member functions: this is done here so that all
        # configuration that might depend on information that is acquired
        # after startup (such as the `whenever` executable) is already known
        # before initializations of forms and application objects
        from lib.trayapp import (
            set_tray_icon_gray,
            set_tray_icon_busy,
            set_tray_icon_normal,
        )
        from lib.forms.about import show_about_box
        from lib.forms.menubox import form_MenuBox
        from lib.forms.cfgform import form_Config
        from lib.forms.history import form_History

        self.set_tray_icon_gray = set_tray_icon_gray
        self.set_tray_icon_busy = set_tray_icon_busy
        self.set_tray_icon_normal = set_tray_icon_normal
        self.show_about_box = show_about_box
        self.form_MenuBox = form_MenuBox
        self.form_Config = form_Config
        self.form_History = form_History

        style = ttk.Style()
        style.theme_use(get_UI_theme())
        self._window.bind("<<OpenHistory>>", self.open_history)
        self._window.bind("<<OpenCfgApp>>", self.open_cfgapp)
        self._window.bind("<<OpenAboutBox>>", self.open_aboutbox)
        self._window.bind("<<OpenMenuBox>>", self.open_menubox)
        self._window.bind("<<SchedPause>>", self.sched_pause)
        self._window.bind("<<SchedResume>>", self.sched_resume)
        self._window.bind("<<SchedSetBusy>>", self.sched_icon_busy)
        self._window.bind("<<SchedSetNotBusy>>", self.sched_icon_not_busy)
        self._window.bind("<<SchedSetPaused>>", self.sched_icon_paused)
        self._window.bind("<<SchedSetNotPaused>>", self.sched_icon_not_paused)
        self._window.bind("<<SchedResetConditions>>", self.sched_reset_conditions)
        self._window.bind("<<SchedReloadConfig>>", self.sched_reload_configuration)
        self._window.bind("<<ExitApplication>>", self.exit_app)
        self._wrapper = None
        self._trayicon = None
        self._busy = False

    # the main loop is mandatory to react to events
    def run(self) -> None:
        if self._window is not None:
            self._window.mainloop()

    # the scheduler wrapper is needed as it provides access to task history
    def set_wrapper(self, wrapper) -> None:
        self._wrapper = wrapper

    # the tray icon if any
    def set_trayicon(self, icon) -> None:
        self._trayicon = icon

    # send an event to the main loop asynchronously
    def send_event(self, event: str) -> None:
        if self._window:
            self._window.update()
            self._window.event_generate(event)

    # shortcut to send an EXIT event
    def send_exit(self) -> None:
        if self._window:
            self._window.update()
            self._window.event_generate("<<ExitApplication>>")

    # destroy the window, stop whenever, and cleanup internals
    def destroy(self) -> None:
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
    def open_history(self, _) -> None:
        if self._window and self._wrapper:
            form = self.form_History(self._wrapper)
            form.run()
            del form
            gc.collect()

    def sched_pause(self, _) -> None:
        if not self._paused and self._window and self._wrapper:
            self._wrapper.whenever_pause()

    def sched_resume(self, _) -> None:
        if self._paused and self._window and self._wrapper:
            self._wrapper.whenever_resume()

    def sched_reset_conditions(self, _) -> None:
        if self._window and self._wrapper:
            self._wrapper.whenever_reset_conditions()

    def sched_reload_configuration(self, _) -> None:
        if self._window and self._wrapper:
            self._wrapper.whenever_reload_configuration()

    def sched_icon_busy(self, _) -> None:
        if self._icon:
            # check current status to avoid useless icon swaps
            if not self._busy:
                self._busy = True
                if not self._paused:
                    self.set_tray_icon_busy(self._trayicon)

    def sched_icon_not_busy(self, _) -> None:
        if self._icon:
            # check current status to avoid useless icon swaps
            if self._busy:
                self._busy = False
                if self._paused:
                    self.set_tray_icon_gray(self._trayicon)
                else:
                    self.set_tray_icon_normal(self._trayicon)

    def sched_icon_paused(self, _) -> None:
        if self._icon:
            # check current status to avoid useless icon swaps
            if not self._paused:
                self._paused = True
                self.set_tray_icon_gray(self._trayicon)

    def sched_icon_not_paused(self, _) -> None:
        if self._icon:
            # check current status to avoid useless icon swaps
            if self._paused:
                self._paused = False
                if self._busy:
                    self.set_tray_icon_busy(self._trayicon)
                else:
                    self.set_tray_icon_normal(self._trayicon)

    def open_cfgapp(self, _) -> None:
        if self._window:
            form = self.form_Config(self)
            form.run()
            del form
            gc.collect()

    def open_menubox(self, _) -> None:
        if self._window and self._wrapper:
            form = self.form_MenuBox(self)
            form.run()
            del form
            gc.collect()

    def open_aboutbox(self, _) -> None:
        if self._window:
            self.show_about_box(False)
            gc.collect()

    def exit_app(self, _) -> None:
        self.destroy()


# set up the main window which is the event receiver: since the root window
# is only created by instantiating App, this is needed in every command that
# displays a window, because all other forms are just non-root toplevels;
# NOTE: every windowed subprogram *must* receive a reference to the root
# window and take care of sending a `send_exit()` event when finishing
def setup_windows() -> None:
    global _root
    _root = App()


# prepare expected environment, such as configuration directory
def prepare_environment() -> None:
    # create the application data directory if it does not exist
    try:
        _ = get_appdata()
    except Exception as e:
        exit_error(e)
    try:
        _ = get_scriptsdir()
    except Exception as e:
        exit_error(e)


# subcommand main functions


# version: display the application version and exit
def main_version(_) -> None:
    # print plain text: could be programatically used to determine version
    print("%s: v%s" % (UI_APP, UI_APP_VERSION))


# config: enter the configuration utility and exit (no scheduler launched)
def main_config(args) -> None:
    # set some global configuration values according to CLI options
    AppConfig.delete("APPDATA")
    AppConfig.set("APPDATA", args.dir_appdata)
    retrieve_whenever_options()
    prepare_environment()
    if DEBUG:
        configfile = get_configfile()
        if not os.path.exists(configfile):
            try:
                with open(configfile, "w") as f:
                    f.write("# Created by: %s v%s" % (UI_APP, UI_APP_VERSION))
            except Exception as e:
                exit_error(CLI_ERR_CONFIG_UNACCESSIBLE)
        setup_windows()
        from lib.cfgapp import main

        main(_root)
    else:
        try:
            configfile = get_configfile()
            if not os.path.exists(configfile):
                try:
                    with open(configfile, "w") as f:
                        f.write("# Created by: %s v%s" % (UI_APP, UI_APP_VERSION))
                except Exception as e:
                    exit_error(CLI_ERR_CONFIG_UNACCESSIBLE)
            setup_windows()
            from lib.cfgapp import main

            main(_root)
        except Exception as e:
            exit_error(CLI_ERR_UNEXPECTED_EXCEPTION % e)


# start: start the scheduler in the background and display the tray icon
def main_start(args) -> None:
    # set some global configuration values according to CLI options
    AppConfig.delete("APPDATA")
    AppConfig.set("APPDATA", args.dir_appdata)
    AppConfig.delete("LOGLEVEL")
    AppConfig.set("LOGLEVEL", args.log_level.upper())
    AppConfig.delete("WHENEVER")
    AppConfig.set("WHENEVER", args.whenever)
    retrieve_whenever_options()
    prepare_environment()
    if is_whenever_running():
        exit_error(CLI_ERR_ALREADY_RUNNING)
    # prepare application so that the logger can be initialized
    setup_windows()
    # get configuration options
    log_level = AppConfig.get("LOGLEVEL")
    log_file = get_logfile()
    config_file = get_configfile()
    init_logger(log_file, log_level, _root)
    log = get_logger().context().use(emitter="FRONTEND")
    log.use(
        level=log.LEVEL_INFO,
        when=log.WHEN_START,
        action="initializing",
        status=log.STATUS_MSG,
    ).log("starting resident %s, version %s" % (UI_APP, UI_APP_VERSION))
    if DEBUG:
        # setup the scheduler and associate it to the application
        whenever: str = AppConfig.get("WHENEVER")   # type: ignore
        if (
            whenever is None
            or not os.path.exists(whenever)
            or not os.access(whenever, os.X_OK)
        ):
            log.use(level=log.LEVEL_ERROR, status=log.STATUS_ERR).log(
                "error: `whenever` binary not found"
            )
            exit_error(CLI_ERR_WHENEVER_NOT_FOUND)
        wrapper = Wrapper(config_file, whenever, _root)
        # start the scheduler in a separate thread
        if not wrapper.start():
            log.use(level=log.LEVEL_ERROR, status=log.STATUS_ERR).log(
                "error: `whenever` not started"
            )
            raise Exception(CLI_ERR_STARTING_SCHEDULER)
        # check that everything is fine after start
        if not wrapper.running():
            log.use(level=log.LEVEL_ERROR, status=log.STATUS_ERR).log(
                "error: `whenever` not running"
            )
            raise Exception(CLI_ERR_STARTING_SCHEDULER)
        # run the tray icon application main loop
        from lib.trayapp import main

        main(_root)
        if _root is not None:
            _root.run()
    else:
        try:
            # setup the scheduler and associate it to the application
            whenever: str = AppConfig.get("WHENEVER")   # type: ignore
            if (
                whenever is None
                or not os.path.exists(whenever)
                or not os.access(whenever, os.X_OK)
            ):
                log.use(level=log.LEVEL_ERROR, status=log.STATUS_ERR).log(
                    "error: `whenever` binary not found"
                )
                exit_error(CLI_ERR_WHENEVER_NOT_FOUND)
            wrapper = Wrapper(config_file, whenever, _root)
            # start the scheduler in a separate thread
            if not wrapper.start():
                log.use(level=log.LEVEL_ERROR, status=log.STATUS_ERR).log(
                    "error: `whenever` not started"
                )
                raise Exception(CLI_ERR_STARTING_SCHEDULER)
            # check that everything is fine after start
            if not wrapper.running():
                log.use(level=log.LEVEL_ERROR, status=log.STATUS_ERR).log(
                    "error: `whenever` not running"
                )
                raise Exception(CLI_ERR_STARTING_SCHEDULER)
            # run the tray icon application main loop
            from lib.trayapp import main

            main(_root)
            if _root is not None:
                _root.run()
        except Exception as e:
            log.use(level=log.LEVEL_ERROR, status=log.STATUS_ERR).log(
                "unexpected exception: %s" % e
            )
            exit_error(CLI_ERR_UNEXPECTED_EXCEPTION % e)


# toolbox: various utilities that can help build a proper setup
def main_toolbox(args) -> None:
    AppConfig.delete("APPDATA")
    AppConfig.set("APPDATA", args.dir_appdata)
    prepare_environment()
    console = get_rich_console()
    verbose = not args.quiet
    # download the latest stable release of whenever and install it
    if args.install_whenever:
        if is_whenever_running():
            exit_error(CLI_ERR_CANNOT_INSTALL_ON_RUNNING)
        if args.desktop and verbose:
            write_warning(CLI_ERR_UNSUPPORTED_SWITCH % "--desktop")
        if args.autostart and verbose:
            write_warning(CLI_ERR_UNSUPPORTED_SWITCH % "--autostart")
        if args.create_icons and verbose:
            write_warning(CLI_ERR_UNSUPPORTED_SWITCH % "--create-icons")
        if args.fix_config and verbose:
            write_warning(CLI_ERR_UNSUPPORTED_SWITCH % "--fix-config")
        from lib.toolbox.install_whenever import install

        install(verbose=verbose)
        if verbose:
            console.print(CLI_MSG_INSTALLATION_FINISHED, highlight=False)

    # create shortcuts/desktop files in the appropriate requested locations
    elif args.create_icons:
        # this will never happen because the switch is handled before this one
        if args.install_whenever and verbose:
            write_warning(CLI_ERR_UNSUPPORTED_SWITCH % "--install-whenever")
        if args.fix_config and verbose:
            write_warning(CLI_ERR_UNSUPPORTED_SWITCH % "--fix-config")
        from lib.toolbox.create_shortcuts import create_shortcuts

        my_path = os.path.normpath(os.path.realpath(__file__))
        create_shortcuts(my_path, args.desktop, args.autostart, verbose)
        if verbose:
            console.print(CLI_MSG_OPERATION_FINISHED, highlight=False)

    # fix configuration
    elif args.fix_config:
        if args.desktop and verbose:
            write_warning(CLI_ERR_UNSUPPORTED_SWITCH % "--desktop")
        if args.autostart and verbose:
            write_warning(CLI_ERR_UNSUPPORTED_SWITCH % "--autostart")
        if args.create_icons and verbose:
            write_warning(CLI_ERR_UNSUPPORTED_SWITCH % "--create-icons")
        if args.install_whenever and verbose:
            write_warning(CLI_ERR_UNSUPPORTED_SWITCH % "--install-whenever")
        retrieve_whenever_options()
        from lib.toolbox.fix_config import fix_config_file

        fix_config_file(get_configfile(), verbose=verbose)
        if verbose:
            console.print(CLI_MSG_OPERATION_FINISHED, highlight=False)

    # ...


# main program: perform CLI parsing and run the appropriate subcommand
def main() -> None:
    global _root

    default_appdata = get_default_configdir()
    default_whenever = get_default_whenever()

    # for now set the paths to their default values
    AppConfig.set("APPDATA", default_appdata)
    AppConfig.set("WHENEVER", default_whenever)

    # main parser
    parser = argparse.ArgumentParser(
        description=CLI_APP_DESCRIPTION,
        epilog=CLI_APP_HELP_EPILOG,
    )
    subparsers = parser.add_subparsers(help=CLI_ARG_HELP_COMMAND)

    # parser for the `start` subcommand
    parser_start = subparsers.add_parser("start", help=CLI_ARG_HELP_CMD_START)
    parser_start.add_argument(
        "-D",
        "--dir-appdata",
        help=CLI_ARG_HELP_DIR_APPDATA,
        type=str,
        default=default_appdata,
    )
    parser_start.add_argument(
        "-W",
        "--whenever",
        help=CLI_ARG_HELP_WHENEVER,
        type=str,
        default=default_whenever,
    )
    parser_start.add_argument(
        "-L",
        "--log-level",
        help=CLI_ARG_HELP_LOGLEVEL,
        type=str,
        choices=["trace", "debug", "info", "warn", "error"],
        default="info",
    )
    parser_start.set_defaults(func=main_start)

    # parser for the `config` subcommand
    parser_config = subparsers.add_parser("config", help=CLI_ARG_HELP_CMD_CONFIG)
    parser_config.add_argument(
        "-D",
        "--dir-appdata",
        help=CLI_ARG_HELP_DIR_APPDATA,
        type=str,
        default=default_appdata,
    )
    parser_config.add_argument(
        "-W",
        "--whenever",
        help=CLI_ARG_HELP_WHENEVER,
        type=str,
        default=default_whenever,
    )
    parser_config.set_defaults(func=main_config)

    # parser for the `tool` subcommand
    parser_toolbox = subparsers.add_parser("tool", help=CLI_ARG_HELP_CMD_TOOLBOX)
    parser_toolbox.add_argument(
        "-D",
        "--dir-appdata",
        help=CLI_ARG_HELP_DIR_APPDATA,
        type=str,
        default=default_appdata,
    )
    parser_toolbox.add_argument(
        "--install-whenever",
        help=CLI_ARG_HELP_INSTALL_WHENEVER,
        action="store_true",
    )
    parser_toolbox.add_argument(
        "--create-icons",
        help=CLI_ARG_HELP_CREATE_SHORTCUTS,
        action="store_true",
    )
    parser_toolbox.add_argument(
        "--desktop",
        help=CLI_ARG_HELP_DESKTOP,
        action="store_true",
    )
    parser_toolbox.add_argument(
        "--autostart",
        help=CLI_ARG_HELP_AUTOSTART,
        action="store_true",
    )
    parser_toolbox.add_argument(
        "--fix-config",
        help=CLI_ARG_HELP_FIXCONFIG,
        action="store_true",
    )
    parser_toolbox.add_argument(
        "--quiet",
        help=CLI_ARG_HELP_QUIET,
        action="store_true",
    )
    parser_toolbox.set_defaults(func=main_toolbox)

    # parser for the `version` subcommand
    parser_version = subparsers.add_parser("version", help=CLI_ARG_HELP_CMD_VERSION)
    parser_version.set_defaults(func=main_version)

    # all program functionality is split in the `main_[...]` functions above
    args = parser.parse_args()
    args.func(args)


# standard startup
if __name__ == "__main__":
    main()


# end
