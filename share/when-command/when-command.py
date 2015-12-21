#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# When
#
# Copyright (c) 2015 Francesco Garosi
# Released under the BSD License (see LICENSE file)
#
# Small startup applet that runs tasks when particular conditions are met.


import os
import sys
import time
import signal
import subprocess
import threading
import configparser
import pickle
import json
import logging
import logging.config
import logging.handlers
import argparse
import shutil
import re
import locale

import traceback

from gi.repository import GLib, Gio
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import AppIndicator3 as AppIndicator
from gi.repository import Notify
from gi.repository import Pango

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from concurrent.futures import ThreadPoolExecutor

from collections import OrderedDict, deque, namedtuple

try:
    import pyinotify
    FILE_NOTIFY_ENABLED = True
except ImportError:
    FILE_NOTIFY_ENABLED = False


# this innocent hack is for compatibility between different layouts
if 'when_command' not in sys.modules:
    sys.modules['when_command'] = sys.modules[__name__]


#############################################################################
# constants

# base constants
APPLET_NAME = 'when-command'
APPLET_FULLNAME = 'When Gnome Scheduler'
APPLET_SHORTNAME = 'When'
APPLET_COPYRIGHT = '(c) 2015 Francesco Garosi'
APPLET_URL = 'http://almostearthling.github.io/when-command/'
APPLET_ID = 'it.jks.WhenCommand'
APPLET_BUS_NAME = '%s.BusService' % APPLET_ID
APPLET_BUS_PATH = '/' + APPLET_BUS_NAME.replace('.', '/')
APPLET_LONGDESC = "When is a configurable user task scheduler for Gnome."

# NOTE: the following lines *must both* be edited at each release increment
# * the first holds the version ID that build utilities can extract
# * the second one includes a message that is used both as a commit message
#   and as a tag-associated message (in `git tag -m`)
APPLET_VERSION = '0.9.4~beta.2'
APPLET_TAGDESC = 'Provide minimalistic mode'

# logging constants
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_MAX_BACKUPS = 4

# action constants
ACTION_OK = 0
ACTION_CANCEL = -1
ACTION_DELETE = 9

# DBus return value comparison operators
DBUS_CHECK_COMPARE_IS = 'is'
DBUS_CHECK_COMPARE_CONTAINS = 'contains'
DBUS_CHECK_COMPARE_MATCHES = 'matches'
DBUS_CHECK_COMPARE_GREATER = 'gt'
DBUS_CHECK_COMPARE_LESS = 'lt'

# item types for CLI arguments
ITEM_TYPE_TASKS = 'tasks'
ITEM_TYPE_CONDITIONS = 'conditions'
ITEM_TYPE_SIGNAL_HANDLERS = 'sighandlers'
ITEM_TYPE_UNKNOWN = 'unknown'

ITEM_SPEC_SEPARATOR = ':'

# force to True to allow adding only self-contained item files
ITEM_ADD_SELF_CONTAINED = False

# item operation error codes
ITEM_OPERATION_OK = 0
ITEM_OPERATION_ERR_TYPE = 1
ITEM_OPERATION_ERR_NOTFOUND = 2
ITEM_OPERATION_ERR_CONFLICT = 3
ITEM_OPERATION_ERR_UNKNOWN = -1

# validation constants
VALIDATE_TASK_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$')
VALIDATE_CONDITION_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$')
VALIDATE_SIGNAL_HANDLER_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$')
VALIDATE_ENVVAR_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')

# see http://dbus.freedesktop.org/doc/dbus-specification.html#message-protocol-names
VALIDATE_DBUS_NAME_RE = re.compile(r'^[-a-zA-Z_][-a-zA-Z0-9_]*(\.[-a-zA-Z_][-a-zA-Z0-9_]*)+\.?$')
VALIDATE_DBUS_PATH_RE = re.compile(r'^\/[a-zA-Z0-9_]+(\/[a-zA-Z0-9_]+)+$')
VALIDATE_DBUS_INTERFACE_RE = re.compile(r'^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)+\.?$')
VALIDATE_DBUS_SIGNAL_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
VALIDATE_DBUS_SUBPARAM_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

# user interface constants
UI_INTERVALS_MINUTES = [1, 2, 3, 5, 15, 30, 60]
UI_INTERVALS_HOURS = [1, 2, 3, 4, 6, 8, 12, 24]

# headers for history file
HISTORY_HEADERS = ['ITEM_ID', 'STARTUP_TIME', 'RUN_TIME', 'TASK_NAME',
                   'TRIGGER_COND', 'SUCCESS', 'EXIT_CODE', 'FAILURE_REASON']
HISTORY_ERR_EMPTY = -1
HISTORY_ERR_IOERROR = -2
HISTORY_ENTRY_SUCCESS = 'success'
HISTORY_ENTRY_FAILURE = 'failure'
HISTORY_SEPARATOR = ';'

# folders
USER_FOLDER = os.path.expanduser('~')
USER_DATA_FOLDER = os.path.join(USER_FOLDER, '.local', 'share', APPLET_NAME)
USER_LAUNCHER_FOLDER = os.path.join(USER_FOLDER, '.local', 'share', 'applications')
USER_AUTOSTART_FOLDER = os.path.join(USER_FOLDER, '.config', 'autostart')
USER_CONFIG_FOLDER = os.path.join(USER_FOLDER, '.config', APPLET_NAME)
USER_LOG_FOLDER = os.path.join(USER_DATA_FOLDER, 'log')
USER_LOG_FILE = os.path.join(USER_LOG_FOLDER, '%s.log' % APPLET_NAME)
USER_CONFIG_FILE = os.path.join(USER_CONFIG_FOLDER, '%s.conf' % APPLET_NAME)
USER_PAUSE_FILE = os.path.join(USER_CONFIG_FOLDER, '%s.pause' % APPLET_NAME)

GRAPHIC_ENVIRONMENT = 'DISPLAY' in os.environ.keys()

# event strings (applet, system, session)
EVENT_APPLET_STARTUP = 'startup'
EVENT_APPLET_SHUTDOWN = 'shutdown'
EVENT_SYSTEM_SUSPEND = 'system_suspend'
EVENT_SYSTEM_RESUME = 'system_resume'
EVENT_SYSTEM_DEVICE_ATTACH = 'device_attach'
EVENT_SYSTEM_DEVICE_DETACH = 'device_detach'
EVENT_SYSTEM_NETWORK_JOIN = 'network_join'
EVENT_SYSTEM_NETWORK_LEAVE = 'network_leave'
EVENT_SESSION_SCREENSAVER = 'screensaver'
EVENT_SESSION_SCREENSAVER_EXIT = 'screensaver_exit'
EVENT_SESSION_LOCK = 'session_lock'
EVENT_SESSION_UNLOCK = 'session_unlock'
EVENT_COMMAND_LINE = 'command_line'
EVENT_SYSTEM_BATTERY_CHARGE = 'battery_charge'
EVENT_SYSTEM_BATTERY_DISCHARGING = 'battery_discharging'
EVENT_SYSTEM_BATTERY_LOW = 'battery_low'

EVENT_COMMAND_LINE_PREAMBLE = 'command_line'
EVENT_DBUS_SIGNAL_PREAMBLE = 'dbus_signal'

# file names
FILE_CONFIG_LIST_TASKS = 'task.list'
FILE_CONFIG_LIST_CONDITIONS = 'condition.list'
FILE_CONFIG_LIST_SIGNAL_HANDLERS = 'signalhandler.list'

# network manager constants
NM_STATE_UNKNOWN = 0
NM_STATE_ASLEEP = 10
NM_STATE_DISCONNECTED = 20
NM_STATE_DISCONNECTING = 30
NM_STATE_CONNECTING = 40
NM_STATE_CONNECTED_LOCAL = 50
NM_STATE_CONNECTED_SITE = 60
NM_STATE_CONNECTED_GLOBAL = 70

# file notification constants: from inotify.h here are the constants
# IN_ACCESS		   0x00000001	/* File was accessed */
# IN_MODIFY		   0x00000002	/* File was modified */
# IN_ATTRIB		   0x00000004	/* Metadata changed */
# IN_CLOSE_WRITE   0x00000008	/* Writtable file was closed */
# IN_CLOSE_NOWRITE 0x00000010	/* Unwrittable file closed */
# IN_OPEN		   0x00000020	/* File was opened */
# IN_MOVED_FROM	   0x00000040	/* File was moved from X */
# IN_MOVED_TO	   0x00000080	/* File was moved to Y */
# IN_CREATE		   0x00000100	/* Subfile was created */
# IN_DELETE		   0x00000200	/* Subfile was deleted */
# IN_DELETE_SELF   0x00000400	/* Self was deleted */
#
# Need everything *but* access, open, and close_nowrite thus:
# 2 | 4 | 8 | 64 | 128 | 256 | 512 | 1024 = 1998
FN_IN_MODIFY_EVENTS = 1998

# environment variables to be set when spawning processes
ENVVAR_NAME_TASK = 'WHEN_COMMAND_TASK'
ENVVAR_NAME_COND = 'WHEN_COMMAND_CONDITION'
ENVVAR_UNKNOWN_COND = '(unknown)'

#############################################################################
# global variables referenced through the code (this should be redundant)
applet = None
applet_lock = threading.Lock()
applet_enabled_events = None
main_dbus_loop = None
current_system_event = None
current_deferred_events = None
current_changed_path = None
current_deferred_changed_paths = None

applet_log_handler = logging.NullHandler()
applet_log_formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
applet_log_handler.setFormatter(applet_log_formatter)
applet_log = logging.getLogger(APPLET_NAME)
applet_log.addHandler(applet_log_handler)

config = None
periodic = None
tasks = None
conditions = None
history = None
deferred_events = None
deferred_watch_paths = None
signal_handlers = None
watch_path_manager = None
watch_path_notifier = None


# verify that the user folders are present, otherwise create them
def verify_user_folders():
    if not os.path.exists(USER_DATA_FOLDER):
        os.makedirs(USER_DATA_FOLDER, exist_ok=True)
    if not os.path.exists(USER_LOG_FOLDER):
        os.makedirs(USER_LOG_FOLDER, exist_ok=True)
    if not os.path.exists(USER_CONFIG_FOLDER):
        os.makedirs(USER_CONFIG_FOLDER, exist_ok=True)
    if not os.path.exists(USER_LAUNCHER_FOLDER):
        os.makedirs(USER_LAUNCHER_FOLDER, exist_ok=True)
    if not os.path.exists(USER_AUTOSTART_FOLDER):
        os.makedirs(USER_AUTOSTART_FOLDER, exist_ok=True)


#############################################################################
# Support these installation schemes:
#
# * default: LSB standard (/usr/bin, /usr/share/when-command/*)
# * /opt based (/opt/when-command, /opt/when-command/share/when-command/*)
# * LSB local (/usr/local/bin, /usr/local/share/when-command/*)
# * $HOME generic (~/.local/bin, ~/.local/when-command/share/*)
# * own folder ($FOLDER, $FOLDER/share/when-command/*)
#
# where first element is the invoked command directory, second one is the
# prefix of the applet data folder (where dialogs, icons and other resources
# have to be installed); icons have their own subtree in the data folder;
# locales are either in standard system folders or a subtree of data folder.
APP_BASE_FOLDER = '/usr'
APP_BIN_FOLDER = os.path.join(APP_BASE_FOLDER, 'bin')
APP_DATA_FOLDER = os.path.join(APP_BASE_FOLDER, 'share', APPLET_NAME)
APP_ICON_FOLDER = os.path.join(APP_DATA_FOLDER, 'icons')
APP_LOCALE_FOLDER = os.path.join(APP_BASE_FOLDER, 'share', 'locale')

INVOKED_CMD = sys.argv[0]
INVOKED_DIR = os.path.dirname(INVOKED_CMD)
if INVOKED_DIR == os.path.join('/opt', APPLET_NAME):
    APP_BIN_FOLDER = INVOKED_DIR
    APP_BASE_FOLDER = INVOKED_DIR
    APP_DATA_FOLDER = os.path.join(APP_BASE_FOLDER, 'share')
    APP_ICON_FOLDER = os.path.join(APP_DATA_FOLDER, 'icons')
    APP_LOCALE_FOLDER = os.path.join(APP_DATA_FOLDER, 'locale')
elif INVOKED_DIR == '/usr/local/bin':
    APP_BIN_FOLDER = INVOKED_DIR
    APP_BASE_FOLDER = '/usr/local'
    APP_DATA_FOLDER = os.path.join(APP_BASE_FOLDER, 'share', APPLET_NAME)
    APP_ICON_FOLDER = os.path.join(APP_DATA_FOLDER, 'icons')
    APP_LOCALE_FOLDER = os.path.join(APP_BASE_FOLDER, 'share', 'locale')
elif INVOKED_DIR == os.path.join(USER_FOLDER, '.local', 'bin'):
    APP_BIN_FOLDER = INVOKED_DIR
    APP_BASE_FOLDER = USER_DATA_FOLDER
    APP_DATA_FOLDER = USER_DATA_FOLDER
    APP_ICON_FOLDER = os.path.join(APP_DATA_FOLDER, 'icons')
    APP_LOCALE_FOLDER = os.path.join(APP_DATA_FOLDER, 'locale')
elif not INVOKED_DIR.startswith('/usr'):
    APP_BIN_FOLDER = INVOKED_DIR
    APP_BASE_FOLDER = INVOKED_DIR
    APP_DATA_FOLDER = os.path.join(APP_BASE_FOLDER, 'share', APPLET_NAME)
    APP_ICON_FOLDER = os.path.join(APP_DATA_FOLDER, 'icons')
    APP_LOCALE_FOLDER = os.path.join(APP_BASE_FOLDER, 'share', 'locale')

# update Python path
sys.path.insert(0, APP_DATA_FOLDER)


# dialog boxes
def load_applet_dialog(name):
    base = os.path.dirname(sys.argv[0])
    with open(os.path.join(APP_DATA_FOLDER, '%s.glade' % name)) as f:
        dialog_xml = f.read()
    return dialog_xml


# setup i18n for both applet text and dialogs
locale.setlocale(locale.LC_ALL, locale.getlocale())
locale.bindtextdomain(APPLET_NAME, APP_LOCALE_FOLDER)
locale.textdomain(APPLET_NAME)
_ = locale.gettext


# format an exception for logging purposes
def _x(e):
    t, v, tb = sys.exc_info()
    if t is None:
        return ''
    return '%s: %s' % (t.__name__, v)


# dialog boxes are loaded after initialization
ui_add_task = None
ui_add_condition = None
ui_settings = None
ui_task_history = None
ui_about = None
ui_add_signal = None


# define resource strings using the _() function for i18n
class Resources(object):
    pass

resources = Resources()
resources.DLG_CONFIRM_DELETE_TASK = _("Are you sure you want to delete task %s?")
resources.DLG_CONFIRM_DELETE_CONDITION = _("Are you sure you want to delete condition %s?")
resources.DLG_CONFIRM_DELETE_SIGHANDLER = _("Are you sure you want to delete signal handler %s?")
resources.DLG_CANNOT_DELETE_TASK = _("Task %s could not be deleted.")
resources.DLG_CANNOT_DELETE_CONDITION = _("Condition %s could not be deleted.")
resources.DLG_CANNOT_DELETE_SIGHANDLER = _("Signal handler %s could not be deleted.")
resources.DLG_CANNOT_FIND_TASK = _("Task %s could not be found.")
resources.DLG_CANNOT_FIND_CONDITION = _("Condition %s could not be found.")
resources.DLG_CANNOT_FIND_SIGHANDLER = _("Signal handler %s could not be found.")
resources.DLG_CANNOT_REGISTER_SIGHANDLER = _("Signal handler %s could not be registered.")
resources.DLG_PATH_NOT_SPECIFIED = _("Must specify watched path: condition not created.")
resources.DLG_WRONG_EXIT_STATUS = _("Invalid value for exit status specified.\nPlease consider reviewing it.")
resources.DLG_WRONG_PARAM_INDEX = _("Invalid value for signal parameter index specified.\nCannot add parameter test.")
resources.DLG_NOT_IMPLEMENTED_FEATURE = _("This feature has not been implemented yet.")
resources.DLG_NOT_ENABLED_FEATURE = _("This feature is not enabled.\nPlease check documentation for possible reasons.")
resources.DLG_ABOUT_VERSION_STRING = _("Version: %s")
resources.DLG_ITEM_DISABLED = _("[disabled]")
resources.DLG_TITLE_CHOOSE_FILE = _("Choose File")
resources.DLG_TITLE_CHOOSE_DIR = _("Choose Directory")
resources.DLG_TITLE_CHOOSE_FILEDIR = _("Choose File or Directory")

resources.NOTIFY_TASK_FAILED = _("Task failed: %s")

resources.MENU_EDIT_TASKS = _("Edit Tasks...")
resources.MENU_EDIT_CONDITIONS = _("Edit Conditions...")
resources.MENU_SETTINGS = _("Settings...")
resources.MENU_TASK_HISTORY = _("Task History...")
resources.MENU_PAUSE = _("Pause")
resources.MENU_ABOUT = _("About...")
resources.MENU_QUIT = _("Quit")

resources.CBENTRY_CONDITION_DBUS_EVENTS = [_("User Defined Event"), '70']

resources.LISTCOL_ENVVARS_NAME = _("Variable")
resources.LISTCOL_ENVVARS_VALUE = _("Value")
resources.LISTCOL_TASKS_NAME = _("Task Name")
resources.LISTCOL_HISTORY_TIMESTAMP = _("Time / Duration")
resources.LISTCOL_HISTORY_TASK = _("Task Name")
resources.LISTCOL_HISTORY_TRIGGER = _("Trigger")
resources.LISTCOL_HISTORY_EXITCODE = _("Exit Code")
resources.LISTCOL_HISTORY_SUCCESS = _("Result")
resources.LISTCOL_HISTORY_REASON = _("Reason")
resources.LISTCOL_HISTORY_ROWID = _("Row ID")
resources.LISTCOL_SIGNAL_PARAMETER = _("Param")
resources.LISTCOL_SIGNAL_PARAMETER_SUB = _("Sub")
resources.LISTCOL_SIGNAL_NEGATE = _("Negate")
resources.LISTCOL_SIGNAL_OPERATOR = _("Compare")
resources.LISTCOL_SIGNAL_VALUE = _("Value")
# resources.LISTCOL_SIGNAL_ROWID = _("Row ID")

resources.OERR_SHUTDOWN_BEGIN = _("an existing instance will be %s")
resources.OERR_SHUTDOWN_SHUTDOWN = _("shut down")
resources.OERR_SHUTDOWN_KILL = _("killed")
resources.OERR_SHUTDOWN_FINISH = _("instance shutdown finished")
resources.OERR_SHOW_BOX = _("showing %s box of currently running instance")
resources.OERR_RUN_CONDITION = _("attempting to run condition %s")
resources.OERR_RUN_CONDITION_FAIL = _("condition %s could not be run")
resources.OERR_EXPORT_HISTORY = _("attempting to export task history to %s")
resources.OERR_EXPORT_HISTORY_EMPTY = _("empty")
resources.OERR_EXPORT_HISTORY_IOERROR = _("ioerror")
resources.OERR_EXPORT_HISTORY_UNKNOWN = _("unknown")
resources.OERR_EXPORT_HISTORY_FAIL = _("could not save task history (%s)")
resources.OERR_EXPORT_HISTORY_FINISH = _("exported %s elements to specified file")
resources.OERR_CLEAR_DATA = _("removing all items")
resources.OERR_CLEAR_DATA_CONDFAIL = _("could not remove condition list file")
resources.OERR_CLEAR_DATA_TASKFAIL = _("could not remove task list file")
resources.OERR_CLEAR_DATA_SIGFAIL = _("could not remove signal handler list file")
resources.OERR_EXPORT_DATA_BEGIN = _("exporting items:")
resources.OERR_EXPORT_DATA_TASKS = _("    %s tasks")
resources.OERR_EXPORT_DATA_CONDITIONS = _("    %s conditions")
resources.OERR_EXPORT_DATA_SIGHANDLERS = _("    %s signal handlers")
resources.OERR_EXPORT_DATA_FINISH = _("items exported to file %s")
resources.OERR_IMPORT_DATA = _("importing items from file %s")
resources.OERR_IMPORT_DATA_FAIL = _("could not import from dump file")
resources.OERR_IMPORT_DATA_BEGIN = _("restoring items:")
resources.OERR_IMPORT_DATA_TASKS = _("    %s tasks")
resources.OERR_IMPORT_DATA_CONDITIONS = _("    %s conditions")
resources.OERR_IMPORT_DATA_SIGHANDLERS = _("    %s signal handlers")
resources.OERR_IMPORT_DATA_FINISH = _("items successfully imported")
resources.OERR_ITEMOPS_DEL_FINISH = _("item %s successfully deleted")
resources.OERR_ITEMOPS_DEL_FAIL = _("cannot delete item: %s")
resources.OERR_ITEMOPS_ADD_NOREAD = _("cannot add items from provided file")
resources.OERR_ITEMOPS_ADD_FAIL = _("cannot add items: malformed item file")
resources.OERR_NO_INSTANCE = _("no instance could be found")
resources.OERR_FOUND_INSTANCE = _("found a running instance")
resources.OERR_EXPORT = _("tasks and conditions successfully exported")
resources.OERR_RESET = _("configuration has been reset")
resources.OERR_CLEAR = _("tasks and conditions deleted")
resources.OERR_INSTALL = _("icons and data installed")

resources.OERR_ERR_REQUIRE_DESKTOP = _("this program requires a graphical session")
resources.OERR_ERR_ALREADY_RUNNING = _("another instance is present: leaving")
resources.OERR_ERR_REQUIRE_INSTANCE = _("could not find a running instance, please start it first")
resources.OERR_ERR_MINIMALISTIC = _("feature not available in minimalistic mode")
resources.OERR_ERR_NO_INSTANCE = _("could not find a running instance")
resources.OERR_ERR_DBUS_DISABLED = _("dbus signals disabled by configuration")
resources.OERR_ERR_DBUS_SERVICE = _("error in communication with running applet")
resources.OERR_ERR_EXPORT_GENERIC = _("an error occurred while trying to export items")
resources.OERR_ERR_RESET_RUNNING = _("cannot reset configuration, please close instance first")
resources.OERR_ERR_RESET_GENERIC = _("an error occurred while trying to reset configuration")
resources.OERR_ERR_CLEAR_RUNNING = _("cannot clear items, please close instance first")
resources.OERR_ERR_CLEAR_GENERIC = _("an error occurred while trying to delete items")
resources.OERR_ERR_IMPORT_RUNNING = _("cannot import items, please close instance first")
resources.OERR_ERR_IMPORT_GENERIC = _("an error occurred while trying to import items")
resources.OERR_ERR_INSTALL_RUNNING = _("cannot install, please close instance first")
resources.OERR_ERR_INSTALL_GENERIC = _("an error occurred while trying to install icons")
resources.OERR_ERR_ITEMOPS_OK = _("no error found")
resources.OERR_ERR_ITEMOPS_TYPE = _("unknown item type")
resources.OERR_ERR_ITEMOPS_CONFLICT = _("item name conflict")
resources.OERR_ERR_ITEMOPS_NOTFOUND = _("item not found")
resources.OERR_ERR_ITEMOPS_DBUS = _("error communicating with applet")
resources.OERR_ERR_ITEMOPS_GENERIC = _("unknown error or dependency conflict")

resources.COMMAND_LINE_HELP_VERSION = _("show applet version")
resources.COMMAND_LINE_HELP_SHOW_SETTINGS = _("show settings dialog box for the running instance [R]")
resources.COMMAND_LINE_HELP_SHOW_HISTORY = _("show history dialog box for the running instance [R]")
resources.COMMAND_LINE_HELP_SHOW_TASKS = _("show tasks dialog box for the running instance [R]")
resources.COMMAND_LINE_HELP_SHOW_CONDITIONS = _("show conditions box for the running instance [R]")
resources.COMMAND_LINE_HELP_SHOW_DBUS_SIGNALS = _("show dbus signals box for the running instance [R]")
resources.COMMAND_LINE_HELP_RESET_CONFIG = _("reset general configuration to default [S]")
resources.COMMAND_LINE_HELP_SHOW_ICON = _("show applet icon [N]")
resources.COMMAND_LINE_HELP_CLEAR = _("clear all tasks and conditions [S]")
resources.COMMAND_LINE_HELP_INSTALL = _("install application icons and autostart [S]")
resources.COMMAND_LINE_HELP_QUERY = _("query for a running instance")
resources.COMMAND_LINE_HELP_EXPORT_HISTORY = _("export task history to a text file [R]")
resources.COMMAND_LINE_HELP_RUN_CONDITION = _("run a command-line bound condition")
resources.COMMAND_LINE_HELP_DEFER_CONDITION = _("enqueue a command-line bound condition")
resources.COMMAND_LINE_HELP_SHUTDOWN = _("run shutdown tasks and close an existing istance [R]")
resources.COMMAND_LINE_HELP_KILL = _("kill an existing istance [R]")
resources.COMMAND_LINE_HELP_EXPORT = _("save tasks and conditions to a portable format")
resources.COMMAND_LINE_HELP_IMPORT = _("import tasks and conditions from saved file [S]")
resources.COMMAND_LINE_HELP_ITEM_LIST = _("list items of the given type to console")
resources.COMMAND_LINE_HELP_ITEM_ADD = _("add items from specified file or standard input")
resources.COMMAND_LINE_HELP_ITEM_DELETE = _("delete the item specified as [type:]NAME")
resources.COMMAND_LINE_HELP_VERBOSE = _("show verbose output for some options")
resources.COMMAND_LINE_SHOWVERSION = _("%s: %s, version %s")
resources.COMMAND_LINE_PREAMBLE = _("""\
%s: %s - %s /
When is a configurable user task scheduler for Gnome.
The command line interface can be used to interact with running instances of
When or to perform maintenance tasks. Use the --verbose option to read output
from the command, as most operations will show no output by default.
""") % (APPLET_NAME, APPLET_FULLNAME, APPLET_COPYRIGHT)
resources.COMMAND_LINE_EPILOG = _("""\
Note: options marked with [R] require an instance running in the background,
with [S] require that no instance is running and with [N] have only effect
after restart. Go to %s for more information.
""") % APPLET_URL

# constants for desktop entry and autostart entry
APP_ENTRY_DESKTOP = """\
#!/usr/bin/env xdg-open
[Desktop Entry]
Version={applet_version}
Name={applet_shortname}
Comment={applet_fullname}
Icon={icon_path}/alarmclock-128.png
Terminal=false
Type=Application
Categories=Utility;Application;System;
Exec=/usr/bin/env python3 {applet_exec}
"""

APP_ENTRY_AUTOSTART = """\
[Desktop Entry]
Name={applet_shortname}
GenericName={applet_fullname}
Comment={applet_fullname}
Icon={icon_path}/alarmclock-128.png
Terminal=false
Type=Application
Categories=Utility;Application;System;
Exec=/usr/bin/env python3 {applet_exec}
StartupNotify=false
X-GNOME-Autostart-enabled={autostart_enable}
"""


# utility to create a desktop file if not installed system-wide
def create_desktop_file(overwrite=False):
    filename = '%s.desktop' % APPLET_NAME
    if APP_BASE_FOLDER == '/usr':
        if os.path.exists(os.path.join(APP_BASE_FOLDER, 'share',
                                       'applications', filename)):
            return
    pathname = os.path.join(USER_DATA_FOLDER, filename)
    if not os.path.exists(pathname) or overwrite:
        applet_log.info("MAIN: creating desktop entries")
        content = APP_ENTRY_DESKTOP.format(
            applet_version=APPLET_VERSION,
            applet_shortname=APPLET_SHORTNAME,
            applet_fullname=APPLET_FULLNAME,
            icon_path=APP_ICON_FOLDER,
            applet_exec=sys.argv[0],
        )
        with open(pathname, 'w') as f:
            f.write(content)
        os.chmod(pathname, 0o755)
        if os.path.isdir(USER_LAUNCHER_FOLDER):
            try:
                os.symlink(
                    pathname, os.path.join(USER_LAUNCHER_FOLDER, filename))
            except Exception:
                applet_log.error("MAIN: could not create the launcher")


# utility to create the autostart file
def create_autostart_file(overwrite=True):
    filename = '%s-startup.desktop' % APPLET_NAME
    pathname = os.path.join(USER_DATA_FOLDER, filename)
    enable = 'true' if config.get('General', 'autostart') else 'false'
    if not os.path.exists(pathname) or overwrite:
        applet_log.info("MAIN: creating autostart entries")
        content = APP_ENTRY_AUTOSTART.format(
            applet_version=APPLET_VERSION,
            applet_shortname=APPLET_SHORTNAME,
            applet_fullname=APPLET_FULLNAME,
            icon_path=APP_ICON_FOLDER,
            autostart_enable=enable,
            applet_exec=sys.argv[0],
        )
        with open(pathname, 'w') as f:
            f.write(content)
        os.chmod(pathname, 0o755)
        linkname = os.path.join(USER_AUTOSTART_FOLDER, filename)
        if os.path.isdir(USER_AUTOSTART_FOLDER) and not os.path.exists(linkname):
            try:
                os.symlink(pathname, linkname)
            except Exception:
                applet_log.error("MAIN: could not create the autostart launcher")


# manage pause file
def create_pause_file():
    if not os.path.exists(USER_PAUSE_FILE):
        applet_log.info("MAIN: creating pause file")
        with open(USER_PAUSE_FILE, 'w') as f:
            f.write('paused')
        return True
    else:
        return False


def check_pause_file():
    applet_log.info("MAIN: checking if pause file exists")
    if os.path.exists(USER_PAUSE_FILE):
        applet_log.debug("MAIN: pause file exists")
        return True
    else:
        applet_log.debug("MAIN: pause file does not exist")
        return False


def unlink_pause_file():
    if os.path.exists(USER_PAUSE_FILE):
        applet_log.info("MAIN: removing pause file")
        os.unlink(USER_PAUSE_FILE)
        return True
    else:
        return False


def config_loglevel(level=None):
    if level is None:
        try:
            level = config.get('General', 'log level').lower()
        except Exception:
            level = logging.WARNING
    if type(level) == str:
        try:
            level = {
                'debug': logging.DEBUG,
                'info': logging.INFO,
                'warning': logging.WARNING,
                'error': logging.ERROR,
                'critical': logging.CRITICAL,
            }[level.lower()]
        except KeyError as e:
            level = logging.DEBUG
    if type(level) == int:
        applet_log.setLevel(level)
    else:
        applet_log.setLevel(logging.WARNING)


def config_loghandler(max_size=None, max_backups=None):
    global applet_log_handler
    if max_size is None:
        max_size = config.get('History', 'log size')
    if max_backups is None:
        max_backups = config.get('History', 'log backups')
    handler = logging.handlers.RotatingFileHandler(
        USER_LOG_FILE, 'a', max_size, max_backups)
    handler.setFormatter(applet_log_formatter)
    applet_log.removeHandler(applet_log_handler)
    applet_log_handler = handler
    applet_log.addHandler(applet_log_handler)


#############################################################################
# item operations functions

# wrapper around removal function, accepts list of '[type:]name' or single str
def remove_item_specs(item_specs):
    if not isinstance(item_specs, list):
        item_specs = [item_specs]
    to_delete = []
    not_deleted = []
    for item in item_specs:
        if ITEM_SPEC_SEPARATOR in item:
            t, n = item.split(ITEM_SPEC_SEPARATOR)
            t = t.lower()
            if ITEM_TYPE_CONDITIONS.startswith(t):
                to_delete.append((ITEM_TYPE_CONDITIONS, n))
            elif ITEM_TYPE_SIGNAL_HANDLERS.startswith(t):
                to_delete.append((ITEM_TYPE_SIGNAL_HANDLERS, n))
            elif ITEM_TYPE_TASKS.startswith(t):
                to_delete.append((ITEM_TYPE_TASKS, n))
            else:
                applet_log.warning("MAIN: incorrect type %s specified for item %s" % (t, n))
                not_deleted.append((t, n, ITEM_OPERATION_ERR_TYPE))
        else:
            if item in conditions.names:
                if item in tasks.names or item in signal_handlers.names:
                    applet_log.warning("MAIN: cannot delete item %s: name conflict" % item)
                    not_deleted.append((ITEM_TYPE_CONDITIONS, item,
                                        ITEM_OPERATION_ERR_CONFLICT))
                else:
                    to_delete.append((ITEM_TYPE_CONDITIONS, item))
            elif item in tasks.names:
                if item in conditions.names or item in signal_handlers.names:
                    applet_log.warning("MAIN: cannot delete item %s: name conflict" % item)
                    not_deleted.append((ITEM_TYPE_TASKS, item,
                                        ITEM_OPERATION_ERR_CONFLICT))
                else:
                    to_delete.append((ITEM_TYPE_TASKS, item))
            elif item in signal_handlers.names:
                if item in conditions.names or item in tasks.names:
                    applet_log.warning("MAIN: cannot delete item %s: name conflict" % item)
                    not_deleted.append((ITEM_TYPE_SIGNAL_HANDLERS, item,
                                        ITEM_OPERATION_ERR_CONFLICT))
                else:
                    to_delete.append((ITEM_TYPE_SIGNAL_HANDLERS, item))
            else:
                applet_log.warning("MAIN: cannot delete item %s: item not found" % item)
                not_deleted.append((ITEM_TYPE_UNKNOWN, item,
                                    ITEM_OPERATION_ERR_NOTFOUND))
    not_deleted += remove_items(to_delete)
    return not_deleted


# this function deletes items as provided as a list of (itemtype, name) pairs
# as long as this doesn't create dependency problems with conditions; expects
# all item collections to be loaded and can be called from within the applet
def remove_items(item_list):
    applet_log.info("MAIN: requesting deletion of possibly multiple items")
    not_deleted = []
    items = [e[1] for e in item_list if e[0] == ITEM_TYPE_CONDITIONS]
    removed = False
    for item_name in items:
        if item_name not in conditions.names:
            applet_log.warning("MAIN: condition %s specified for removal but not found" % item_name)
            not_deleted.append(
                (ITEM_TYPE_CONDITIONS, item_name, ITEM_OPERATION_ERR_NOTFOUND))
        else:
            if not conditions.remove(cond_name=item_name):
                applet_log.warning("MAIN: could not remove condition %s" % item_name)
                not_deleted.append(
                    (ITEM_TYPE_CONDITIONS, item_name,
                     ITEM_OPERATION_ERR_UNKNOWN))
            else:
                removed = True
    if removed:
        conditions.save()
    items = [e[1] for e in item_list if e[0] == ITEM_TYPE_SIGNAL_HANDLERS]
    removed = False
    for item_name in items:
        if item_name not in signal_handlers.names:
            applet_log.warning("MAIN: signal handler %s specified for removal but not found" % item_name)
            not_deleted.append(
                (ITEM_TYPE_SIGNAL_HANDLERS, item_name,
                 ITEM_OPERATION_ERR_NOTFOUND))
        else:
            if not signal_handlers.remove(handler_name=item_name):
                applet_log.warning("MAIN: could not remove signal handler %s" % item_name)
                not_deleted.append(
                    (ITEM_TYPE_SIGNAL_HANDLERS, item_name,
                     ITEM_OPERATION_ERR_UNKNOWN))
            else:
                removed = True
    if removed:
        signal_handlers.save()
    items = [e[1] for e in item_list if e[0] == ITEM_TYPE_TASKS]
    removed = False
    for item_name in items:
        if item_name not in tasks.names:
            applet_log.warning("MAIN: task %s specified for removal but not found" % item_name)
            not_deleted.append(
                (ITEM_TYPE_TASKS, item_name, ITEM_OPERATION_ERR_NOTFOUND))
        else:
            if not tasks.remove(task_name=item_name):
                applet_log.warning("MAIN: could not remove task %s" % item_name)
                not_deleted.append(
                    (ITEM_TYPE_TASKS, item_name, ITEM_OPERATION_ERR_UNKNOWN))
            else:
                removed = True
    if removed:
        tasks.save()
    return not_deleted


#############################################################################
# this class can create items by interpreting an .ini like file
class ItemDataFileInterpreter(object):
    _data_parser = None

    def __init__(self, data=None):
        self._data = None
        self._data_parser = configparser.ConfigParser()
        if data:
            self._data = self.load_data(data)

    # will not partially load a file even if a single item is incorrect
    # NOTE: entry names are hard-coded here as with the configuration file
    def load_data(self, data):
        try:
            self._data_parser.read_string(data)
        except configparser.Error:
            raise ValueError("bad item data file structure")
        store = []
        for item_name in self._data_parser.sections():
            values = self._data_parser[item_name]
            if 'type' not in values:
                raise ValueError("type not specified for item '%s'" % item_name)
            item_type = values['type'].lower()
            if item_type == 'task':
                if not VALIDATE_TASK_RE.match(item_name):
                    raise ValueError("invalid name for task: '%s'" % item_name)
                if 'command' not in values:
                    raise ValueError("command not specified for task '%s'"
                                     % item_name)
                d = {
                    'type': 'task',
                    'task_name': item_name,
                    'task_id': tasks.get_id(),
                    'environment_vars': {},
                    'include_env': True,
                    'success_stdout': None,
                    'success_stderr': None,
                    'success_status': 0,
                    'failure_stdout': None,
                    'failure_stderr': None,
                    'failure_status': None,
                    'match_exact': False,
                    'match_regexp': False,
                    'case_sensitive': False,
                    'startup_dir': '',
                    'command': values['command'],
                }
                if 'environment variables' in values:
                    li = values['environment variables'].split('\n')
                    value = {}
                    for x in li:
                        x = x.strip()
                        if x and '=' in x:
                            var, val = x.split('=', 1)
                            if not VALIDATE_ENVVAR_RE.match(var):
                                raise ValueError("invalid variable name '%s'"
                                                 % var)
                            value[var] = val
                    d['environment_vars'] = value
                if 'import environment' in values:
                    d['include_env'] = values.getboolean('import environment')
                if 'check for' in values:
                    value = values['check for'].strip()
                    if value.lower() == 'nothing':
                        d['success_status'] = None
                    else:
                        outcome, source, value = map(str.strip,
                                                     value.split(',', 2))
                        if source.lower() == 'status':
                            value = int(value)
                            if outcome.lower() == 'success':
                                d['success_status'] = value
                            elif outcome.lower() == 'failure':
                                d['success_status'] = None
                                d['failure_status'] = value
                            else:
                                raise ValueError(
                                    "invalid outcome specification '%s'"
                                    % outcome)
                        else:
                            d['success_status'] = None
                            if source.lower() == 'stdout':
                                if outcome.lower() == 'success':
                                    d['success_stdout'] = value
                                elif outcome.lower() == 'failure':
                                    d['failure_stdout'] = value
                                else:
                                    raise ValueError(
                                        "invalid outcome specification '%s'"
                                        % outcome)
                            elif source.lower() == 'stderr':
                                if outcome.lower() == 'success':
                                    d['success_stderr'] = value
                                elif outcome.lower() == 'failure':
                                    d['failure_stderr'] = value
                                else:
                                    raise ValueError(
                                        "invalid outcome specification '%s'"
                                        % outcome)
                            if 'exact match' in values:
                                d['match_exact'] = values.getboolean('exact match')
                            if 'regexp match' in values:
                                d['match_regexp'] = values.getboolean('regexp match')
                            if 'case sensitive' in values:
                                d['case_sensitive'] = values.getboolean('case sensitive')
                if 'startup directory' in values:
                    value = values['startup directory'].strip()
                    d['startup_dir'] = value
            elif item_type == 'condition':
                if 'based on' not in values:
                    raise ValueError("type not specified for condition '%s'"
                                     % item_name)
                deftype = values['based on'].lower()
                subtype_map = {
                    'interval': 'IntervalBasedCondition',
                    'time': 'TimeBasedCondition',
                    'command': 'CommandBasedCondition',
                    'idle_session': 'IdleTimeBasedCondition',
                    'event': 'EventBasedCondition',
                    'file_change': 'PathNotifyBasedCondition',
                    'user_event': 'EventBasedCondition',
                    # TODO: add more type associations here
                }
                if deftype not in subtype_map:
                    raise ValueError("incorrect condition type specified: '%s'"
                                     % deftype)
                subtype = subtype_map[deftype]
                task_list = []
                if 'task names' in values:
                    task_list = list(map(str.strip,
                                         values['task names'].split(',')))
                    for x in task_list:
                        if not VALIDATE_TASK_RE.match(x):
                            raise ValueError("incorrect task name: '%s'" % x)
                d = {
                    'type': 'condition',
                    'cond_name': item_name,
                    'cond_id': conditions.get_id(),
                    'subtype': subtype,
                    'task_names': task_list,
                    'repeat': True,
                    'exec_sequence': True,
                    'suspended': False,
                    'break_failure': False,
                    'break_success': False,
                }
                if 'repeat checks' in values:
                    d['repeat'] = values.getboolean('repeat checks')
                if 'sequential' in values:
                    d['exec_sequence'] = values.getboolean('sequential')
                if 'suspended' in values:
                    d['suspended'] = values.getboolean('suspended')
                if 'break on' in values:
                    value = values['break on'].lower()
                    if value == 'success':
                        d['break_success'] = True
                    elif value == 'failure':
                        d['break_failure'] = True
                    elif value != 'nothing':
                        raise ValueError("condition break cause incorrect: '%s'"
                                         % value)
                if deftype == 'interval':
                    if 'interval minutes' not in values:
                        raise ValueError("interval minutes must be specified")
                    value = values.getint('interval minutes')
                    if value <= 0:
                        raise ValueError("invalid interval minutes: %s" % value)
                    d['interval'] = value * 60
                elif deftype == 'time':
                    d['year'] = None
                    d['month'] = None
                    d['day'] = None
                    d['hour'] = 0
                    d['minute'] = 0
                    d['weekday'] = None
                    if 'year' in values:
                        d['year'] = values.getint('year')
                    if 'month' in values:
                        value = values.getint('month')
                        if 1 <= value <= 12:
                            d['month'] = value
                        else:
                            raise ValueError("invalid month: %s" % value)
                    if 'day' in values:
                        value = values.getint('day')
                        if 1 <= value <= 31:
                            d['day'] = value
                        else:
                            raise ValueError("invalid day: %s" % value)
                    if 'hour' in values:
                        value = values.getint('hour')
                        if 0 <= value <= 23:
                            d['hour'] = value
                        else:
                            raise ValueError("invalid hour: %s" % value)
                    if 'minute' in values:
                        value = values.getint('minute')
                        if 0 <= value <= 59:
                            d['minute'] = value
                        else:
                            raise ValueError("invalid minute: %s" % value)
                    if 'day of week' in values:
                        value = values['day of week'].lower()
                        if value in (1, 'monday'):
                            d['weekday'] = 0
                        elif value in (2, 'tuesday'):
                            d['weekday'] = 1
                        elif value in (3, 'wednesday'):
                            d['weekday'] = 2
                        elif value in (4, 'thursday'):
                            d['weekday'] = 3
                        elif value in (5, 'friday'):
                            d['weekday'] = 4
                        elif value in (6, 'saturday'):
                            d['weekday'] = 5
                        elif value in (7, 'sunday'):
                            d['weekday'] = 6
                        else:
                            raise ValueError("incorrect weekday value: '%s'"
                                             % value)
                elif deftype == 'command':
                    if 'command' not in values:
                        raise ValueError("command must be specified")
                    d['command'] = values['command']
                    d['match_exact'] = False
                    d['match_regexp'] = False
                    d['case_sensitive'] = False
                    d['expected_status'] = 0
                    d['expected_stdout'] = None
                    d['expected_stderr'] = None
                    if 'check for' in values:
                        value = values['check for']
                        source, value = map(str.strip, value.split(',', 1))
                        if source == 'status':
                            d['expected_status'] = int(value)
                        else:
                            d['expected_status'] = None
                            if source == 'stdout':
                                d['expected_stdout'] = value
                            elif source == 'stderr':
                                d['expected_stderr'] = value
                            else:
                                raise ValueError(
                                    "invalid source for outcome check: '%s'"
                                    % source)
                            if 'exact match' in values:
                                d['match_exact'] = values.getboolean('exact match')
                            if 'regexp match' in values:
                                d['match_regexp'] = values.getboolean('regexp match')
                            if 'case sensitive' in values:
                                d['case_sensitive'] = values.getboolean('case sensitive')
                elif deftype == 'idle_session':
                    if 'idle minutes' not in values:
                        raise ValueError("idle minutes must be specified")
                    value = values.getint('idle minutes') * 60
                    if value <= 0:
                        raise ValueError("invalid idle time: %s seconds"
                                         % value)
                    d['idle_secs'] = value
                elif deftype == 'event':
                    if 'event type' not in values:
                        raise ValueError("event type must be specified")
                    value = values['event type'].lower()
                    event_map = {
                        'startup': EVENT_APPLET_STARTUP,
                        'shutdown': EVENT_APPLET_SHUTDOWN,
                        'suspend': EVENT_SYSTEM_SUSPEND,
                        'resume': EVENT_SYSTEM_RESUME,
                        'connect_storage': EVENT_SYSTEM_DEVICE_ATTACH,
                        'disconnect_storage': EVENT_SYSTEM_DEVICE_DETACH,
                        'join_network': EVENT_SYSTEM_NETWORK_JOIN,
                        'leave_network': EVENT_SYSTEM_NETWORK_LEAVE,
                        'screensaver': EVENT_SESSION_SCREENSAVER,
                        'exit_screensaver': EVENT_SESSION_SCREENSAVER_EXIT,
                        'lock': EVENT_SESSION_LOCK,
                        'unlock': EVENT_SESSION_UNLOCK,
                        'charging': EVENT_SYSTEM_BATTERY_CHARGE,
                        'discharging': EVENT_SYSTEM_BATTERY_DISCHARGING,
                        'battery_low': EVENT_SYSTEM_BATTERY_LOW,
                        'command_line': EVENT_COMMAND_LINE,
                        # TODO: add more predefined events here
                    }
                    if value not in event_map:
                        raise ValueError("invalid event type")
                    event = event_map[value]
                    if value == 'command_line':
                        event = EVENT_COMMAND_LINE_PREAMBLE + ':' + item_name
                    d['event'] = event
                    d['no_skip'] = True
                elif deftype == 'file_change':
                    if 'watched path' not in values:
                        raise ValueError("watched path must be specified")
                    value = values['watched path']
                    d['watched_paths'] = [value]
                    d['no_skip'] = True
                elif deftype == 'user_event':
                    if not config.get('General', 'user events'):
                        raise ValueError("signal handlers are not enabled")
                    if 'event name' not in values:
                        raise ValueError("event name must be specified")
                    value = values['event name']
                    if not VALIDATE_SIGNAL_HANDLER_RE.match(value):
                        raise ValueError("invalid name for user event: '%s'"
                                         % value)
                    d['event'] = EVENT_DBUS_SIGNAL_PREAMBLE + ':' + value
                    d['no_skip'] = True
            elif item_type == 'signal_handler':
                if not config.get('General', 'user events'):
                    raise ValueError("signal handlers are not enabled")
                if 'bus name' not in values or not VALIDATE_DBUS_NAME_RE.match(values['bus name']):
                    raise ValueError("bus name must be correctly specified")
                if 'object path' not in values or not VALIDATE_DBUS_PATH_RE.match(values['object path']):
                    raise ValueError("object path must be correctly specified")
                if 'interface' not in values or not VALIDATE_DBUS_INTERFACE_RE.match(values['interface']):
                    raise ValueError("interface must be correctly specified")
                if 'signal' not in values or not VALIDATE_DBUS_SIGNAL_RE.match(values['signal']):
                    raise ValueError("signal must be correctly specified")
                d = {
                    'type': 'dbus_signal_handler',
                    'handler_name': item_name,
                    'bus': 'session',
                    'bus_name': values['bus name'],
                    'bus_path': values['object path'],
                    'interface': values['interface'],
                    'signal': values['signal'],
                    'param_checks': [],
                    'verify_all_checks': False,
                    'defer': True,
                }
                if 'bus' in values:
                    value = values['bus']
                    if value in ('session', 'system'):
                        d['bus'] = value
                    else:
                        raise ValueError("incorrect value for bus: '%s'"
                                         % value)
                if 'defer' in values:
                    d['defer'] = values.getboolean('defer')
                if 'parameters' in values:
                    param_list = values['parameters'].split('\n')
                    param_checks = []
                    for p in param_list:
                        p = p.strip()
                        if p:
                            elem, oper, value = map(str.strip, p.split(',', 2))
                            oper = oper.lower()
                            t = elem.split(':', 1)
                            if len(t) == 1:
                                v, sub = int(elem), None
                            else:
                                v = int(t[0])
                                try:
                                    sub = int(t[1])
                                except ValueError:
                                    sub = t[1]
                                    if not VALIDATE_DBUS_SUBPARAM_RE.match(sub):
                                        raise ValueError(
                                            "invalid value for parameter subindex: '%s'"
                                            % sub)
                            if v < 0 or (type(sub) == int and sub < 0):
                                raise ValueError(
                                    "invalid value for parameter index or subindex: %s, %s"
                                    % (v, sub))
                            t = oper.split()
                            neg = False
                            if len(t) == 2:
                                if t[0] == 'not':
                                    neg = True
                                else:
                                    raise ValueError("incorrect operator: '%s'"
                                                     % oper)
                                oper = t[1]
                            elif len(t) > 2:
                                raise ValueError("incorrect operator: '%s'"
                                                 % oper)
                            oper_map = {
                                'equal': DBUS_CHECK_COMPARE_IS,
                                'gt': DBUS_CHECK_COMPARE_GREATER,
                                'lt': DBUS_CHECK_COMPARE_LESS,
                                'contains': DBUS_CHECK_COMPARE_CONTAINS,
                                'matches': DBUS_CHECK_COMPARE_MATCHES,
                            }
                            if oper not in oper_map:
                                raise ValueError("incorrect operator: '%s'"
                                                 % oper)
                            o = oper_map[oper]
                            param_checks.append((v, sub, o, neg, value))
                    d['param_checks'] = param_checks
                    if 'verify' in values:
                        value = values['verify'].lower()
                        if value == 'all':
                            d['verify_all_checks'] = True
                        elif value == 'any':
                            d['verify_all_checks'] = False
                        else:
                            raise ValueError("incorrect verify value: '%s'"
                                             % value)
            # add the item dictionary to the temporary store
            store.append(d)
        # if we are here without raising exceptions, the only checks
        # still to be made are that conditions rely on existing items
        task_names = [d['task_name'] for d in store if 'task_name' in d]
        sighandler_names = [
            d['handler_name'] for d in store if 'handler_name' in d]
        if not ITEM_ADD_SELF_CONTAINED:
            task_names += tasks.names
            sighandler_names += signal_handlers.names
        for cond in [d for d in store if d['type'] == 'condition']:
            for name in cond['task_names']:
                if name not in task_names:
                    raise ValueError("unknown task name: '%s'" % name)
            if 'event' in cond and cond['event'].startswith(EVENT_DBUS_SIGNAL_PREAMBLE + ':'):
                name = cond['event'].split(':')[1]
                if name not in sighandler_names:
                    raise ValueError("unknown signal handler name: '%s'" % name)
        # all tests passed
        return store

    def create_items(self):
        if not self._data:
            raise ValueError("items not loaded")
        new_tasks = []
        new_signal_handlers = []
        new_conditions = []
        for item_dict in self._data:
            item_type = item_dict['type']
            if item_type == 'condition':
                subtype = item_dict['subtype']
                if subtype == 'IntervalBasedCondition':
                    item = dict_to_IntervalBasedCondition(item_dict)
                elif subtype == 'TimeBasedCondition':
                    item = dict_to_TimeBasedCondition(item_dict)
                elif subtype == 'CommandBasedCondition':
                    item = dict_to_CommandBasedCondition(item_dict)
                elif subtype == 'IdleTimeBasedCondition':
                    item = dict_to_IdleTimeBasedCondition(item_dict)
                elif subtype == 'EventBasedCondition':
                    item = dict_to_EventBasedCondition(item_dict)
                elif subtype == 'PathNotifyBasedCondition':
                    item = dict_to_PathNotifyBasedCondition(item_dict)
                new_conditions.append(item)
            elif item_type == 'task':
                item = dict_to_Task(item_dict)
                new_tasks.append(item)
            elif item_type == 'dbus_signal_handler':
                item = dict_to_SignalHandler(item_dict)
                new_signal_handlers.append(item)
        for item in new_signal_handlers:
            signal_handlers.add(item)
        for item in new_tasks:
            tasks.add(item)
        for item in new_conditions:
            conditions.add(item)


#############################################################################
# the DBus service is needed for the running applet to receive commands
class AppletDBusService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName(APPLET_BUS_NAME, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, APPLET_BUS_PATH)

    @dbus.service.method(APPLET_BUS_NAME)
    def kill_instance(self):
        self.remove_from_connection()
        Gtk.main_quit()

    @dbus.service.method(APPLET_BUS_NAME)
    def quit_instance(self):
        self.remove_from_connection()
        applet.quit(None)

    @dbus.service.method(APPLET_BUS_NAME)
    def show_dialog(self, dlgname):
        if dlgname == 'settings':
            applet.dlgsettings(None)
        elif dlgname == 'about':
            applet.dlgabout(None)
        elif dlgname == 'task':
            applet.dlgtask(None)
        elif dlgname == 'condition':
            applet.dlgcondition(None)
        elif dlgname == 'history':
            applet.dlghistory(None)
        elif dlgname == 'dbus_signal':
            applet.dlgdbussignal(None)

    @dbus.service.method(APPLET_BUS_NAME)
    def show_icon(self, show=True):
        applet.hide_icon(not show)

    @dbus.service.method(APPLET_BUS_NAME)
    def run_condition(self, cond_name, deferred=False):
        return applet.start_event_condition(cond_name, deferred)

    @dbus.service.method(APPLET_BUS_NAME)
    def export_history(self, file_name):
        return applet.export_task_history(file_name)

    # NOTE: to self/to remove: rv is None on OK or error string on failure
    @dbus.service.method(APPLET_BUS_NAME)
    def add_items(self, item_data):
        return applet.add_items(item_data)

    @dbus.service.method(APPLET_BUS_NAME)
    def del_item(self, item_spec):
        li = remove_item_specs(item_spec)
        if len(li) > 1:
            applet_log.error("SERVICE: NTBS: too many items not deleted than expected (%s)" % len(li))
            for x in li:
                if x[2] == ITEM_OPERATION_OK:
                    reason = "no error"
                elif x[2] == ITEM_OPERATION_ERR_TYPE:
                    reason = "invalid or unknown type"
                elif x[2] == ITEM_OPERATION_ERR_NOTFOUND:
                    reason = "item not found"
                elif x[2] == ITEM_OPERATION_ERR_CONFLICT:
                    reason = "name conflict"
                else:
                    reason = "unknown error"
                applet_log.error("SERVICE: NTBS: item specification %s:%s marked as not removed (%s)" % (x[0], x[1], reason))
            rv = '/'.join(['%s:%s:%s' % t for t in li])
        else:
            if li:
                x = li[0]
                if x[2] == ITEM_OPERATION_OK:
                    reason = "no error"
                elif x[2] == ITEM_OPERATION_ERR_TYPE:
                    reason = "invalid or unknown type"
                elif x[2] == ITEM_OPERATION_ERR_NOTFOUND:
                    reason = "item not found"
                elif x[2] == ITEM_OPERATION_ERR_CONFLICT:
                    reason = "name conflict"
                else:
                    reason = "unknown error"
                applet_log.warning("SERVICE: item specification %s:%s could not be deleted (%s)" % (x[0], x[1], reason))
                rv = '%s:%s:%s' % li[0]
            else:
                applet_log.info("SERVICE: item specification %s has been removed" % item_spec)
                rv = None
        return rv


#############################################################################
# Core classes

# Main configuration handler
class Config(object):
    _config_file = None
    _config_parser = None

    def __init__(self, config_file=USER_CONFIG_FILE):
        def bool_spec(v):
            if type(v) == str:
                v = v.lower()
                if v in ('true', 'yes', 'on', '1'):
                    return True
                elif v in ('false', 'no', 'off', '0'):
                    return False
                else:
                    return None
            else:
                return bool(v)
        self._config_file = config_file
        self._config_parser = configparser.ConfigParser()
        self._default()
        if os.path.exists(self._config_file):
            self.load()
        else:
            self.save()
        self._types = {
            'Scheduler': {
                'tick seconds': int,
                'skip seconds': int,
                'preserve pause': bool_spec,
            },
            'General': {
                'show icon': bool_spec,
                'autostart': bool_spec,
                'notifications': bool_spec,
                'log level': str,
                'icon theme': str,
                'user events': bool_spec,
                'file notifications': bool_spec,
                'environment vars': bool_spec,
                'minimalistic mode': bool_spec,
            },
            'Concurrency': {
                'max threads': int,
            },
            'History': {
                'max items': int,
                'log size': int,
                'log backups': int,
            },
        }

    def _default(self):
        self._config_parser.read_string("""
            [Scheduler]
            tick seconds = 15
            skip seconds = 60
            preserve pause = true

            [General]
            show icon = true
            autostart = false
            notifications = true
            icon theme = guess
            log level = warning
            user events = false
            file notifications = false
            environment vars = true
            minimalistic mode = false

            [Concurrency]
            max threads = 5

            [History]
            max items = 100
            log size = 1048576
            log backups = 4
            """)

    def get(self, section, entry):
        type_spec = self._types[section][entry]
        return type_spec(self._config_parser.get(section, entry))

    def set(self, section, entry, value):
        typespec = self._types[section][entry]
        try:
            v = str(typespec(value))
            if type(v) == bool:
                v = v.lower()
            self._config_parser.set(section, entry, v)
        except (TypeError, configparser.Error) as e:
            applet_log.warning("CONFIG: cannot set option %s:%s = %s [%s]" % (section, entry, value, _x(e)))

    def load(self):
        try:
            self._config_parser.read(self._config_file)
        except configparser.Error as e:
            applet_log.warning("CONFIG: malformed configuration file, using default [%s]" % _x(e))
            self._default()
            self.save()

    def reset(self):
        self._default()
        self.save()

    def save(self):
        try:
            with open(self._config_file, mode='w') as f:
                self._config_parser.write(f)
        except IOError as e:
            applet_log.error("CONFIG: cannot write file %s [%s]" % (_config_file, _x(e)))


# scheduler logic, see http://stackoverflow.com/a/18906292 for details
class Periodic(object):
    def __init__(self, interval, function, *args, **kwargs):
        self.stopped = True
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._logger = logging.getLogger(APPLET_NAME)
        self._lock = threading.Lock()
        self._timer = None
        self._logger.info("SCHED: initialized")
        if kwargs.pop('autostart', True):
            self.start()

    def _run(self):
        self.start(from_run=True)
        self._logger.info("SCHED: periodic run")
        self.function(*self.args, **self.kwargs)

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self.stopped:
            self.stopped = False
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
        self._lock.release()
        if not from_run:
            self._logger.info("SCHED: started")

    def stop(self):
        self._lock.acquire()
        self.stopped = True
        if self._timer is not None:
            self._timer.cancel()
        self._lock.release()
        self._logger.info("SCHED: stopped")

    def restart(self, new_interval=None):
        if new_interval:
            self._logger.info("SCHED: changing interval to %s" % new_interval)
            self.interval = new_interval
        self.stop()
        self.start()


# module level functions to handle condition checks and thus task execution
def periodic_condition_check():
    global current_deferred_events
    global current_deferred_changed_paths
    applet_lock.acquire()
    current_deferred_events = deferred_events.items(clear=True)
    current_deferred_changed_paths = deferred_watch_paths.items(clear=True)
    applet_lock.release()
    try:
        with ThreadPoolExecutor(config.get('Concurrency', 'max threads')) as e:
            e.map(lambda c: c.tick(), conditions)
    finally:
        applet_lock.acquire()
        current_deferred_changed_paths = None
        current_deferred_events = None
        applet_lock.release()


# check among the system event conditions setting the global system event
def sysevent_condition_check(event, param=None):
    global current_system_event
    applet_lock.acquire()
    current_system_event = event
    applet_lock.release()
    try:
        if periodic.stopped:
            applet_log.info("SYSEVENT: check skipped due to scheduler pause")
            return
        conds = [c for c in conditions if type(c) == EventBasedCondition]
        with ThreadPoolExecutor(config.get('Concurrency', 'max threads')) as e:
            e.map(lambda c: c.tick(), conds)
    finally:
        applet_lock.acquire()
        current_system_event = None
        applet_lock.release()


# check among the path notifications by setting the global changed path:
# it is not going to be used for now, all file notification events are handled
# in a deferred fashion until a safe way to specify synchronous notifications
# is found, maybe using a dedicated lock
def pathchanged_condition_check(path):
    global current_changed_path
    applet_lock.acquire()
    current_changed_path = path
    # applet_lock.release()     # FIXME: should it be released here?
    try:
        if periodic.stopped:
            applet_log.info("PATHNOTIFY: check skipped due to scheduler pause")
            return
        conds = [c for c in conditions if type(c) == PathNotifyBasedCondition]
        with ThreadPoolExecutor(config.get('Concurrency', 'max threads')) as e:
            e.map(lambda c: c.tick(), conds)
    finally:
        # applet_lock.acquire()
        current_changed_path = None
        applet_lock.release()


# application-wide collections
class Tasks(object):
    _list = []
    _last_id = 0
    _lock = threading.Lock()

    def __iter__(self):
        for task in self._list:
            yield task

    names = property(lambda self: [t.task_name for t in self._list])

    def get_id(self):
        self._lock.acquire()
        self._last_id += 1
        retval = self._last_id
        self._lock.release()
        return retval

    def save(self):
        l = []
        for t in self._list:
            t.dump()
            l.append(t.task_name)
        file_name = os.path.join(USER_CONFIG_FOLDER, FILE_CONFIG_LIST_TASKS)
        with open(file_name, 'wb') as f:
            pickle.dump(l, f)

    def load(self):
        self._list = []
        self._last_id = 0
        file_name = os.path.join(USER_CONFIG_FOLDER, FILE_CONFIG_LIST_TASKS)
        with open(file_name, 'rb') as f:
            l = pickle.load(f)
        for x in l:
            t = Task.restore(x)
            self.add(t)

    def add(self, task):
        if task.task_id == 0:
            raise ValueError("task must be initialized or loaded")
        if task.task_id <= self._last_id or task.task_name in [t.task_name for t in self._list]:
            applet_log.info("GLOBAL: adding task %s" % task.task_name)
            self._lock.acquire()
            l = [x for x in self._list if x.task_name != task.task_name]
            l.append(task)
            self._list = l
            self._lock.release()
        else:
            self._lock.acquire()
            self._list.append(task)
            self._lock.release()

    def remove(self, task_name=None, task_id=None):
        task = None
        if task_id:
            task = next((t for t in self._list if t.task_id == task_id), None)
        elif task_name:
            task = next((t for t in self._list if t.task_name == task_name), None)
        if task:
            removable = True
            for c in conditions:
                if task.task_name in c.task_names:
                    removable = False
                    applet_log.warning("GLOBAL: cannot delete task %s used in condition %s" % (task_name, c.cond_name))
                    break
            if removable:
                self._lock.acquire()
                self._list.remove(task)
                task.unlink_file()
                self._lock.release()
                return True
            else:
                return False
        else:
            return False

    def get(self, task_id=None, task_name=None):
        if task_id:
            return next((x for x in self._list if task_id == x.task_id), None)
        elif task_name:
            return next((x for x in self._list if task_name == x.task_name), None)


class Conditions(object):
    _list = []
    _last_id = 0
    _lock = threading.Lock()

    def __iter__(self):
        for condition in self._list:
            yield condition

    names = property(lambda self: [t.cond_name for t in self._list])

    def get_id(self):
        self._lock.acquire()
        self._last_id += 1
        retval = self._last_id
        self._lock.release()
        return retval

    def save(self):
        l = []
        for c in self._list:
            c.dump()
            l.append((c.cond_name, c.__class__.__name__))
        file_name = os.path.join(USER_CONFIG_FOLDER, FILE_CONFIG_LIST_CONDITIONS)
        with open(file_name, 'wb') as f:
            pickle.dump(l, f)

    def load(self):
        self._list = []
        self._last_id = 0
        file_name = os.path.join(USER_CONFIG_FOLDER, FILE_CONFIG_LIST_CONDITIONS)
        with open(file_name, 'rb') as f:
            l = pickle.load(f)
        for x, xc in l:
            c = Condition.restore(x)
            c.reset()
            self.add(c)

    def add(self, cond):
        if cond.cond_id == 0:
            raise ValueError("condition must be initialized or loaded")
        if cond.cond_id <= self._last_id or cond.cond_name in [t.cond_name for t in self._list]:
            applet_log.info("GLOBAL: adding condition %s" % cond.cond_name)
            self._lock.acquire()
            l = [x for x in self._list if x.cond_name != cond.cond_name]
            l.append(cond)
            if 'activate' in dir(cond) and watch_path_manager is not None:
                cond.activate()
            self._list = l
            self._lock.release()
        else:
            self._lock.acquire()
            self._list.append(cond)
            if 'activate' in dir(cond) and watch_path_manager is not None:
                cond.activate()
            self._lock.release()

    def remove(self, cond_name=None, cond_id=None):
        cond = None
        if cond_id:
            cond = next((c for c in self._list if c.cond_id == cond_id), None)
        elif cond_name:
            cond = next((c for c in self._list if c.cond_name == cond_name), None)
        if cond:
            self._lock.acquire()
            if 'deactivate' in dir(cond) and watch_path_manager is not None:
                cond.deactivate()
            self._list.remove(cond)
            cond.unlink_file()
            self._lock.release()
            return True
        else:
            return False

    def get(self, cond_id=None, cond_name=None):
        if cond_id:
            return next((c for c in self._list if c.cond_id == cond_id), None)
        elif cond_name:
            return next((c for c in self._list if c.cond_name == cond_name), None)


class SignalHandlers(object):

    _list = []
    _lock = threading.Lock()

    def __iter__(self):
        for handler in self._list:
            yield handler

    names = property(lambda self: [h.handler_name for h in self._list])
    not_empty = property(lambda self: bool(self._list))

    def save(self):
        l = []
        for h in self._list:
            h.dump()
            l.append(h.handler_name)
        file_name = os.path.join(
            USER_CONFIG_FOLDER, FILE_CONFIG_LIST_SIGNAL_HANDLERS)
        with open(file_name, 'wb') as f:
            pickle.dump(l, f)

    def load(self):
        self._list = []
        file_name = os.path.join(
            USER_CONFIG_FOLDER, FILE_CONFIG_LIST_SIGNAL_HANDLERS)
        with open(file_name, 'rb') as f:
            l = pickle.load(f)
        for x in l:
            h = SignalHandler.restore(x)
            self.add(h)

    def add(self, handler):
        applet_log.info("GLOBAL: adding signal handler %s" % handler.handler_name)
        if handler.handler_name in [h.handler_name for h in self._list]:
            old_handler = self.get(handler.handler_name)
            self._lock.acquire()
            l = list(
                x for x in self._list if x.handler_name != handler.handler_name)
            l.append(handler)
            reg = None
            applet_log.info("GLOBAL: unregistering old signal handler %s" % old_handler.handler_name)
            if old_handler.unregister():
                reg = handler.register()
            self._list = l
            self._lock.release()
        else:
            self._lock.acquire()
            reg = handler.register()
            self._list.append(handler)
            self._lock.release()
        if not reg:
            applet_log.error("GLOBAL: could not register signal handler %s" % handler.handler_name)
            return False
        else:
            return True

    def remove(self, handler_name=None):
        handler = None
        if handler_name:
            for c in conditions:
                if type(c) == EventBasedCondition and c.event.startswith(EVENT_DBUS_SIGNAL_PREAMBLE + ':'):
                    if c.event.split(':')[1] == handler_name:
                        applet_log.warning("GLOBAL: cannot delete signal handler %s used in condition %s" % (handler_name, c.cond_name))
                        return False
            handler = next((h for h in self._list if h.handler_name == handler_name), None)
        if handler:
            applet_log.info("GLOBAL: removing signal handler %s" % handler_name)
            self._lock.acquire()
            rv = handler.unregister()
            if rv:
                self._list.remove(handler)
                handler.unlink_file()
            self._lock.release()
            applet_log.debug("GLOBAL: signal handler %s removed" % handler_name)
            return rv
        else:
            if handler_name:
                applet_log.info("GLOBAL: signal handler %s could not be found" % handler_name)
            return False

    def get(self, handler_name):
        return next(
            (x for x in self._list if handler_name == x.handler_name), None)


# data for the history queue (which is actually a resizable bounded deque)
historyitem = namedtuple('historyitem', ['item_id', 'startup_time', 'run_time',
                                         'task_name', 'trigger_cond', 'success',
                                         'exit_code', 'stdout', 'stderr',
                                         'failure_reason'])


class HistoryQueue(object):

    def __init__(self, max_items=None):
        if max_items is None:
            max_items = config.get('History', 'max items')
        self._lock = threading.Lock()
        self._queue = deque(maxlen=max_items)
        self._iter_id = self._item_id()

    def _item_id(self):
        # an ID that is unique just within the queue: a reusable int is enough
        # FIXME: find a way to avoid conflicts when the queue is shrunk
        next_id = 0
        while True:
            yield next_id
            next_id = (next_id + 1) % (self._queue.maxlen * 2)

    def append(self, name, startup_time, success, trigger, status=None, stdout=None, stderr=None, reason=None):
        t = time.time()
        run_time = t - startup_time
        item = historyitem(next(self._iter_id), startup_time, run_time, name,
                           trigger, success, status, stdout, stderr, reason)
        self._lock.acquire()
        self._queue.append(item)
        self._lock.release()

    def resize(self, max_items=None):
        if max_items is None:
            max_items = config.get('History', 'max items')
        self._lock.acquire()
        self._queue = deque(self._queue, max_items)
        self._iter_id = self._item_id()
        self._lock.release()

    def clear(self):
        self._lock.acquire()
        self._queue.clear()
        self._lock.release()

    def item_by_id(self, item_id):
        l = list(item for item in self._queue if item.item_id == item_id)
        if len(l) == 1:
            return l[0]
        else:
            return None

    def items(self, max_items=None):
        self._lock.acquire()
        if not max_items:
            rv = deque(self._queue)
        else:
            rv = deque(self._queue, max_items)
        self._lock.release()
        return list(rv)


# list of events that are enqueued by external agents: it is implemented
# as a set; this means that a deferred event only will appear once, no
# matter how many times it is pushed to the list
class DeferredEvents(object):

    def __init__(self):
        self._lock = threading.Lock()
        self._events = set()

    def append(self, event):
        self._lock.acquire()
        self._events.add(event)
        self._lock.release()

    def clear(self):
        self._lock.acquire()
        self._events.clear()
        self._lock.release()

    def items(self, clear=False):
        self._lock.acquire()
        rv = self._events.copy()
        if clear:
            self._events.clear()
        self._lock.release()
        return rv


# list of monitored files that are enqueued by pyinotify
class DeferredWatchPaths(object):

    def __init__(self):
        self._lock = threading.Lock()
        self._paths = set()

    def append(self, path):
        self._lock.acquire()
        self._paths.add(path)
        self._lock.release()

    def clear(self):
        self._lock.acquire()
        self._paths.clear()
        self._lock.release()

    def items(self, clear=False):
        self._lock.acquire()
        rv = self._paths.copy()
        if clear:
            self._paths.clear()
        self._lock.release()
        return rv


#############################################################################
# The main Task class: this represents a certain task registered in the
# application. It contains all information about the task to execute, as well
# as its environment and postconditions
class Task(object):

    _logger = logging.getLogger(APPLET_NAME)

    # make task level logging easier
    def _debug(self, msg):
        self._logger.debug("TASK: %s [%s]: %s" % (self.task_name, self.task_id, msg))

    def _info(self, msg):
        self._logger.info("TASK: %s [%s]: %s" % (self.task_name, self.task_id, msg))

    def _warning(self, msg):
        self._logger.warning("TASK: %s [%s]: %s" % (self.task_name, self.task_id, msg))

    def _error(self, msg):
        self._logger.error("TASK: %s [%s]: %s" % (self.task_name, self.task_id, msg))

    def _critical(self, msg):
        self._logger.critical("TASK: %s [%s]: %s" % (self.task_name, self.task_id, msg))

    # the real McCoy
    def __init__(self, name=None, command=None, startup_dir=None):
        self.task_id = 0
        self.task_name = name
        self.environment_vars = {}
        self.include_env = True
        self.success_stdout = None
        self.success_stderr = None
        self.success_status = None
        self.failure_stdout = None
        self.failure_stderr = None
        self.failure_status = None
        self.match_exact = False
        self.match_regexp = False
        self.case_sensitive = False
        self.command = ''
        self.startup_dir = None
        self.running = False
        self._process_stdout = ''
        self._process_stderr = ''
        self._process_status = 0
        self._process_failed = False
        if name is None:
            self._info("empty task created")
        else:
            self.command = command
            self.startup_dir = startup_dir
            self.task_id = tasks.get_id()
            self._info("task created")

    def set_env(self, var, value):
        self.environment_vars[var] = value

    def clear_env(self, var):
        self.set_env(var, None)

    def set_check(self, **kwargs):
        for k in kwargs.keys():
            if k == 'success_stdout':
                self.success_stdout = str(kwargs[k])
            elif k == 'success_stderr':
                self.success_stderr = str(kwargs[k])
            elif k == 'failure_stdout':
                self.failure_stdout = str(kwargs[k])
            elif k == 'failure_stderr':
                self.failure_stderr = str(kwargs[k])
            elif k == 'success_status':
                self.success_status = int(kwargs[k])
            elif k == 'failure_status':
                self.failure_status = int(kwargs[k])
            else:
                self._error("internal error")
                raise TypeError("keyword argument '%s' not supported" % k)

    def renew_id(self):
        self.task_id = tasks.get_id()

    def dump(self):
        if self.task_name is None:
            raise RuntimeError("task not initialized")
        file_name = os.path.join(USER_CONFIG_FOLDER, '%s.task' % self.task_name)
        with open(file_name, 'wb') as f:
            pickle.dump(self, f)

    def unlink_file(self):
        file_name = os.path.join(USER_CONFIG_FOLDER, '%s.task' % self.task_name)
        if os.path.exists(file_name):
            os.unlink(file_name)

    @staticmethod
    def restore(name):
        file_name = os.path.join(USER_CONFIG_FOLDER, '%s.task' % name)
        with open(file_name, 'rb') as f:
            o = pickle.load(f)
            o.renew_id()
            return o

    # run a task in a subprocess possibly specifying trigger condition name
    def run(self, trigger_name=None):
        if self.running:
            raise RuntimeError("overlapping tasks")
        applet_lock.acquire()
        self.running = True
        applet_lock.release()
        self._process_failed = False
        if self.task_name is None:
            self._process_failed = True
            raise RuntimeError("task not initialized")
        if trigger_name:
            self._info("[trigger: %s] running command: %s" % (trigger_name, self.command))
        else:
            self._info("[trigger: unknown] running command: %s" % self.command)
        if self.environment_vars:
            if self.include_env:
                env = os.environ.copy()
                for k in self.environment_vars:
                    env[k] = self.environment_vars[k]
                if config.get('General', 'environment vars'):
                    env[ENVVAR_NAME_TASK] = self.task_name
                    env[ENVVAR_NAME_COND] = (
                        trigger_name if trigger_name else ENVVAR_UNKNOWN_COND)
            else:
                env = self.environment_vars
        else:
            if config.get('General', 'environment vars'):
                env = os.environ.copy()
                env[ENVVAR_NAME_TASK] = self.task_name
                env[ENVVAR_NAME_COND] = (
                    trigger_name if trigger_name else ENVVAR_UNKNOWN_COND)
            else:
                env = None
        startup_time = time.time()
        self._process_stdout = None
        self._process_stderr = None
        self._process_status = None
        try:
            failure_reason = None
            startup_dir = self.startup_dir if self.startup_dir else '.'
            self._debug("spawning subprocess: %s" % self.command)
            with subprocess.Popen(self.command,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell=True,
                                  cwd=startup_dir,
                                  env=env) as proc:
                stdout, stderr = proc.communicate()
                self._process_stdout = stdout.decode().strip()
                self._process_stderr = stderr.decode().strip()
                self._process_status = proc.returncode
                if self.success_status is not None:
                    if self._process_status != self.success_status:
                        self._warning("task failed (process status=%s)" % self._process_status)
                        self._process_failed = True
                        failure_reason = 'status'
                elif self.failure_status is not None:
                    if self._process_status == self.failure_status:
                        self._warning("task failed (process status=%s)" % self._process_status)
                        self._process_failed = True
                        failure_reason = 'status'
                elif self.failure_stdout is not None:
                    if self.match_regexp:
                        if self.case_sensitive:
                            flags = 0
                        else:
                            flags = re.IGNORECASE
                        if self.match_exact:
                            if re.match(self.failure_stdout, self._process_stdout, flags) is not None:
                                self._warning("task failed (stdout regexp%s check)" % " nocase" if flags else "")
                                self._process_failed = True
                                failure_reason = 'stdout'
                        else:
                            if re.search(self.failure_stdout, self._process_stdout, flags) is not None:
                                self._warning("task failed (stdout regexp%s check)" % " nocase" if flags else "")
                                self._process_failed = True
                                failure_reason = 'stdout'
                    else:
                        if self.case_sensitive:
                            if self.match_exact:
                                if self._process_stdout == self.failure_stdout:
                                    self._warning("task failed (stdout check)")
                                    self._process_failed = True
                                    failure_reason = 'stdout'
                            else:
                                if self.failure_stdout in self._process_stdout:
                                    self._warning("task failed (stdout check)")
                                    self._process_failed = True
                                    failure_reason = 'stdout'
                        else:
                            if self.match_exact:
                                if self._process_stdout.upper() == self.failure_stdout.upper():
                                    self._warning("task failed (stdout check, case insensitive)")
                                    self._process_failed = True
                                    failure_reason = 'stdout'
                            else:
                                if self.failure_stdout.upper() in self._process_stdout.upper():
                                    self._warning("task failed (stdout check, case insensitive)")
                                    self._process_failed = True
                                    failure_reason = 'stdout'
                elif self.failure_stderr is not None:
                    if self.match_regexp:
                        if self.case_sensitive:
                            flags = 0
                        else:
                            flags = re.IGNORECASE
                        if self.match_exact:
                            if re.match(self.failure_stderr, self._process_stderr, flags) is not None:
                                self._warning("task failed (stderr regexp%s check)" % " nocase" if flags else "")
                                self._process_failed = True
                                failure_reason = 'stderr'
                        else:
                            if re.search(self.failure_stderr, self._process_stderr, flags) is not None:
                                self._warning("task failed (stderr regexp%s check)" % " nocase" if flags else "")
                                self._process_failed = True
                                failure_reason = 'stderr'
                    else:
                        if self.case_sensitive:
                            if self.match_exact:
                                if self._process_stderr == self.failure_stderr:
                                    self._warning("task failed (stderr check)")
                                    self._process_failed = True
                                    failure_reason = 'stderr'
                            else:
                                if self.failure_stderr in self._process_stderr:
                                    self._warning("task failed (stderr check)")
                                    self._process_failed = True
                                    failure_reason = 'stderr'
                        else:
                            if self.match_exact:
                                if self._process_stderr.upper() == self.failure_stderr.upper():
                                    self._warning("task failed (stderr check, case insensitive)")
                                    self._process_failed = True
                                    failure_reason = 'stderr'
                            else:
                                if self.failure_stderr.upper() in self._process_stderr.upper():
                                    self._warning("task failed (stderr check, case insensitive)")
                                    self._process_failed = True
                                    failure_reason = 'stderr'
                elif self.success_stdout is not None:
                    if self.match_regexp:
                        if self.case_sensitive:
                            flags = 0
                        else:
                            flags = re.IGNORECASE
                        if self.match_exact:
                            if re.match(self.success_stdout, self._process_stdout, flags) is None:
                                self._warning("task failed (stdout regexp%s check)" % " nocase" if flags else "")
                                self._process_failed = True
                                failure_reason = 'stdout'
                        else:
                            if re.search(self.success_stdout, self._process_stdout, flags) is None:
                                self._warning("task failed (stdout regexp%s check)" % " nocase" if flags else "")
                                self._process_failed = True
                                failure_reason = 'stdout'
                    else:
                        if self.case_sensitive:
                            if self.match_exact:
                                if self._process_stdout != self.success_stdout:
                                    self._warning("task failed (stdout check)")
                                    self._process_failed = True
                                    failure_reason = 'stdout'
                            else:
                                if self.success_stdout not in self._process_stdout:
                                    self._warning("task failed (stdout check, case insensitive)")
                                    self._process_failed = True
                                    failure_reason = 'stdout'
                        else:
                            if self.match_exact:
                                if self._process_stdout.upper() != self.success_stdout.upper():
                                    self._warning("task failed (stdout check)")
                                    self._process_failed = True
                                    failure_reason = 'stdout'
                            else:
                                if not self.success_stdout.upper() in self._process_stdout.upper():
                                    self._warning("task failed (stdout check, case insensitive)")
                                    self._process_failed = True
                                    failure_reason = 'stdout'
                elif self.success_stderr is not None:
                    if self.match_regexp:
                        if self.case_sensitive:
                            flags = 0
                        else:
                            flags = re.IGNORECASE
                        if self.match_exact:
                            if re.match(self.success_stderr, self._process_stderr, flags) is None:
                                self._warning("task failed (stderr regexp%s check)" % " nocase" if flags else "")
                                self._process_failed = True
                                failure_reason = 'stderr'
                        else:
                            if re.search(self.success_stderr, self._process_stderr, flags) is None:
                                self._warning("task failed (stderr regexp%s check)" % " nocase" if flags else "")
                                self._process_failed = True
                                failure_reason = 'stderr'
                    else:
                        if self.case_sensitive:
                            if self.match_exact:
                                if self._process_stderr != self.success_stderr:
                                    self._warning("task failed (stderr check)")
                                    self._process_failed = True
                                    failure_reason = 'stderr'
                            else:
                                if self.success_stderr not in self._process_stderr:
                                    self._warning("task failed (stderr check)")
                                    self._process_failed = True
                                    failure_reason = 'stderr'
                        else:
                            if self.match_exact:
                                if self._process_stderr.upper() != self.success_stderr.upper():
                                    self._warning("task failed (stderr check, case insensitive)")
                                    self._process_failed = True
                                    failure_reason = 'stderr'
                            else:
                                if self.success_stderr.upper() not in self._process_stderr.upper():
                                    self._warning("task failed (stderr check, case insensitive)")
                                    self._process_failed = True
                                    failure_reason = 'stderr'
        except RuntimeError as e:
            self._warning("task failed, runtime error: %s" % _x(e))
            failure_reason = 'overlap'
        except OSError as e:
            self._warning("task failed, system error: %s" % _x(e))
            self._process_failed = True
            failure_reason = 'system'
        except subprocess.CalledProcessError as e:
            self._warning("task failed, called process error")
            self._process_failed = True
            failure_reason = 'process'
        except subprocess.TimeoutExpired as e:
            self._warning("task failed, timeout expired")
            self._process_failed = True
            failure_reason = 'timeout'
        except Exception as e:
            self._error("task failed (unexpected error)")
            self._process_failed = True
            failure_reason = 'generic'
        finally:
            success = self.running and not self._process_failed
            history.append(self.task_name, startup_time, success, trigger_name,
                           self._process_status, self._process_stdout,
                           self._process_stderr, failure_reason)
            if self._process_failed:
                applet.set_attention(True)
                applet.notify(resources.NOTIFY_TASK_FAILED % self.task_name)
            else:
                self._info("task successfully finished")
            if self.running:
                applet_lock.acquire()
                self.running = False
                applet_lock.release()
            to_report = bool(
                self.failure_status is not None or
                self.failure_stderr is not None or
                self.failure_stdout is not None or
                self.success_status is not None or
                self.success_stderr is not None or
                self.success_stdout is not None
            )
            if to_report:
                return success
            else:
                return None


# these functions convert a Task instance to a dictionary and back
def Task_to_dict(t):
    applet_log.info("MAIN: trying to dump task %s" % t.task_name)
    d = {}
    d['type'] = 'task'
    d['task_id'] = t.task_id
    d['task_name'] = t.task_name
    d['environment_vars'] = t.environment_vars
    d['include_env'] = t.include_env
    d['success_stdout'] = t.success_stdout
    d['success_stderr'] = t.success_stderr
    d['success_status'] = t.success_status
    d['failure_stdout'] = t.failure_stdout
    d['failure_stderr'] = t.failure_stderr
    d['failure_status'] = t.failure_status
    d['match_exact'] = t.match_exact
    d['case_sensitive'] = t.case_sensitive
    d['command'] = t.command
    d['startup_dir'] = t.startup_dir
    d['match_regexp'] = t.match_regexp
    applet_log.debug("MAIN: task %s dumped" % t.task_name)
    return d


def dict_to_Task(d):
    if d['type'] != 'task':
        raise ValueError("incorrect dictionary type")
    t = Task()
    applet_log.debug("MAIN: trying to load task %s" % d['task_name'])
    t.task_id = d['task_id']
    t.task_name = d['task_name']
    t.environment_vars = d['environment_vars']
    t.include_env = d['include_env']
    t.success_stdout = d['success_stdout']
    t.success_stderr = d['success_stderr']
    t.success_status = d['success_status']
    t.failure_stdout = d['failure_stdout']
    t.failure_stderr = d['failure_stderr']
    t.failure_status = d['failure_status']
    t.match_exact = d['match_exact']
    t.case_sensitive = d['case_sensitive']
    t.command = d['command']
    t.startup_dir = d['startup_dir']
    # TODO: if there are more parameters, use d.get('key', default_val)
    t.match_regexp = d.get('match_regexp', False)
    applet_log.info("MAIN: task %s loaded" % t.task_name)
    return t


#############################################################################
# The main condition class, with test verification functions: conditions are
# scanned at each clock tick in parallel, and if a condition finds that the
# time to actually test itself it performs the test and possibly runs all the
# associated tasks. The condition logic is provided by the (abstract) base
# class, and all the particular condition types must be derived from it
class Condition(object):

    def _check_condition(self):
        self._critical("NTBS: checking base condition")
        return False

    def _start_timer(self):
        self.startup_time = time.time()
        self.last_tested = self.startup_time

    _logger = logging.getLogger(APPLET_NAME)

    # make condition level logging easier
    def _debug(self, msg):
        self._logger.debug("COND: %s [%s]: %s" % (self.cond_name, self.cond_id, msg))

    def _info(self, msg):
        self._logger.info("COND: %s [%s]: %s" % (self.cond_name, self.cond_id, msg))

    def _warning(self, msg):
        self._logger.warning("COND: %s [%s]: %s" % (self.cond_name, self.cond_id, msg))

    def _error(self, msg):
        self._logger.error("COND: %s [%s]: %s" % (self.cond_name, self.cond_id, msg))

    def _critical(self, msg):
        self._logger.critical("COND: %s [%s]: %s" % (self.cond_name, self.cond_id, msg))

    def __init__(self, name=None, repeat=True, exec_sequence=True):
        self.cond_id = None
        self.cond_name = name
        self.last_tested = None
        self.last_succeeded = None
        self.skip_seconds = config.get('Scheduler', 'skip seconds')
        self.startup_time = None
        self.task_names = []
        self.repeat = True
        self.exec_sequence = True
        self.break_failure = False
        self.break_success = False
        self.suspended = False
        self._has_succeeded = False
        if self.__class__.__name__ == 'Condition':
            raise NotImplementedError("abstract class")
        if name is None:
            self._info("empty condition created")
        else:
            self.repeat = repeat
            self.exec_sequence = exec_sequence
            self.cond_id = conditions.get_id()
            self._info("condition created")
            self._start_timer()

    def add_task(self, task_name):
        self.task_names = [x for x in self.task_names if x != task_name]
        self.task_names.append(task_name)

    def delete_task(self, task_name):
        self.task_names = [x for x in self.task_names if x != task_name]

    def renew_id(self):
        self.cond_id = conditions.get_id()

    def dump(self):
        if self.cond_name is None:
            raise RuntimeError("condition not initialized")
        file_name = os.path.join(USER_CONFIG_FOLDER, '%s.cond' % self.cond_name)
        with open(file_name, 'wb') as f:
            pickle.dump(self, f)

    def unlink_file(self):
        file_name = os.path.join(USER_CONFIG_FOLDER, '%s.cond' % self.cond_name)
        if os.path.exists(file_name):
            os.unlink(file_name)

    @staticmethod
    def restore(name):
        file_name = os.path.join(USER_CONFIG_FOLDER, '%s.cond' % name)
        with open(file_name, 'rb') as f:
            o = pickle.load(f)
            o.renew_id()
            return o

    def reset(self):
        self.last_tested = None
        self.last_succeeded = None
        self._has_succeeded = False

    def suspend(self):
        self.suspended = True

    def resume(self):
        self.suspended = False

    def test(self):
        if self.cond_name is None:
            raise RuntimeError("condition not initialized")
        if self.suspended:
            self._info("check skipped (suspended condition)")
            return False
        elif not self.repeat and self._has_succeeded:
            self._info("check skipped (non-repeating condition)")
            return False
        else:
            self._debug("check or skip condition test")
            t = time.time()
            if not self.last_tested:
                self.last_tested = t
            delta_t = round(t - self.last_tested, 3)
            self._debug("verifying check time (%s >= %s)" % (delta_t, self.skip_seconds))
            if delta_t >= self.skip_seconds:
                self.last_tested = t
                if self._check_condition():
                    self.last_succeeded = t
                    self._has_succeeded = True
                    self._info("check successful")
                    return True
                else:
                    self._info("check failed")
            else:
                self._info("check skipped")
        return False

    def verified(self):
        if self.last_succeeded:
            rv = bool(self.last_tested == self.last_succeeded)
        else:
            rv = False
        self.last_succeeded = None
        return rv

    def tick(self):
        self.test()
        if self.verified():
            if self.exec_sequence:
                for task_name in self.task_names:
                    task = tasks.get(task_name=task_name)
                    if task:
                        self._info("sequential run of task %s" % task_name)
                        outcome = task.run(self.cond_name)
                        if outcome is not None:
                            if outcome and self.break_success:
                                self._info("breaking on task %s success" % task_name)
                                break
                            elif not outcome and self.break_failure:
                                self._info("breaking on task %s failure" % task_name)
                                break
                    else:
                        self._warning("task not found: %s" % task_name)
            else:
                localtasks = []
                foundnames = []
                for task_name in self.task_names:
                    task = tasks.get(task_name=task_name)
                    if task:
                        localtasks.append(task)
                        foundnames.append(task_name)
                    else:
                        self._warning("task not found: %s" % task_name)
                self._info("parallel run of tasks %s" % ", ".join(foundnames))
                with ThreadPoolExecutor(config.get('Concurrency', 'max threads')) as e:
                    e.map(lambda task: task.run(self.cond_name), localtasks)


# convert a condition to a dictionary and back
def Condition_to_dict(c):
    d = {}
    d['type'] = 'condition'
    d['subtype'] = None
    d['cond_id'] = c.cond_id
    d['cond_name'] = c.cond_name
    d['task_names'] = c.task_names
    d['repeat'] = c.repeat
    d['exec_sequence'] = c.exec_sequence
    d['suspended'] = c.suspended
    d['break_failure'] = c.break_failure
    d['break_success'] = c.break_success
    applet_log.debug("MAIN: condition %s dumped" % c.cond_name)
    return d


def dict_to_Condition(d, c=None):
    if d['type'] != 'condition':
        raise ValueError("incorrect dictionary type")
    # this will raise an error
    if c is None:
        applet_log.critical("MAIN: NTBS: attempt to load base Condition")
        c = Condition()
    applet_log.debug("MAIN: trying to load condition %s" % c.cond_name)
    c.cond_id = d['cond_id']
    c.cond_name = d['cond_name']
    c.task_names = d['task_names']
    c.repeat = d['repeat']
    c.exec_sequence = d['exec_sequence']
    c.suspended = d['suspended']
    # TODO: if there are more parameters, use d.get('key', default_val)
    c.break_failure = d.get('break_failure', False)
    c.break_success = d.get('break_success', False)
    return c


class IntervalBasedCondition(Condition):

    def _check_condition(self):
        self._debug("checking interval based condition")
        if self.interval:
            t = time.time()
            if self.interval <= round(t - self.checked):
                self.checked = t
                return True
        return False

    def __init__(self, name, interval, repeat=True, exec_sequence=True):
        self.interval = interval
        self.checked = time.time()
        Condition.__init__(self, name, repeat, exec_sequence)
        self.skip_seconds = 0


def IntervalBasedCondition_to_dict(c):
    applet_log.info("MAIN: dump interval based condition %s" % c.cond_name)
    d = Condition_to_dict(c)
    d['subtype'] = 'IntervalBasedCondition'
    d['interval'] = c.interval
    return d


def dict_to_IntervalBasedCondition(d):
    if d['type'] != 'condition' or d['subtype'] != 'IntervalBasedCondition':
        raise ValueError("incorrect dictionary type")
    name = d['cond_name']
    interval = d['interval']
    # TODO: if there are more parameters, use d.get('key', default_val)
    c = IntervalBasedCondition(name, interval)
    c = dict_to_Condition(d, c)
    applet_log.info("MAIN: loaded interval based condition %s" % c.cond_name)
    return c


class TimeBasedCondition(Condition):

    def _check_condition(self):
        self._debug("checking time based condition")
        cur_time = time.time()
        now = time.localtime(cur_time)
        test_tuple = (
            self.year or now[0],
            self.month or now[1],
            self.day or now[2],
            self.hour or now[3],
            self.minute or now[4],
            0,
            now[6],
            self.weekday or now[6],
            now[8],
        )
        test_time = time.mktime(test_tuple)
        span = max(self.tick_seconds, self.skip_seconds)
        self._debug("checking %.3f - %.3f (=%.3f) in [0-%s]" % (cur_time, test_time, cur_time - test_time, span))
        if 0 < cur_time - test_time <= span:
            return True
        else:
            return False

    def __init__(self, name, timedict, repeat=True, exec_sequence=True):
        if not timedict:
            raise ValueError("time specification must be given")
        self.year = None if 'year' not in timedict.keys() else timedict['year']
        self.month = None if 'month' not in timedict.keys() else timedict['month']
        self.day = None if 'day' not in timedict.keys() else timedict['day']
        self.hour = None if 'hour' not in timedict.keys() else timedict['hour']
        self.minute = None if 'minute' not in timedict.keys() else timedict['minute']
        self.weekday = None if 'weekday' not in timedict.keys() else timedict['weekday']
        self.tick_seconds = config.get('Scheduler', 'tick seconds')
        Condition.__init__(self, name, repeat, exec_sequence)
        self.skip_seconds = 0


def TimeBasedCondition_to_dict(c):
    applet_log.info("MAIN: dump time based condition %s" % c.cond_name)
    d = Condition_to_dict(c)
    d['subtype'] = 'TimeBasedCondition'
    d['year'] = c.year
    d['month'] = c.month
    d['day'] = c.day
    d['hour'] = c.hour
    d['minute'] = c.minute
    d['weekday'] = c.weekday
    return d


def dict_to_TimeBasedCondition(d):
    if d['type'] != 'condition' or d['subtype'] != 'TimeBasedCondition':
        raise ValueError("incorrect dictionary type")
    name = d['cond_name']
    # we can use d for timedict because the needed keys (intentionally) match
    # TODO: if there are more parameters, use d.get('key', default_val)
    c = TimeBasedCondition(name, d)
    c = dict_to_Condition(d, c)
    applet_log.info("MAIN: loaded time based condition %s" % c.cond_name)
    return c


class CommandBasedCondition(Condition):

    def _check_condition(self):
        self._debug("checking command based condition")
        try:
            self._debug("spawning test subprocess: %s" % self.command)
            if config.get('General', 'environment vars'):
                env = os.environ.copy()
                env[ENVVAR_NAME_COND] = self.cond_name
            else:
                env = None
            with subprocess.Popen(self.command,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell=True,
                                  env=env) as proc:
                stdout, stderr = proc.communicate()
                if self.expected_status is not None:
                    self._info("checking condition command exit status")
                    self._debug("test: %s == %s" % (proc.returncode, self.expected_status))
                    if int(proc.returncode) == self.expected_status:
                        return True
                elif self.expected_stdout:
                    self._info("checking condition command output")
                    expected = self.expected_stdout
                    returned = stdout.decode().strip()
                    if self.match_regexp:
                        if self.case_sensitive:
                            flags = 0
                        else:
                            flags = re.IGNORECASE
                        self._debug("test: '%s' ~ '%s'%s" % (returned, expected, ' (I)' if flags else ''))
                        try:
                            if self.match_exact:
                                if re.match(expected, returned, flags) is not None:
                                    return True
                            else:
                                if re.search(expected, returned, flags) is not None:
                                    return True
                        except:
                            self._warning("invalid regular expression (skipped)")
                    else:
                        if not self.case_sensitive:
                            expected = expected.upper()
                            returned = returned.upper()
                        if self.match_exact:
                            self._debug("test: '%s' == '%s'" % (expected, returned))
                            if expected == returned:
                                return True
                        else:
                            self._debug("test: '%s' in '%s'" % (expected, returned))
                            if expected in returned:
                                return True
                elif self.expected_stderr:
                    self._info("checking condition command error output")
                    expected = self.expected_stderr
                    returned = stderr.decode().strip()
                    if self.match_regexp:
                        if self.case_sensitive:
                            flags = 0
                        else:
                            flags = re.IGNORECASE
                        self._debug("test: '%s' ~ '%s'%s" % (returned, expected, ' (I)' if flags else ''))
                        try:
                            if self.match_exact:
                                if re.match(expected, returned, flags) is not None:
                                    return True
                            else:
                                if re.search(expected, returned, flags) is not None:
                                    return True
                        except:
                            self._warning("invalid regular expression (skipped)")
                    else:
                        if not self.case_sensitive:
                            expected = expected.upper()
                            returned = returned.upper()
                        if self.match_exact:
                            self._debug("test: '%s' == '%s'" % (expected, returned))
                            if expected == returned:
                                return True
                        else:
                            self._debug("test: '%s' in '%s'" % (expected, returned))
                            if expected in returned:
                                return True
                self._debug("test failed")
                return False
        except OSError as e:
            self._warning("condition failed, system error: %s" % _x(e))
            return False
        except subprocess.CalledProcessError as e:
            self._warning("condition failed, called process error")
            return False
        except subprocess.TimeoutExpired as e:
            self._warning("condition failed, timeout expired")
            return False
        except Exception as e:
            self._error("condition failed (unexpected error: %s)" % _x(e))
            return False

    def __init__(self, name, command, status=None, stdout=None, stderr=None, repeat=True, exec_sequence=True):
        self.match_exact = False
        self.match_regexp = False
        self.case_sensitive = False
        check_count = 0
        if status is not None:
            check_count += 1
        if stdout is not None:
            check_count += 1
        if stderr is not None:
            check_count += 1
        if check_count != 1:
            raise ValueError("only one of status, stdout, stderr should be set")
        self.command = command
        self.expected_status = status
        self.expected_stdout = stdout
        self.expected_stderr = stderr
        self.last_tick = time.time()
        Condition.__init__(self, name, repeat, exec_sequence)


def CommandBasedCondition_to_dict(c):
    applet_log.info("MAIN: dump command based condition %s" % c.cond_name)
    d = Condition_to_dict(c)
    d['subtype'] = 'CommandBasedCondition'
    d['match_exact'] = c.match_exact
    d['match_regexp'] = c.match_regexp
    d['case_sensitive'] = c.case_sensitive
    d['command'] = c.command
    d['expected_status'] = c.expected_status
    d['expected_stdout'] = c.expected_stdout
    d['expected_stderr'] = c.expected_stderr
    return d


def dict_to_CommandBasedCondition(d):
    if d['type'] != 'condition' or d['subtype'] != 'CommandBasedCondition':
        raise ValueError("incorrect dictionary type")
    name = d['cond_name']
    command = d['command']
    status = d['expected_status']
    stdout = d['expected_stdout']
    stderr = d['expected_stderr']
    match_exact = d['match_exact']
    case_sensitive = d['case_sensitive']
    # TODO: if there are more parameters, use d.get('key', default_val)
    match_regexp = d.get('match_regexp', False)
    c = CommandBasedCondition(name, command, status, stdout, stderr)
    c.match_exact = match_exact
    c.match_regexp = match_regexp
    c.case_sensitive = case_sensitive
    c = dict_to_Condition(d, c)
    applet_log.info("MAIN: loaded command based condition %s" % c.cond_name)
    return c


# this version should use DBus and the screensaver manager to determine
# idle time, but it segfaults when the condition is verified
# class IdleTimeBasedCondition(Condition):
class IdleTimeBasedCondition(CommandBasedCondition):

    def _check_condition(self):
        if self.idle_reset:
            # if get_applet_idle_seconds() >= idle_secs:
            if CommandBasedCondition._check_condition(self):
                self.idle_reset = False
                return True
            else:
                self.idle_reset = True
                return False
        else:
            # if get_applet_idle_seconds() < idle_secs:
            if not CommandBasedCondition._check_condition(self):
                self.idle_reset = True
            return False

    def __init__(self, name, idle_secs, repeat=True, exec_sequence=True):
        self.idle_secs = idle_secs
        self.idle_reset = True
        command = """test $(xprintidle) -gt %s""" % (idle_secs * 1000)
        # Condition.__init__(self, name, repeat, exec_sequence)
        CommandBasedCondition.__init__(
            self, name, command, status=0, repeat=repeat,
            exec_sequence=exec_sequence)


def IdleTimeBasedCondition_to_dict(c):
    applet_log.info("MAIN: dump idle time based condition %s" % c.cond_name)
    d = Condition_to_dict(c)
    d['subtype'] = 'IdleTimeBasedCondition'
    d['idle_secs'] = c.idle_secs
    return d


def dict_to_IdleTimeBasedCondition(d):
    if d['type'] != 'condition' or d['subtype'] != 'IdleTimeBasedCondition':
        raise ValueError("incorrect dictionary type")
    name = d['cond_name']
    idle_secs = d['idle_secs']
    # TODO: if there are more parameters, use d.get('key', default_val)
    c = IdleTimeBasedCondition(name, idle_secs)
    c = dict_to_Condition(d, c)
    applet_log.info("MAIN: loaded idle time based condition %s" % c.cond_name)
    return c


# current_system_event is for events that are not queued and are directly
# triggered by something external (e.g. startup, shutdown, other signals),
# while current_deferred_events is a copy of the events that have been
# more gently enqueued by other triggers (e.g. via DBus or services)
class EventBasedCondition(Condition):

    def _check_condition(self):
        self._debug("checking event based condition: %s" % self.event)
        if current_system_event and self.event == current_system_event:
            return True
        elif current_deferred_events and self.event in current_deferred_events:
            return True
        else:
            return False

    def __init__(self, name, event, no_skip=True, repeat=False, exec_sequence=True):
        self.event = event
        Condition.__init__(self, name, repeat, exec_sequence)
        if no_skip:
            self.skip_seconds = 0


def EventBasedCondition_to_dict(c):
    applet_log.info("MAIN: dump event based condition %s" % c.cond_name)
    d = Condition_to_dict(c)
    d['subtype'] = 'EventBasedCondition'
    d['event'] = c.event
    d['no_skip'] = bool(c.skip_seconds == 0)
    return d


def dict_to_EventBasedCondition(d):
    if d['type'] != 'condition' or d['subtype'] != 'EventBasedCondition':
        raise ValueError("incorrect dictionary type")
    name = d['cond_name']
    event = d['event']
    no_skip = d['no_skip']
    # TODO: if there are more parameters, use d.get('key', default_val)
    c = EventBasedCondition(name, event, no_skip)
    c = dict_to_Condition(d, c)
    applet_log.info("MAIN: loaded event based condition %s" % c.cond_name)
    return c


# the file notification condition only fires when currently notified file list
# contains one or more of the files watched by the condition itself: the
# mechanism is similar to the one of EventBasedCondition and implemented via
# a parallel system
class PathNotifyBasedCondition(Condition):

    def _check_condition(self):
        if not self._active:
            return False
        # the following test is equivalent to checking whether notifications
        # are enabled or not, and maybe faster than the full flag and config
        # test since it involves less function calls and comparisons
        if watch_path_manager is not None:
            self._debug("checking file change based condition for: %s" % ', '.join(self.watched_paths))
            if current_changed_path:
                try:
                    v = next(x for x in self.watched_paths
                             if current_changed_path.startswith(x))
                    return True
                except StopIteration:
                    pass
            elif current_deferred_changed_paths:
                for p in current_deferred_changed_paths:
                    try:
                        v = next(x for x in self.watched_paths if p.startswith(x))
                        return True
                    except StopIteration:
                        pass
            return False
        else:
            self._info("no check because file notifications are not enabled")
            return False

    def __init__(self, name, paths, no_skip=True, repeat=False, exec_sequence=True):
        self._wdd = None
        self._active = False
        self.watched_paths = paths
        Condition.__init__(self, name, repeat, exec_sequence)
        if no_skip:
            self.skip_seconds = 0

    def activate(self):
        if watch_path_manager is None:
            self._warning("file notifications not enabled, cannot activate")
            return
        if not self._active:
            applet_lock.acquire()
            self._wdd = watch_path_manager.add_watch(
                self.watched_paths, mask=FN_IN_MODIFY_EVENTS, rec=True)
            applet_lock.release()
            self._active = True
            self._debug("watching filesystem: %s" % ', '.join(self.watched_paths))

    def deactivate(self):
        if watch_path_manager is None:
            self._debug("file notifications not enabled, cannot deactivate")
            return
        if self._active:
            self._debug("removing all watches")
            # explicit conversion to list as pyinotify does strict checking
            applet_lock.acquire()
            watch_path_manager.rm_watch(list(self._wdd.values()))
            applet_lock.release()
            self._warning = False
            self._wdd = None

    # do not save activity state or it might not be activated on restore
    def dump(self):
        save_active = self._active
        save_wdd = self._wdd
        self._active = False
        self._wdd = None
        Condition.dump(self)
        self._wdd = save_wdd
        self._active = save_active


def PathNotifyBasedCondition_to_dict(c):
    applet_log.info("MAIN: dump file change based condition %s" % c.cond_name)
    d = Condition_to_dict(c)
    d['subtype'] = 'PathNotifyBasedCondition'
    d['watched_paths'] = c.watched_paths
    d['no_skip'] = bool(c.skip_seconds == 0)
    return d


def dict_to_PathNotifyBasedCondition(d):
    if d['type'] != 'condition' or d['subtype'] != 'PathNotifyBasedCondition':
        raise ValueError("incorrect dictionary type")
    name = d['cond_name']
    event = d['watched_paths']
    no_skip = d['no_skip']
    # TODO: if there are more parameters, use d.get('key', default_val)
    c = PathNotifyBasedCondition(name, event, no_skip)
    c = dict_to_Condition(d, c)
    applet_log.info("MAIN: loaded file change based condition %s" % c.cond_name)
    return c


#############################################################################
# abstract class for conditions based on generically collected data: derived
# implementations should override data_collector and check_data; a failure
# in data_collector prevents condition trigger anyway, while success allows
# check_data to decide whether to trigger or not depending on retrieved data
class DataCollectorBasedCondition(Condition):

    def _check_condition(self):
        self._debug("checking data collector based condition")
        try:
            current_data = self.data_collector()
            rv = self.check_data(current_data)
            self.data = current_data
            return bool(rv)
        except Exception as e:
            self._debug("error %s checking data collector based condition %s" % (e, self.cond_name))
            return False

    def __init__(self, name=None, no_skip=False, repeat=True, exec_sequence=True):
        if self.__class__.__name__ == 'DataCollectorBasedCondition':
            raise NotImplementedError("abstract class")
        Condition.__init__(self, name, repeat, exec_sequence)
        if no_skip:
            self.skip_seconds = 0

    # this virtual function should collect data somehow and return it
    def data_collector(self):
        return None

    # this virtual function should verify submitted data and return a
    # boolean, possibly comparing it with already stored data
    def check_data(self, collected):
        return False


def DataCollectorBasedCondition_to_dict(c):
    d = Condition_to_dict(c)
    d['subtype'] = 'DataCollectorBasedCondition'
    d['no_skip'] = bool(c.skip_seconds == 0)
    return d


def dict_to_DataCollectorBasedCondition(d, c=None):
    if d['type'] != 'condition' or d['subtype'] != 'DataCollectorBasedCondition':
        raise ValueError("incorrect dictionary type")
    name = d['cond_name']
    no_skip = d['no_skip']
    # TODO: if there are more parameters, use d.get('key', default_val)
    # the following will raise an error
    if c is None:
        applet_log.critical("MAIN: NTBS: attempt to load base DataCollectorBasedCondition")
        c = DataCollectorBasedCondition(name, no_skip)
    if no_skip:
        c.skip_seconds = 0
    c = dict_to_Condition(d, c)
    return c


#############################################################################
# a class to build DBus signal handlers: related conditions are event based
# conditions with a special event (dbus_signal:SigHandlerName) to reuse code
param_check = namedtuple('param_check', ['value_idx', 'sub_idx',
                                         'comparison', 'negate',
                                         'test_value'])


class SignalHandler(object):

    _logger = logging.getLogger(APPLET_NAME)

    # make task level logging easier
    def _debug(self, msg):
        self._logger.debug("DBUS: %s: %s" % (self.handler_name, msg))

    def _info(self, msg):
        self._logger.info("DBUS: %s: %s" % (self.handler_name, msg))

    def _warning(self, msg):
        self._logger.warning("DBUS: %s: %s" % (self.handler_name, msg))

    def _error(self, msg):
        self._logger.error("DBUS: %s: %s" % (self.handler_name, msg))

    def _critical(self, msg):
        self._logger.critical("DBUS: %s: %s" % (self.handler_name, msg))

    def __init__(self, name, bus=None, bus_name=None, bus_path=None, interface=None, signal=None):
        self.handler_name = name
        self.bus = bus
        self.bus_name = bus_name
        self.bus_path = bus_path
        self.interface = interface
        self.signal = signal
        self.signal_match = None
        self.param_checks = []
        self.verify_all_checks = False
        self.defer = True

    registered = property(lambda self: self.signal_match is not None)

    def add_check(self, value_idx, sub_idx, negate, comparison, test_value):
        t = param_check(
            value_idx,
            sub_idx,
            comparison,
            negate,
            test_value,
        )
        self.param_checks = list(
            x for x in self.param_checks
            if x.value_idx != value_idx and x.sub_idx != sub_idx)
        self.param_checks.append(t)

    def remove_check(self, value_idx, sub_idx):
        self.param_checks = list(
            x for x in self.param_checks
            if x.value_idx != value_idx and x.sub_idx != sub_idx)

    # this will be called by the actual handler with the actual arguments
    def signal_handler_helper(self, *args):

        # incomparable values or comparison errors return False by design
        def perform_check(c):
            index = c.value_idx
            sub = c.sub_idx
            test = c.test_value
            compare = c.comparison
            rv = None

            def warning(msg):
                self._warning("param %s: %s" % (index, msg))

            def error(msg):
                self._error("param %s: %s" % (index, msg))

            def bool_spec(v):
                if type(v) == str:
                    v = v.lower()
                    if v in ('true', 'yes', 'on', '1'):
                        return True
                    elif v in ('false', 'no', 'off', '0'):
                        return False
                    else:
                        return None
                else:
                    return bool(v)

            try:
                param = args[index]
            except Exception as e:
                error("cannot extract parameter (%s)" % _x(e))
                return False
            if sub is not None:
                if type(param) in (dbus.Array, dbus.Struct):
                    try:
                        sub = int(sub)
                    except Exception as e:
                        error("expected integer subindex (%s)" % _x(e))
                        return False
                    try:
                        param = param[sub]
                    except IndexError as e:
                        warning("subindex %s not in list" % sub)
                        return False
                elif type(param) == dbus.Dictionary:
                    try:
                        sub = dbus.String(sub)
                    except Exception as e:
                        error("expected string subindex (%s)" % _x(e))
                        return False
                    try:
                        param = param[sub]
                    except KeyError as e:
                        warning("subindex '%s' not in dictionary keys" % sub)
                        return False
                else:
                    error("cannot apply subindex to non-compound type")
                    return False
            # here param is already something that is not compound or, if it
            # actually is still compound, only accepts a 'contains' operator
            if type(param) == dbus.Boolean:
                if compare != DBUS_CHECK_COMPARE_IS:
                    error("boolean comparison requires equality test")
                    return False
                else:
                    param = bool(param)
                    test = bool_spec(test)
                    if test is None:
                        error("invalid value specified for boolean comparison")
                        return False
                    else:
                        rv = bool(param == test)
            elif type(param) in (dbus.Byte, dbus.Int16, dbus.Int32, dbus.Int64,
                                 dbus.UInt16, dbus.UInt32, dbus.UInt64):
                try:
                    param = int(param)
                    test = int(test)
                except Exception as e:
                    error("cannot convert either param or test value (%s)" % _x(e))
                    return False
                if compare == DBUS_CHECK_COMPARE_IS:
                    rv = bool(param == test)
                elif compare == DBUS_CHECK_COMPARE_GREATER:
                    rv = bool(param > test)
                elif compare == DBUS_CHECK_COMPARE_LESS:
                    rv = bool(param < test)
                else:
                    error("numeric comparison requires equality, greater or less")
                    return False
            elif type(param) == dbus.Double:
                try:
                    param = float(param)
                    test = float(test)
                except Exception as e:
                    error("cannot convert either param or test value (%s)" % _x(e))
                    return False
                if compare == DBUS_CHECK_COMPARE_IS:
                    rv = bool(param == test)
                elif compare == DBUS_CHECK_COMPARE_GREATER:
                    rv = bool(param > test)
                elif compare == DBUS_CHECK_COMPARE_LESS:
                    rv = bool(param < test)
                else:
                    error("numeric comparison requires equality, greater or less")
                    return False
            elif type(param) in (dbus.String,
                                 dbus.ObjectPath, dbus.Signature,
                                 dbus.ByteArray):
                try:
                    param = str(param)
                    test = str(test)
                except Exception as e:
                    error("cannot convert either param or test value (%s)" % _x(e))
                    return False
                if compare == DBUS_CHECK_COMPARE_IS:
                    rv = bool(param == test)
                elif compare == DBUS_CHECK_COMPARE_GREATER:
                    rv = bool(param > test)
                elif compare == DBUS_CHECK_COMPARE_LESS:
                    rv = bool(param < test)
                elif compare == DBUS_CHECK_COMPARE_CONTAINS:
                    rv = bool(test in param)
                elif compare == DBUS_CHECK_COMPARE_MATCHES:
                    if re.match(test, param):
                        rv = True
                    else:
                        rv = False
                else:
                    error("invalid operator for string comparison")
                    return False
            elif type(param) in (dbus.Array, dbus.Struct):
                if compare == DBUS_CHECK_COMPARE_CONTAINS:
                    for x in param:
                        if type(x) == dbus.Boolean:
                            x = bool(x)
                            test = bool_spec(test)
                            if test is not None:
                                rv = bool(x == test)
                        elif type(x) in (dbus.Byte, dbus.Int16, dbus.Int32,
                                         dbus.Int64, dbus.UInt16, dbus.UInt32,
                                         dbus.UInt64):
                            try:
                                x = int(x)
                                test = int(test)
                            except Exception as e:
                                continue
                            rv = bool(x == test)
                        elif type(x) == dbus.Double:
                            try:
                                x = float(x)
                                test = float(test)
                            except Exception as e:
                                continue
                            rv = bool(x == test)
                        elif type(x) in (dbus.String,
                                         dbus.ObjectPath, dbus.Signature,
                                         dbus.ByteArray):
                            try:
                                x = str(x)
                                test = str(test)
                            except Exception as e:
                                continue
                            rv = bool(x == test)
                        if rv:
                            break
                else:
                    error("comparison in compound types requires subindex or contains")
                    return False
            elif type(param) == dbus.Dictionary:
                if compare == DBUS_CHECK_COMPARE_CONTAINS:
                    for k in param.keys():
                        x = param[k]
                        if type(x) == dbus.Boolean:
                            x = bool(x)
                            test = bool_spec(test)
                            if test is not None:
                                rv = bool(x == test)
                        elif type(x) in (dbus.Byte, dbus.Int16, dbus.Int32,
                                         dbus.Int64, dbus.UInt16, dbus.UInt32,
                                         dbus.UInt64):
                            try:
                                x = int(x)
                                test = int(test)
                            except Exception as e:
                                continue
                            rv = bool(x == test)
                        elif type(x) == dbus.Double:
                            try:
                                x = float(x)
                                test = float(test)
                            except Exception as e:
                                continue
                            rv = bool(x == test)
                        elif type(x) in (dbus.String,
                                         dbus.ObjectPath, dbus.Signature,
                                         dbus.ByteArray):
                            try:
                                x = str(x)
                                test = str(test)
                            except Exception as e:
                                continue
                            rv = bool(x == test)
                        if rv:
                            break
                else:
                    error("comparison in compound types requires subindex or contains")
                    return False
            # there is no special handling of variant types, because the
            # new DBus interface automatically casts variants to their
            # actual type, just including the variant_level attribute
            else:
                error("unsupported data type for comparison")
                return False
            # at this point rv is either bool or None
            if rv is not None and c.negate:
                return not rv
            return rv

        # try to evaluate as shortcut as possible
        r = True
        for check in self.param_checks:
            r = perform_check(check)
            if r is None:
                self._warning("could not compare signal parameter")
                if self.verify_all_checks:
                    return False
                else:
                    r = False
            elif not r:
                if self.verify_all_checks:
                    return False
            else:
                if not self.verify_all_checks:
                    return True
        # the last evaluation is the one that yields, because if we are here
        # then none of the shortcut checks before has been encountered
        return r

    # the callback to be registered as a signal listener
    def signal_handler_callback(self, *args):
        signal_caught = False
        try:
            signal_caught = self.signal_handler_helper(*args)
        except Exception as e:
            self._error("exception %s raised by signal handler %s" % (e.__class__.__name__, self.handler_name))
            return
        if signal_caught:
            event_name = EVENT_DBUS_SIGNAL_PREAMBLE + ':' + self.handler_name
            self._info("DBus signal caught: raising event %s" % event_name)
            if self.defer:
                deferred_events.append(event_name)
            else:
                sysevent_condition_check(event_name)

    def register(self):
        try:
            if self.signal_match:
                self.signal_match.remove()
            self.signal_match = None
            if self.bus == 'session':
                bus = dbus.SessionBus()
            elif self.bus == 'system':
                bus = dbus.SystemBus()
            else:
                self._error("NTBS: invalid bus specification %s: not registering %s:%s handler" % (self.bus, self.interface, self.signal))
                return None
            proxy = bus.get_object(self.bus_name, self.bus_path)
            manager = dbus.Interface(proxy, self.interface)
            self.signal_match = manager.connect_to_signal(
                self.signal, self.signal_handler_callback)
            self._info("signal handler %s:%s correctly registered" % (self.interface, self.signal))
            return manager
        except dbus.exceptions.DBusException:
            self._warning("error registering %s:%s handler" % (self.interface, self.signal))
            return None

    def unregister(self):
        # the signal matcher has the ability to kill itself, as per source code
        # (see: http://dbus.freedesktop.org/doc/dbus-python/api/dbus.connection-pysrc.html#SignalMatch.remove)
        try:
            if self.signal_match:
                self.signal_match.remove()
            self.signal_match = None
            return True
        except Exception as e:
            self._warning("could not unregister handler (%s)" % _x(e))
            return False

    def dump(self):
        if self.handler_name is None:
            raise RuntimeError("signal handler not initialized")
        file_name = os.path.join(USER_CONFIG_FOLDER, '%s.handler' % self.handler_name)
        # self.signal_match is session dependent (and a weakref): don't dump
        m = self.signal_match
        self.signal_match = None
        with open(file_name, 'wb') as f:
            pickle.dump(self, f)
        self.signal_match = m

    def unlink_file(self):
        file_name = os.path.join(USER_CONFIG_FOLDER, '%s.handler' % self.handler_name)
        if os.path.exists(file_name):
            os.unlink(file_name)

    @staticmethod
    def restore(name):
        file_name = os.path.join(USER_CONFIG_FOLDER, '%s.handler' % name)
        with open(file_name, 'rb') as f:
            o = pickle.load(f)
            return o


def SignalHandler_to_dict(h):
    applet_log.info("MAIN: trying to dump DBus signal handler %s" % h.handler_name)
    d = {}
    d['type'] = 'dbus_signal_handler'
    d['handler_name'] = h.handler_name
    d['bus'] = h.bus
    d['bus_name'] = h.bus_name
    d['bus_path'] = h.bus_path
    d['interface'] = h.interface
    d['signal'] = h.signal
    d['param_checks'] = h.param_checks
    d['verify_all_checks'] = h.verify_all_checks
    d['defer'] = h.defer
    applet_log.debug("MAIN: DBus signal handler %s dumped" % h.handler_name)
    return d


def dict_to_SignalHandler(d):
    if d['type'] != 'dbus_signal_handler':
        raise ValueError("incorrect dictionary type")
    applet_log.debug("MAIN: trying to load DBus signal handler %s" % d['handler_name'])
    h = SignalHandler(d['handler_name'])
    h.bus = d['bus']
    h.bus_name = d['bus_name']
    h.bus_path = d['bus_path']
    h.interface = d['interface']
    h.signal = d['signal']
    # too bad I used named tuples: they are not well JSONified
    param_checks = d['param_checks']
    h.param_checks = []
    for p in param_checks:
        t = param_check(p[0], p[1], p[2], p[3], p[4])
        h.param_checks.append(t)
    h.verify_all_checks = d['verify_all_checks']
    h.defer = d['defer']
    # TODO: if there are more parameters, use d.get('key', default_val)
    applet_log.info("MAIN: DBus signal handler %s loaded" % h.handler_name)
    return h


#############################################################################
# dialog boxes and windows

# This dialog box is populated by loading a dummy task from a file, when the
# task is edited it goes directly to the loaded file (if existing or a new one
# otherwise) and is listed or replaced in the current task list.
class TaskDialog(object):

    def __init__(self):
        self.builder = Gtk.Builder().new_from_string(ui_add_task, -1)
        self.builder.connect_signals(self)
        self.builder.set_translation_domain(APPLET_NAME)
        o = self.builder.get_object
        self.dialog = o('dlgAddTask')
        self.stored_tasks = tasks.names
        self.stored_tasks.sort()
        cb_tasks = o('cbTaskName')
        for x in self.stored_tasks:
            cb_tasks.append_text(x)
        l = o('listEnvVars')
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_ENVVARS_NAME, Gtk.CellRendererText(), text=0)
        l.append_column(c)
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_ENVVARS_VALUE, Gtk.CellRendererText(), text=1)
        l.append_column(c)

    def validate_int(self, s, min_value=None, max_value=None):
        try:
            n = int(s)
            if min_value is not None and n < min_value:
                return None
            elif max_value is not None and n > max_value:
                return None
            else:
                return n
        except ValueError as e:
            return None

    def click_btnVarAdd(self, _):
        o = self.builder.get_object
        name = o('txtVarName').get_text()
        value = o('txtVarValue').get_text()
        m = o('store_listEnvVars')
        li = []
        updated = False
        for row in m:
            if name == row[0]:
                updated = True
                li.append([name, value])
            else:
                li.append([row[0], row[1]])
        if not updated:
            li.append([name, value])
        li.sort()
        m.clear()
        for i in li:
            m.append(i)

    def click_btnVarRemove(self, _):
        o = self.builder.get_object
        name = o('txtVarName').get_text()
        m = o('store_listEnvVars')
        li = []
        for row in m:
            if name != row[0]:
                li.append([row[0], row[1]])
        li.sort()
        m.clear()
        for i in li:
            m.append(i)

    def click_listEnvVars(self, selected):
        o = self.builder.get_object
        m, i = selected.get_selected()
        if i is not None:
            o('txtVarName').set_text(m[i][0])
            o('txtVarValue').set_text(m[i][1])

    def click_btnChooseDir(self, _):
        o = self.builder.get_object
        curpath = o('txtFolder').get_text()
        dirdlg = Gtk.FileChooserDialog(title=resources.DLG_TITLE_CHOOSE_DIR,
                                       action=Gtk.FileChooserAction.SELECT_FOLDER,
                                       buttons=(Gtk.STOCK_CANCEL,
                                                Gtk.ResponseType.CANCEL,
                                                Gtk.STOCK_OK,
                                                Gtk.ResponseType.OK))
        if os.path.exists(curpath) and os.path.isdir(curpath):
            dirdlg.set_filename(curpath)
        ret = dirdlg.run()
        dirdlg.hide()
        if ret == Gtk.ResponseType.OK:
            o('txtFolder').set_text(dirdlg.get_filename())

    def choose_task(self, box):
        o = self.builder.get_object
        self.default_box()
        name = box.get_active_text()
        if name in self.stored_tasks:
            task = tasks.get(task_name=name)
            o('txtVarName').set_text('')
            o('txtVarValue').set_text('')
            o('txtCommand').set_text(task.command)
            o('txtFolder').set_text(task.startup_dir)
            if task.success_status is not None:
                o('rdSuccess').set_active(True)
                o('cbCheckWhat').set_active(0)
                o('txtCheckValue').set_text(str(task.success_status))
            elif task.success_stdout is not None:
                o('rdSuccess').set_active(True)
                o('cbCheckWhat').set_active(1)
                o('txtCheckValue').set_text(task.success_stdout)
            elif task.success_stderr is not None:
                o('rdSuccess').set_active(True)
                o('cbCheckWhat').set_active(2)
                o('txtCheckValue').set_text(task.success_stderr)
            elif task.failure_status is not None:
                o('rdFailure').set_active(True)
                o('cbCheckWhat').set_active(0)
                o('txtCheckValue').set_text(str(task.failure_status))
            elif task.failure_stdout is not None:
                o('rdFailure').set_active(True)
                o('cbCheckWhat').set_active(1)
                o('txtCheckValue').set_text(task.failure_stdout)
            elif task.failure_stderr is not None:
                o('rdFailure').set_active(True)
                o('cbCheckWhat').set_active(2)
                o('txtCheckValue').set_text(task.failure_stderr)
            else:
                o('rdNoCheck').set_active(True)
                o('txtCheckValue').set_text("0")
            o('chkExactMatch').set_active(task.match_exact)
            o('chkRegExp').set_active(task.match_regexp)
            o('chkCaseSensitive').set_active(task.case_sensitive)
            o('chkImportEnvironment').set_active(task.include_env)
            m = o('store_listEnvVars')
            li = []
            e = task.environment_vars
            for k in e.keys():
                li.append([k, e[k]])
            li.sort()
            m.clear()
            for i in li:
                m.append(i)

    def change_txtName(self, _):
        o = self.builder.get_object
        name = o('txtName').get_text()
        if VALIDATE_TASK_RE.match(name):
            o('buttonOK').set_sensitive(True)
            if name in self.stored_tasks:
                o('btnDelete').set_sensitive(True)
            else:
                o('btnDelete').set_sensitive(False)
        else:
            o('buttonOK').set_sensitive(False)
            o('btnDelete').set_sensitive(False)

    def change_cbCheckWhat(self, _):
        o = self.builder.get_object
        if o('cbCheckWhat').get_active() == 0:
            o('chkExactMatch').set_sensitive(False)
            o('chkCaseSensitive').set_sensitive(False)
            o('chkRegExp').set_sensitive(False)
        else:
            o('chkExactMatch').set_sensitive(True)
            o('chkCaseSensitive').set_sensitive(True)
            o('chkRegExp').set_sensitive(True)

    def default_box(self, include_name=False):
        o = self.builder.get_object
        if include_name:
            o('txtName').set_text('')
        o('txtVarName').set_text('')
        o('txtVarValue').set_text('')
        o('txtCommand').set_text('')
        o('txtFolder').set_text('')
        o('chkExactMatch').set_active(False)
        o('chkCaseSensitive').set_active(False)
        o('chkRegExp').set_active(False)
        o('chkImportEnvironment').set_active(True)
        o('rdSuccess').set_active(True)
        o('cbCheckWhat').set_active(0)
        o('txtCheckValue').set_text("0")
        o('store_listEnvVars').clear()

    def run(self):
        o = self.builder.get_object
        self.default_box(True)
        self.stored_tasks = tasks.names
        self.stored_tasks.sort()
        cb_tasks = o('cbTaskName')
        cb_tasks.get_model().clear()
        for x in self.stored_tasks:
            cb_tasks.append_text(x)
        self.dialog.set_keep_above(True)
        self.dialog.present()
        self.change_txtName(None)
        self.change_cbCheckWhat(None)
        ret = self.dialog.run()
        self.dialog.hide()
        self.dialog.set_keep_above(False)
        if ret == ACTION_OK:
            name = o('txtName').get_text()
            command = o('txtCommand').get_text()
            startup_dir = o('txtFolder').get_text()
            task = Task(name, command, startup_dir)
            idx = o('cbCheckWhat').get_active()
            if o('rdSuccess').get_active():
                if idx == 0:
                    s = self.validate_int(o('txtCheckValue').get_text(), 0)
                    if s is None:
                        msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                                   buttons=Gtk.ButtonsType.OK)
                        msgbox.set_markup(resources.DLG_WRONG_EXIT_STATUS)
                        msgbox.run()
                        msgbox.hide()
                        applet_log.warning("DLGTASK: wrong exit code specification")
                        s = 0
                    task.set_check(success_status=s)
                elif idx == 1:
                    s = str(o('txtCheckValue').get_text())
                    task.set_check(success_stdout=s)
                elif idx == 2:
                    s = str(o('txtCheckValue').get_text())
                    task.set_check(success_stderr=s)
            elif o('rdFailure').get_active():
                if idx == 0:
                    s = self.validate_int(o('txtCheckValue').get_text(), 0)
                    if s is None:
                        msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                                   buttons=Gtk.ButtonsType.OK)
                        msgbox.set_markup(resources.DLG_WRONG_EXIT_STATUS)
                        msgbox.run()
                        msgbox.hide()
                        s = 0
                    task.set_check(failure_status=s)
                elif idx == 1:
                    s = str(o('txtCheckValue').get_text())
                    task.set_check(failure_stdout=s)
                elif idx == 2:
                    s = str(o('txtCheckValue').get_text())
                    task.set_check(failure_stderr=s)
            m = o('store_listEnvVars')
            for row in m:
                task.set_env(row[0], row[1])
            task.match_exact = o('chkExactMatch').get_active()
            task.match_regexp = o('chkRegExp').get_active()
            task.case_sensitive = o('chkCaseSensitive').get_active()
            task.include_env = o('chkImportEnvironment').get_active()
            task.dump()
            tasks.add(task)
            tasks.save()
            return task
        elif ret == ACTION_DELETE:
            name = o('txtName').get_text()
            task = tasks.get(task_name=name)
            if task:
                msgbox = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,
                                           buttons=Gtk.ButtonsType.YES_NO)
                msgbox.set_markup(resources.DLG_CONFIRM_DELETE_TASK % name)
                ret = msgbox.run()
                msgbox.hide()
                if ret == Gtk.ResponseType.YES:
                    self.default_box(True)
                    if tasks.remove(task_name=name):
                        tasks.save()
                    else:
                        applet_log.error("DLGTASK: task %s could not be deleted" % name)
                        msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                                   buttons=Gtk.ButtonsType.OK)
                        msgbox.set_markup(
                            resources.DLG_CANNOT_DELETE_TASK % name)
                        msgbox.run()
                        msgbox.hide()
                else:
                    applet_log.info("DLGTASK: removal of task %s canceled" % name)
            else:
                applet_log.error("DLGTASK: task %s not found" % name)
                msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                           buttons=Gtk.ButtonsType.OK)
                msgbox.set_markup(resources.DLG_CANNOT_FIND_TASK % name)
                msgbox.run()
                msgbox.hide()
            return None
        else:
            return None


# This dialog box is populated by loading a dummy condition from a file, with
# a mechanism similar to the above one. The main difference is that this box
# should contain a dynamic part, since there are different condition types.
class ConditionDialog(object):

    def __init__(self):
        self.builder = Gtk.Builder().new_from_string(ui_add_condition, -1)
        self.builder.connect_signals(self)
        self.builder.set_translation_domain(APPLET_NAME)
        o = self.builder.get_object
        self.dialog = o('dlgAddCondition')
        self.stored_conditions = conditions.names
        self.stored_conditions.sort()
        cb_conds = o('cbConditionName')
        cb_conds.get_model().clear()
        for x in self.stored_conditions:
            cb_conds.append_text(x)
        self.stored_tasks = tasks.names
        self.stored_tasks.sort()
        cb_tasks = o('cbAddTask')
        cb_tasks.get_model().clear()
        for x in self.stored_tasks:
            cb_tasks.append_text(x)
        self.stored_handlers = signal_handlers.names
        self.stored_handlers.sort()
        cb_handlers = o('cbDBusEvent')
        for x in self.stored_handlers:
            cb_handlers.append_text(x)
        self.update_box_type(None)
        l = o('listTasks')
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_TASKS_NAME, Gtk.CellRendererText(), text=0)
        l.append_column(c)
        self.all_events = [
            EVENT_APPLET_STARTUP,
            EVENT_APPLET_SHUTDOWN,
            EVENT_SYSTEM_SUSPEND,
            EVENT_SYSTEM_RESUME,
            EVENT_SYSTEM_DEVICE_ATTACH,
            EVENT_SYSTEM_DEVICE_DETACH,
            EVENT_SYSTEM_NETWORK_JOIN,
            EVENT_SYSTEM_NETWORK_LEAVE,
            EVENT_SESSION_SCREENSAVER,
            EVENT_SESSION_SCREENSAVER_EXIT,
            EVENT_SESSION_LOCK,
            EVENT_SESSION_UNLOCK,
            EVENT_SYSTEM_BATTERY_CHARGE,
            EVENT_SYSTEM_BATTERY_DISCHARGING,
            EVENT_SYSTEM_BATTERY_LOW,

            # the following should be the last one
            EVENT_COMMAND_LINE
        ]
        if applet_enabled_events:
            enabled_events = applet_enabled_events
        else:
            enabled_events = []
        i = 0
        li = []
        model = o('cbSysEvent').get_model()
        for row in model:
            r, v = row[0], row[1]
            if self.all_events[i] not in enabled_events:
                r = "%s %s" % (r, resources.DLG_ITEM_DISABLED)
            li.append([r, v])
            i += 1
        model.clear()
        for x in li:
            model.append(x)
        o('cbSysEvent').set_model(model)

        # since the box was built using the Glade interface designer, for now
        # just add the extra condition if enabled: this forces the user to
        # restart the applet to actually enable DBus signal handlers in this
        # dialog box, but it's probably a good way to handle such a setting
        if config.get("General", "user events"):
            model = o("cbType").get_model()
            model.append(resources.CBENTRY_CONDITION_DBUS_EVENTS)
            o('cbType').set_model(model)

    def validate_int(self, s, min_value=None, max_value=None):
        try:
            n = int(s)
            if min_value is not None and n < min_value:
                return None
            elif max_value is not None and n > max_value:
                return None
            else:
                return n
        except ValueError as e:
            return None

    def click_btnAddTask(self, _):
        o = self.builder.get_object
        task_name = o('cbAddTask').get_active_text()
        if task_name:
            li = []
            m = o('store_listTasks')
            for row in m:
                r = row[0]
                if r != task_name:
                    li.append(r)
            li.append(task_name)
            m.clear()
            for x in li:
                m.append([x])

    def click_btnRemoveTask(self, _):
        o = self.builder.get_object
        task_name = o('cbAddTask').get_active_text()
        if task_name:
            li = []
            m = o('store_listTasks')
            for row in m:
                r = row[0]
                if r != task_name:
                    li.append(r)
            m.clear()
            for x in li:
                m.append([x])

    def click_listTasks(self, selected):
        o = self.builder.get_object
        m = o('cbAddTask').get_model()
        m1, i = selected.get_selected()
        if i is not None:
            idx = 0
            for row in m:
                if row[0] == m1[i][0]:
                    o('cbAddTask').set_active(idx)
                    break
                else:
                    idx += 1

    def update_box_type(self, _):
        o = self.builder.get_object
        idx = o('cbType').get_active()
        widgets = [
            'canvasOptions_Interval',
            'canvasOptions_Time',
            'canvasOptions_Command',
            'canvasOptions_IdleTime',
            'canvasOptions_SysEvent',
            'canvasOptions_FileWatch',
            'canvasOptions_DBusEvent',
            'canvasOptions_Empty',
        ]
        can_disable = [
            'chkRepeat',
            'chkSequence',
            'cbBreakSequence',
            'chkSuspend',
        ]
        to_disable = []
        if idx == 0:
            current_widget = 'canvasOptions_Interval'
        elif idx == 1:
            current_widget = 'canvasOptions_Time'
        elif idx == 2:
            current_widget = 'canvasOptions_Command'
        elif idx == 3:
            current_widget = 'canvasOptions_IdleTime'
        elif idx == 4:
            current_widget = 'canvasOptions_SysEvent'
            to_disable = ['chkRepeat']
        elif idx == 5:
            current_widget = 'canvasOptions_FileWatch'
        elif idx == 6:
            current_widget = 'canvasOptions_DBusEvent'
            to_disable = ['chkRepeat']
        else:
            current_widget = 'canvasOptions_Empty'
        for w in widgets:
            if w == current_widget:
                o(w).show()
            else:
                o(w).hide()
        for w in can_disable:
            if w in to_disable:
                o(w).set_sensitive(False)
            else:
                o(w).set_sensitive(True)

    def click_btnChooseWatchedPath(self, _):
        o = self.builder.get_object
        curpath = o('txtWatchPath').get_text()
        if o('chkSelectDirectory').get_active():
            dlgtitle = resources.DLG_TITLE_CHOOSE_DIR
            dlgaction = Gtk.FileChooserAction.SELECT_FOLDER
        else:
            dlgtitle = resources.DLG_TITLE_CHOOSE_FILE
            dlgaction = Gtk.FileChooserAction.OPEN
        dirdlg = Gtk.FileChooserDialog(title=dlgtitle, action=dlgaction,
                                       buttons=(Gtk.STOCK_CANCEL,
                                                Gtk.ResponseType.CANCEL,
                                                Gtk.STOCK_OK,
                                                Gtk.ResponseType.OK))
        if os.path.exists(curpath):
            dirdlg.set_filename(curpath)
        ret = dirdlg.run()
        dirdlg.hide()
        if ret == Gtk.ResponseType.OK:
            o('txtWatchPath').set_text(dirdlg.get_filename())

    def choose_condition(self, box):
        o = self.builder.get_object
        self.default_box()
        name = box.get_active_text()
        if name in self.stored_conditions:
            cond = conditions.get(cond_name=name)
            self.update_box_type(None)
            if type(cond) == IntervalBasedCondition:
                intv = cond.interval / 60
                if intv % 60 == 0:
                    o('cbTimeUnit').set_active(0)
                    intv /= 60
                o('txtInterval').set_text(str(int(intv)))
                o('cbType').set_active(0)
            elif type(cond) == TimeBasedCondition:
                if cond.year:
                    o('txtYear').set_text(str(cond.year))
                if cond.month:
                    o('cbMonth').set_active(cond.month - 1)
                if cond.day:
                    o('txtDay').set_text(str(cond.day))
                if cond.weekday:
                    o('cbWeekday').set_active(cond.weekday)
                if cond.hour:
                    o('txtHour').set_text(str(cond.hour))
                if cond.minute:
                    o('txtMinute').set_text(str(cond.minute))
                o('cbType').set_active(1)
            elif type(cond) == CommandBasedCondition:
                o('txtCommand').set_text(cond.command)
                o('chkExactMatch').set_active(cond.match_exact)
                o('chkCaseSensitive').set_active(cond.case_sensitive)
                o('chkRegExp').set_active(cond.match_regexp)
                if cond.expected_status is not None:
                    o('cbCheckWhat').set_active(0)
                    o('txtCheckValue').set_text(str(cond.expected_status))
                elif cond.expected_stdout is not None:
                    o('cbCheckWhat').set_active(1)
                    o('txtCheckValue').set_text(cond.expected_stdout)
                elif cond.expected_stderr is not None:
                    o('cbCheckWhat').set_active(2)
                    o('txtCheckValue').set_text(cond.expected_stderr)
                o('cbType').set_active(2)
            elif type(cond) == IdleTimeBasedCondition:
                o('txtIdleMins').set_text(str(int(cond.idle_secs / 60)))
                o('cbType').set_active(3)
            elif type(cond) == EventBasedCondition:
                evt = cond.event
                cb_type = 4
                if evt in self.all_events:
                    o('cbSysEvent').set_active(self.all_events.index(evt))
                elif evt.startswith(EVENT_COMMAND_LINE_PREAMBLE + ':'):
                    o('cbSysEvent').set_active(
                        self.all_events.index(EVENT_COMMAND_LINE))
                elif evt.startswith(EVENT_DBUS_SIGNAL_PREAMBLE + ':'):
                    # although this is implemented as an event based condition
                    # it is not presented to the user as such
                    handler_name = evt.split(':')[1]
                    handler_index = self.stored_handlers.index(handler_name)
                    o('cbDBusEvent').set_active(handler_index)
                    cb_type = 6
                else:
                    o('cbSysEvent').set_active(-1)
                o('cbType').set_active(cb_type)
            elif type(cond) == PathNotifyBasedCondition:
                # here we only handle a single file or directory for the
                # moment, so the file name is the first element of the
                # inherent watched_paths list
                if cond.watched_paths:
                    fname = cond.watched_paths[0]
                    if os.path.exists(fname):
                        if os.path.isdir(fname):
                            o('chkSelectDirectory').set_active(True)
                        else:
                            o('chkSelectDirectory').set_active(False)
                    else:
                        o('chkSelectDirectory').set_active(False)
                else:
                    fname = ''
                    o('chkSelectDirectory').set_active(True)
                o('txtWatchPath').set_text(fname)
                o('cbType').set_active(5)
            else:
                o('cbType').set_active(-1)
            o('chkRepeat').set_active(cond.repeat)
            o('chkSequence').set_active(cond.exec_sequence)
            o('chkSuspend').set_active(cond.suspended)
            if cond.break_failure:
                o('cbBreakSequence').set_active(1)
            elif cond.break_success:
                o('cbBreakSequence').set_active(2)
            else:
                o('cbBreakSequence').set_active(0)
            o('cbBreakSequence').set_sensitive(cond.exec_sequence)
            m = o('store_listTasks')
            for x in cond.task_names:
                m.append([x])

    def change_txtName(self, _):
        o = self.builder.get_object
        name = o('txtName').get_text()
        if VALIDATE_CONDITION_RE.match(name):
            o('buttonOK').set_sensitive(True)
            if name in self.stored_conditions:
                o('btnDelete').set_sensitive(True)
            else:
                o('btnDelete').set_sensitive(False)
        else:
            o('buttonOK').set_sensitive(False)
            o('btnDelete').set_sensitive(False)

    def change_cbCheckWhat(self, _):
        o = self.builder.get_object
        if o('cbCheckWhat').get_active() == 0:
            o('chkExactMatch').set_sensitive(False)
            o('chkCaseSensitive').set_sensitive(False)
            o('chkRegExp').set_sensitive(False)
        else:
            o('chkExactMatch').set_sensitive(True)
            o('chkCaseSensitive').set_sensitive(True)
            o('chkRegExp').set_sensitive(True)

    def change_cbTimeUnit(self, _):
        o = self.builder.get_object
        if o('cbTimeUnit').get_active() == 0:
            l = UI_INTERVALS_HOURS
        else:
            l = UI_INTERVALS_MINUTES
        cb = o('cbInterval')
        cb.get_model().clear()
        for x in l:
            cb.append_text(str(x))

    def click_chkSequence(self, _):
        o = self.builder.get_object
        o('cbBreakSequence').set_sensitive(o('chkSequence').get_active())

    def default_box(self, include_name=False):
        o = self.builder.get_object
        if include_name:
            o('txtName').set_text('')
        o('txtInterval').set_text('')
        o('txtYear').set_text('')
        o('cbMonth').set_active(-1)
        o('txtDay').set_text('')
        o('cbWeekday').set_active(-1)
        o('txtHour').set_text('')
        o('txtMinute').set_text('')
        o('txtCommand').set_text('')
        o('txtCheckValue').set_text('0')
        o('txtIdleMins').set_text('')
        o('cbType').set_active(2)
        o('cbTimeUnit').set_active(1)
        o('cbSysEvent').set_active(1)
        o('cbDBusEvent').set_active(0)
        o('txtWatchPath').set_text('')
        o('chkSelectDirectory').set_active(True)
        o('cbAddTask').set_active(-1)
        o('cbCheckWhat').set_active(0)
        o('chkRepeat').set_active(True)
        o('chkSequence').set_active(True)
        o('cbBreakSequence').set_active(0)
        o('chkExactMatch').set_active(False)
        o('chkCaseSensitive').set_active(False)
        o('chkRegExp').set_active(False)
        o('chkSuspend').set_active(False)
        o('store_listTasks').clear()
        cb = o('cbInterval')
        cb.get_model().clear()
        for x in UI_INTERVALS_MINUTES:
            cb.append_text(str(x))

    def run(self):
        o = self.builder.get_object
        self.default_box(True)
        self.stored_conditions = conditions.names
        self.stored_conditions.sort()
        cb_conds = o('cbConditionName')
        cb_conds.get_model().clear()
        for x in self.stored_conditions:
            cb_conds.append_text(x)
        self.stored_tasks = tasks.names
        self.stored_tasks.sort()
        cb_tasks = o('cbAddTask')
        cb_tasks.get_model().clear()
        for x in self.stored_tasks:
            cb_tasks.append_text(x)
        self.stored_handlers = signal_handlers.names
        self.stored_handlers.sort()
        cb_handlers = o('cbDBusEvent')
        cb_handlers.get_model().clear()
        for x in self.stored_handlers:
            cb_handlers.append_text(x)
        self.dialog.set_keep_above(True)
        self.dialog.present()
        self.change_txtName(None)
        self.change_cbCheckWhat(None)
        ret = self.dialog.run()
        self.dialog.hide()
        self.dialog.set_keep_above(False)
        if ret == ACTION_OK:
            name = o('txtName').get_text()
            repeat = o('chkRepeat').get_active()
            sequence = o('chkSequence').get_active()
            suspend = o('chkSuspend').get_active()
            break_sequence = o('cbBreakSequence').get_active()
            break_success = False
            break_failure = False
            if break_sequence == 1:
                break_failure = True
            elif break_sequence == 2:
                break_success = True
            task_names = []
            m = o('store_listTasks')
            for row in m:
                task_names.append(row[0])
            idx = o('cbType').get_active()
            if idx == 0:
                v = int(o('txtInterval').get_text())
                if o('cbTimeUnit').get_active == 0:
                    interval = v * 60 * 60
                else:
                    interval = v * 60
                c = IntervalBasedCondition(name, interval, repeat, sequence)
                c.break_failure = break_failure
                c.break_success = break_success
            elif idx == 1:
                now = time.localtime()
                current_year = now.tm_year
                timedict = {
                    'year': self.validate_int(o('txtYear').get_text(), min_value=current_year),
                    'month': self.validate_int(o('cbMonth').get_active() + 1, min_value=1, max_value=12),
                    'day': self.validate_int(o('txtDay').get_text(), min_value=1, max_value=31),
                    'weekday': self.validate_int(o('cbWeekday').get_active(), min_value=0, max_value=6),
                    'hour': self.validate_int(o('txtHour').get_text(), min_value=0, max_value=24),
                    'minute': self.validate_int(o('txtMinute').get_text(), min_value=0, max_value=59),
                }
                c = TimeBasedCondition(name, timedict, repeat, sequence)
                c.break_failure = break_failure
                c.break_success = break_success
            elif idx == 2:
                command = o('txtCommand').get_text()
                status, stdout, stderr = None, None, None
                chk = o('cbCheckWhat').get_active()
                if chk == 0:
                    status = self.validate_int(o('txtCheckValue').get_text(), 0)
                    if status is None:
                        msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                                   buttons=Gtk.ButtonsType.OK)
                        msgbox.set_markup(resources.DLG_WRONG_EXIT_STATUS)
                        msgbox.run()
                        msgbox.hide()
                        applet_log.warning("DLGCOND: wrong exit code specification")
                        status = 0
                elif chk == 1:
                    stdout = str(o('txtCheckValue').get_text())
                elif chk == 2:
                    stderr = str(o('txtCheckValue').get_text())
                c = CommandBasedCondition(
                    name, command, status, stdout, stderr, repeat, sequence)
                c.break_failure = break_failure
                c.break_success = break_success
                c.match_exact = o('chkExactMatch').get_active()
                c.case_sensitive = o('chkCaseSensitive').get_active()
                c.match_regexp = o('chkRegExp').get_active()
            elif idx == 3:
                idle_secs = int(o('txtIdleMins').get_text()) * 60
                c = IdleTimeBasedCondition(name, idle_secs, repeat, sequence)
                c.break_failure = break_failure
                c.break_success = break_success
            elif idx == 4:
                event_type = self.all_events[o('cbSysEvent').get_active()]
                if event_type == EVENT_COMMAND_LINE:
                    event_type = EVENT_COMMAND_LINE_PREAMBLE + ':' + name
                c = EventBasedCondition(
                    name, event_type, True, repeat, sequence)
                c.break_failure = break_failure
                c.break_success = break_success
            elif idx == 5:
                if watch_path_manager is not None:
                    fname = str(o('txtWatchPath').get_text()).strip()
                    if fname:
                        fname = os.path.realpath(os.path.normpath(fname))
                        if os.path.isdir(fname):
                            fname += '/'
                        c = PathNotifyBasedCondition(
                            name, [fname], True, repeat, sequence)
                        c.break_failure = break_failure
                        c.break_success = break_success
                    else:
                        msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                                   buttons=Gtk.ButtonsType.OK)
                        msgbox.set_markup(resources.DLG_PATH_NOT_SPECIFIED)
                        msgbox.run()
                        msgbox.hide()
                        return None
                else:
                    msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                               buttons=Gtk.ButtonsType.OK)
                    msgbox.set_markup(resources.DLG_NOT_ENABLED_FEATURE)
                    msgbox.run()
                    msgbox.hide()
                    applet_log.warning("DLGCOND: file watch condition is disabled")
                    return None
            elif idx == 6:
                handler_name = o('cbDBusEvent').get_active_text()
                event_type = EVENT_DBUS_SIGNAL_PREAMBLE + ':' + handler_name
                c = EventBasedCondition(
                    name, event_type, True, repeat, sequence)
                c.break_failure = break_failure
                c.break_success = break_success
            for x in task_names:
                if tasks.get(task_name=x):
                    c.add_task(x)
            if suspend:
                c.suspend()
            else:
                c.resume()
            c.dump()
            conditions.add(c)
            conditions.save()
            return c
        elif ret == ACTION_DELETE:
            name = o('txtName').get_text()
            cond = conditions.get(cond_name=name)
            if cond:
                msgbox = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,
                                           buttons=Gtk.ButtonsType.YES_NO)
                msgbox.set_markup(resources.DLG_CONFIRM_DELETE_CONDITION % name)
                ret = msgbox.run()
                msgbox.hide()
                if ret == Gtk.ResponseType.YES:
                    self.default_box(True)
                    if conditions.remove(cond_name=name):
                        conditions.save()
                    else:
                        applet_log.error("DLGCOND: condition %s could not be deleted" % name)
                        msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                                   buttons=Gtk.ButtonsType.OK)
                        msgbox.set_markup(
                            resources.DLG_CANNOT_DELETE_CONDITION % name)
                        msgbox.run()
                        msgbox.hide()
                else:
                    applet_log.debug("DLGCOND: removal of condition %s canceled")
            else:
                applet_log.error("DLGCOND: condition %s not found" % name)
                msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                           buttons=Gtk.ButtonsType.OK)
                msgbox.set_markup(resources.DLG_CANNOT_FIND_CONDITION % name)
                msgbox.run()
                msgbox.hide()
            return None
        else:
            return None


class SignalDialog(object):

    def __init__(self):
        self.builder = Gtk.Builder().new_from_string(ui_add_signal, -1)
        self.builder.connect_signals(self)
        self.builder.set_translation_domain(APPLET_NAME)
        o = self.builder.get_object
        self.dialog = o('dlgAddDBusSignal')
        self.stored_handlers = signal_handlers.names
        self.stored_handlers.sort()
        cb_handlers = o('cbName')
        cb_handlers.get_model().clear()
        for x in self.stored_handlers:
            cb_handlers.append_text(x)
        l = o('listTests')
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_SIGNAL_PARAMETER, renderer, text=0)
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_SIGNAL_PARAMETER_SUB, renderer, text=1)
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_SIGNAL_NEGATE, renderer, text=2)
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_SIGNAL_OPERATOR, renderer, text=3)
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_SIGNAL_VALUE, renderer, text=4)
        l.append_column(c)
        self.signal_param_tests = []
        self.all_comparisons = [
            DBUS_CHECK_COMPARE_IS,
            DBUS_CHECK_COMPARE_CONTAINS,
            DBUS_CHECK_COMPARE_MATCHES,
            DBUS_CHECK_COMPARE_LESS,
            DBUS_CHECK_COMPARE_GREATER,
        ]
        self.all_comparisons_symdict = {
            DBUS_CHECK_COMPARE_IS: '=',
            DBUS_CHECK_COMPARE_CONTAINS: 'CONTAINS',
            DBUS_CHECK_COMPARE_MATCHES: 'MATCHES',
            DBUS_CHECK_COMPARE_LESS: '<',
            DBUS_CHECK_COMPARE_GREATER: '>',
        }
        self.all_comparisons_revdict = {}
        for k in self.all_comparisons_symdict.keys():
            self.all_comparisons_revdict[self.all_comparisons_symdict[k]] = k

    def validate_int(self, s, min_value=None, max_value=None):
        try:
            n = int(s)
            if min_value is not None and n < min_value:
                return None
            elif max_value is not None and n > max_value:
                return None
            else:
                return n
        except ValueError as e:
            return None

    def click_btnAddTest(self, _):
        o = self.builder.get_object
        s = o('txtValueNum').get_text()
        value_idx = self.validate_int(s, min_value=0)
        if value_idx is None:
            applet_log.debug("DLGSIG: not adding signal check with bad param index")
            msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                       buttons=Gtk.ButtonsType.OK)
            msgbox.set_markup(resources.DLG_WRONG_PARAM_INDEX)
            msgbox.run()
            msgbox.hide()
            return
        sub_idx = o('txtValueSub').get_text()
        if sub_idx == '':
            sub_idx = None
        elif self.validate_int(sub_idx, min_value=0) is not None:
            sub_idx = int(sub_idx)
        else:
            if not VALIDATE_DBUS_SUBPARAM_RE.match(sub_idx):
                applet_log.debug("DLGSIG: not adding signal check with bad subparam index")
                msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                           buttons=Gtk.ButtonsType.OK)
                msgbox.set_markup(resources.DLG_WRONG_PARAM_INDEX)
                msgbox.run()
                msgbox.hide()
                return
        l = [x for x in self.signal_param_tests
             if x.value_idx != value_idx or x.sub_idx != sub_idx]
        check = param_check(
            value_idx,
            sub_idx,
            self.all_comparisons[o('cbOperatorCompare').get_active()],
            bool(o('chkOperatorNot').get_active()),
            str(o('txtTestValue').get_text()),
        )
        l.append(check)
        self.signal_param_tests = l
        self.update_listTests()
        o('txtValueNum').set_text("")
        o('txtValueSub').set_text("")
        o('chkOperatorNot').set_active(False)
        o('cbOperatorCompare').set_active(0)
        o('txtTestValue').set_text("")

    def click_btnRemoveTest(self, _):
        o = self.builder.get_object
        s = o('txtValueNum').get_text()
        if not s:
            applet_log.debug("DLGSIG: not removing signal check without param index")
            return
        try:
            value_idx = int(s)
            if value_idx < 0:
                applet_log.debug("DLGSIG: not removing signal check with bad param index")
                return
        except:
            applet_log.debug("DLGSIG: not removing signal check with bad param index")
            return
        sub_idx = o('txtValueSub').get_text()
        if sub_idx == '':
            sub_idx = None
        else:
            if self.validate_int(sub_idx, min_value=0) is not None:
                sub_idx = int(sub_idx)
        l = [x for x in self.signal_param_tests
             if x.value_idx != value_idx or x.sub_idx != sub_idx]
        self.signal_param_tests = l
        self.update_listTests()

    def click_listTests(self, selected):
        o = self.builder.get_object
        m, i = selected.get_selected()
        if i is not None:
            o('txtValueNum').set_text(m[i][0])
            o('txtValueSub').set_text(m[i][1])
            o('chkOperatorNot').set_active(m[i][2] == 'NOT')
            o('cbOperatorCompare').set_active(
                self.all_comparisons.index(self.all_comparisons_revdict[m[i][3]]))
            o('txtTestValue').set_text(m[i][4])

    def update_listTests(self):
        o = self.builder.get_object
        m = o('listTests').get_model()
        m.clear()
        for check in self.signal_param_tests:
            row = [
                str(check.value_idx),
                '' if check.sub_idx is None else str(check.sub_idx),
                'NOT' if check.negate else '',
                self.all_comparisons_symdict[check.comparison],
                str(check.test_value),
            ]
            m.append(row)

    def choose_handler(self, box):
        o = self.builder.get_object
        name = box.get_active_text()
        if name in self.stored_handlers:
            handler = signal_handlers.get(handler_name=name)
            o('txtValueNum').set_text("")
            o('txtValueSub').set_text("")
            o('txtTestValue').set_text("")
            if handler.bus == 'session':
                o('cbBusType').set_active(0)
            elif handler.bus == 'system':
                o('cbBusType').set_active(1)
            o('txtBusID').set_text(handler.bus_name)
            o('txtBusPath').set_text(handler.bus_path)
            o('txtInterface').set_text(handler.interface)
            o('txtSignal').set_text(handler.signal)
            self.signal_param_tests = handler.param_checks.copy()
            self.update_listTests()
            if handler.verify_all_checks:
                o('rdAll').set_active(True)
            else:
                o('rdAny').set_active(True)
            o('chkDefer').set_active(handler.defer)

    def change_txtValues(self, _):
        o = self.builder.get_object
        name = o('txtName').get_text()
        busname = o('txtBusID').get_text()
        path = o('txtBusPath').get_text()
        interface = o('txtInterface').get_text()
        signal = o('txtSignal').get_text()
        valid_name = bool(VALIDATE_SIGNAL_HANDLER_RE.match(name))
        valid_busname = bool(VALIDATE_DBUS_NAME_RE.match(busname))
        valid_path = bool(VALIDATE_DBUS_PATH_RE.match(path))
        valid_interface = bool(VALIDATE_DBUS_INTERFACE_RE.match(interface))
        valid_signal = bool(VALIDATE_DBUS_SIGNAL_RE.match(signal))
        if valid_name:
            if valid_busname and valid_path and valid_interface and valid_signal:
                o('buttonOK').set_sensitive(True)
            else:
                o('buttonOK').set_sensitive(False)
            if name in self.stored_handlers:
                o('btnDelete').set_sensitive(True)
            else:
                o('btnDelete').set_sensitive(False)
        else:
            o('buttonOK').set_sensitive(False)
            o('btnDelete').set_sensitive(False)

    def default_box(self, include_name=False):
        o = self.builder.get_object
        if include_name:
            o('txtName').set_text("")
        o('cbBusType').set_active(0)
        o('txtBusID').set_text("")
        o('txtBusPath').set_text("")
        o('txtInterface').set_text("")
        o('txtSignal').set_text("")
        o('txtValueNum').set_text("")
        o('txtValueSub').set_text("")
        o('chkOperatorNot').set_active(False)
        o('cbOperatorCompare').set_active(0)
        o('txtTestValue').set_text("")
        o('rdAny').set_active(True)
        o('chkDefer').set_active(True)
        o('store_listTests').clear()
        o('buttonOK').set_sensitive(False)
        o('btnDelete').set_sensitive(False)

    def run(self):
        o = self.builder.get_object
        self.default_box(True)
        self.stored_handlers = signal_handlers.names
        self.stored_handlers.sort()
        cb_handlers = o('cbName')
        cb_handlers.get_model().clear()
        for x in self.stored_handlers:
            cb_handlers.append_text(x)
        self.dialog.set_keep_above(True)
        self.dialog.present()
        ret = self.dialog.run()
        self.dialog.hide()
        self.dialog.set_keep_above(False)
        if ret == ACTION_OK:
            name = o('txtName').get_text()
            bus_name = o('txtBusID').get_text()
            bus_path = o('txtBusPath').get_text()
            interface = o('txtInterface').get_text()
            signal = o('txtSignal').get_text()
            defer = o('chkDefer').get_active()
            if o('cbBusType').get_active() == 0:
                bus = 'session'
            elif o('cbBusType').get_active() == 1:
                bus = 'system'
            if o('rdAny').get_active():
                verify_all = False
            elif o('rdAll').get_active():
                verify_all = True
            h = SignalHandler(name, bus, bus_name, bus_path, interface, signal)
            h.defer = bool(defer)
            for x in self.signal_param_tests:
                h.add_check(
                    x.value_idx, x.sub_idx, x.negate, x.comparison,
                    x.test_value.strip())
            if not signal_handlers.add(h):
                applet_log.error("DLGSIG: signal handler %s could not be registererd" % name)
                msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                           buttons=Gtk.ButtonsType.OK)
                msgbox.set_markup(
                    resources.DLG_CANNOT_REGISTER_SIGHANDLER % name)
                msgbox.run()
                msgbox.hide()
            signal_handlers.save()
            return h
        elif ret == ACTION_DELETE:
            name = o('txtName').get_text()
            handler = signal_handlers.get(handler_name=name)
            if handler:
                msgbox = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,
                                           buttons=Gtk.ButtonsType.YES_NO)
                msgbox.set_markup(
                    resources.DLG_CONFIRM_DELETE_SIGHANDLER % name)
                ret = msgbox.run()
                msgbox.hide()
                if ret == Gtk.ResponseType.YES:
                    self.default_box(True)
                    if signal_handlers.remove(handler_name=name):
                        signal_handlers.save()
                    else:
                        applet_log.error("DLGSIG: signal handler %s could not be deleted" % name)
                        msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                                   buttons=Gtk.ButtonsType.OK)
                        msgbox.set_markup(
                            resources.DLG_CANNOT_DELETE_SIGHANDLER % name)
                        msgbox.run()
                        msgbox.hide()
                else:
                    applet_log.info("DLGSIG: removal of signal handler %s canceled" % name)
            return None
        else:
            return None


# settings dialog
class SettingsDialog(object):

    def __init__(self):
        self.builder = Gtk.Builder().new_from_string(ui_settings, -1)
        self.builder.connect_signals(self)
        self.builder.set_translation_domain(APPLET_NAME)
        o = self.builder.get_object
        self.dialog = o('dlgSettings')
        self.log_levels = [
            'critical',
            'error',
            'warning',
            'info',
            'debug',
        ]
        self.icon_themes = [
            'light',
            'dark',
            'color',
            'guess',
        ]

    def default_box(self):
        o = self.builder.get_object
        log_level_idx = self.log_levels.index(
            config.get('General', 'log level'))
        icon_theme_idx = self.icon_themes.index(
            config.get('General', 'icon theme'))
        o('chkShowIcon').set_active(
            config.get('General', 'show icon'))
        o('chkAutostart').set_active(
            config.get('General', 'autostart'))
        o('chkMinimalisticMode').set_active(
            config.get('General', 'minimalistic mode'))
        o('chkNotifications').set_active(config.get('General', 'notifications'))
        o('chkPreservePause').set_active(
            config.get('Scheduler', 'preserve pause'))
        o('cbLogLevel').set_active(log_level_idx)
        o('cbIconTheme').set_active(icon_theme_idx)
        o('txtTickSeconds').set_text(
            str(config.get('Scheduler', 'tick seconds')))
        o('txtSkipSeconds').set_text(
            str(config.get('Scheduler', 'skip seconds')))
        o('txtMaxThreads').set_text(
            str(config.get('Concurrency', 'max threads')))
        o('txtMaxLogSize').set_text(str(config.get('History', 'log size')))
        o('txtMaxLogBackups').set_text(
            str(config.get('History', 'log backups')))
        o('txtMaxHistoryItems').set_text(
            str(config.get('History', 'max items')))
        if signal_handlers.not_empty:
            o('chkEnableUserEvents').set_active(True)
            o('chkEnableUserEvents').set_sensitive(False)
        else:
            o('chkEnableUserEvents').set_active(
                config.get('General', 'user events'))
            o('chkEnableUserEvents').set_sensitive(True)
        if FILE_NOTIFY_ENABLED:
            o('chkEnableWatchPaths').set_active(
                config.get('General', 'file notifications'))
            o('chkEnableWatchPaths').set_sensitive(True)
        else:
            o('chkEnableWatchPaths').set_active(False)
            o('chkEnableWatchPaths').set_sensitive(False)
        o('chkEnableEnvVars').set_active(
            config.get('General', 'environment vars'))

    def run(self):
        o = self.builder.get_object
        self.default_box()
        self.dialog.set_keep_above(True)
        self.dialog.present()
        ret = self.dialog.run()
        self.dialog.hide()
        self.dialog.set_keep_above(False)
        if ret == ACTION_OK:
            config_skip = []
            v = o('cbLogLevel').get_active()
            if v >= 0:
                config.set('General', 'log level', self.log_levels[v])
            else:
                config_skip.append('log level')
            config.set('General', 'icon theme',
                       self.icon_themes[o('cbIconTheme').get_active()])
            config.set('General', 'show icon', o('chkShowIcon').get_active())
            config.set('General', 'autostart', o('chkAutostart').get_active())
            config.set('General', 'minimalistic mode',
                       o('chkMinimalisticMode').get_active())
            config.set('General', 'notifications',
                       o('chkNotifications').get_active())
            config.set('General', 'user events',
                       o('chkEnableUserEvents').get_active())
            config.set('General', 'file notifications',
                       o('chkEnableWatchPaths').get_active())
            config.set('General', 'environment vars',
                       o('chkEnableEnvVars').get_active())
            preserve_pause = o('chkPreservePause').get_active()
            config.set('Scheduler', 'preserve pause', preserve_pause)
            if not preserve_pause:
                unlink_pause_file()
            try:
                t = o('txtTickSeconds').get_text()
                v = int(t)
                if v > 0:
                    config.set('Scheduler', 'tick seconds', v)
                else:
                    config_skip.append('tick seconds')
            except ValueError:
                config_skip.append('tick seconds')
            try:
                t = o('txtSkipSeconds').get_text()
                v = int(t)
                if v >= config.get('Scheduler', 'tick seconds'):
                    config.set('Scheduler', 'skip seconds', v)
                else:
                    config_skip.append('skip seconds')
            except ValueError:
                config_skip.append('skip seconds')
            try:
                t = o('txtMaxThreads').get_text()
                v = int(t)
                if v > 1:
                    config.set('Concurrency', 'max threads', v)
                else:
                    config_skip.append('max threads')
            except ValueError:
                config_skip.append('max threads')
            try:
                t = o('txtMaxLogSize').get_text()
                v = int(t)
                if v > 0:
                    config.set('History', 'log size', v)
                else:
                    config_skip.append('log size')
            except ValueError:
                config_skip.append('log size')
            try:
                t = o('txtMaxLogBackups').get_text()
                v = int(t)
                if v > 0:
                    config.set('History', 'log backups', v)
                else:
                    config_skip.append('log backups')
            except ValueError:
                config_skip.append('log backups')
            try:
                t = o('txtMaxHistoryItems').get_text()
                v = int(t)
                if v > 0:
                    config.set('History', 'max items', v)
                else:
                    config_skip.append('max items')
            except ValueError:
                config_skip.append('max items')
            if config_skip:
                applet_log.info("DLGCONF: values for %s invalid: skipped" % ", ".join(config_skip))
            applet_log.info("DLGCONF: saving user configuration")
            config.save()
            # reconfigure running applet as much as possible
            applet_log.info("DLGCONF: reconfiguring application")
            config_loghandler()
            config_loglevel()
            periodic.restart(new_interval=config.get('Scheduler', 'tick seconds'))
            history.resize()
            create_autostart_file()
            applet.hide_icon(not config.get('General', 'show icon'))


class HistoryDialog(object):

    def __init__(self):
        self.builder = Gtk.Builder().new_from_string(ui_task_history, -1)
        self.builder.connect_signals(self)
        self.builder.set_translation_domain(APPLET_NAME)
        o = self.builder.get_object
        self.dialog = o('dlgHistory')
        self.image_success = Gtk.Image.new_from_file(
            os.path.join(APP_ICON_FOLDER, 'emblems', 'success.png'))
        self.image_failure = Gtk.Image.new_from_file(
            os.path.join(APP_ICON_FOLDER, 'emblems', 'failure.png'))
        l = o('listHistory')
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_HISTORY_TIMESTAMP, renderer, text=0)
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_HISTORY_TASK, renderer, text=1)
        c.props.expand = True
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_HISTORY_TRIGGER, renderer, text=2)
        c.props.expand = True
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_HISTORY_EXITCODE, renderer, text=3)
        l.append_column(c)
        renderer = Gtk.CellRendererPixbuf()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_HISTORY_SUCCESS, renderer, pixbuf=4)
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_HISTORY_REASON, renderer, text=5)
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(
            resources.LISTCOL_HISTORY_ROWID, renderer, text=6)
        c.set_visible(False)
        l.append_column(c)
        o('txtStdOut').modify_font(Pango.FontDescription('Monospace'))
        o('txtStdErr').modify_font(Pango.FontDescription('Monospace'))

    def choose_item(self, selected):
        o = self.builder.get_object
        m, i = selected.get_selected()
        if i is not None:
            item_id = m[i][6]
            item = history.item_by_id(item_id)
            if item:
                if item.stdout:
                    o('txtStdOut').get_buffer().set_text(item.stdout)
                else:
                    o('txtStdOut').get_buffer().set_text("")
                if item.stderr:
                    o('txtStdErr').get_buffer().set_text(item.stderr)
                else:
                    o('txtStdErr').get_buffer().set_text("")
            else:
                o('txtStdOut').get_buffer().set_text("")
                o('txtStdErr').get_buffer().set_text("")

    def update_list(self):
        o = self.builder.get_object
        rows = []
        for i in history.items():
            s_time = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(i.startup_time))
            emblem = self.image_success if i.success else self.image_failure
            row = [
                '%s / %.2f' % (s_time, i.run_time),
                i.task_name,
                i.trigger_cond if i.trigger_cond is not None else '',
                str(i.exit_code) if i.exit_code is not None else '',
                emblem.get_pixbuf(),
                i.failure_reason if i.failure_reason is not None else '',
                i.item_id,
            ]
            rows.insert(0, row)
        m = o('store_listHistory')
        m.clear()
        for row in rows:
            m.append(row)

    def click_btnReload(self, _):
        self.update_list()

    def run(self):
        self.update_list()
        self.dialog.set_keep_above(True)
        self.dialog.present()
        ret = self.dialog.run()
        self.dialog.hide()
        self.dialog.set_keep_above(False)


class AboutDialog(object):

    def __init__(self):
        self.image_logo = Gtk.Image.new_from_file(
            os.path.join(APP_ICON_FOLDER, 'alarmclock-128.png'))
        self.builder = Gtk.Builder().new_from_string(ui_about, -1)
        self.builder.connect_signals(self)
        self.builder.set_translation_domain(APPLET_NAME)
        o = self.builder.get_object
        self.dialog = o('dlgAbout')
        self.dialog.set_logo(self.image_logo.get_pixbuf())
        self.dialog.set_version(
            resources.DLG_ABOUT_VERSION_STRING % APPLET_VERSION)
        self.dialog.set_icon_from_file(
            os.path.join(APP_ICON_FOLDER, 'alarmclock.png'))

    def run(self):
        self.dialog.set_keep_above(True)
        self.dialog.present()
        ret = self.dialog.run()
        self.dialog.hide()
        self.dialog.set_keep_above(False)


#############################################################################
# Applet

# program startup
class AppletIndicator(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id=APPLET_ID,
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)

        # shortcut to make code more clean and less repetitive
        def _signal_manager(bus, bus_name, bus_path, bus_interface, sigs_handlers):
            try:
                proxy = bus.get_object(bus_name, bus_path)
                manager = dbus.Interface(proxy, bus_interface)
                for signal, handler in sigs_handlers:
                    manager.connect_to_signal(signal, handler)
                return manager
            except dbus.exceptions.DBusException:
                applet_log.error("MAIN: error registering %s handlers" % bus_interface)
                return None

        try:
            self.register(None)
        except Exception as e:
            applet_log.critical("MAIN: exception %s registering application" % _x(e))
            sys.exit(2)

        self.connect('activate', self.applet_activate)
        self.leaving = False

        # The system and session bus signals give many possibilities for events
        self.system_bus = dbus.SystemBus()
        self.session_bus = dbus.SessionBus()
        self.applet_bus = AppletDBusService()

        enabled_events = [EVENT_APPLET_STARTUP]

        # DBus events
        self.login_mgr = _signal_manager(
            self.system_bus,
            'org.freedesktop.login1', '/org/freedesktop/login1',
            'org.freedesktop.login1.Manager',
            [
                ('PrepareForShutdown', self.before_shutdown),
                ('PrepareForSleep', self.system_sleep_manager),
            ]
        )
        if self.login_mgr:
            enabled_events.append(EVENT_APPLET_SHUTDOWN)
            enabled_events.append(EVENT_SYSTEM_SUSPEND)
            enabled_events.append(EVENT_SYSTEM_RESUME)

        self.screensaver_mgr = _signal_manager(
            self.session_bus,
            'org.gnome.ScreenSaver', '/org/gnome/ScreenSaver',
            'org.gnome.ScreenSaver',
            [
                ('ActiveChanged', self.screensaver_manager),
            ]
        )
        if self.screensaver_mgr:
            enabled_events.append(EVENT_SESSION_SCREENSAVER)
            enabled_events.append(EVENT_SESSION_SCREENSAVER_EXIT)

        self.lock_mgr = _signal_manager(
            self.session_bus,
            'com.ubuntu.Upstart', '/com/ubuntu/Upstart',
            'com.ubuntu.Upstart0_6',
            [
                ('EventEmitted', self.upstart_lock_manager),
            ]
        )
        # self.lock_mgr = _signal_manager(
        #     self.system_bus,
        #     'org.freedesktop.login1', '/org/freedesktop/login1',
        #     'org.freedesktop.login1.Session',
        #     [
        #         ('Lock', self.session_login_lock),
        #         ('Unlock', self.session_login_unlock),
        #     ]
        # )
        if self.lock_mgr:
            enabled_events.append(EVENT_SESSION_LOCK)
            enabled_events.append(EVENT_SESSION_UNLOCK)

        self.storage_mgr = _signal_manager(
            self.system_bus,
            'org.freedesktop.UDisks2', '/org/freedesktop/UDisks2',
            'org.freedesktop.DBus.ObjectManager',
            [
                ('InterfacesAdded', self.storage_device_manager),
                ('InterfacesRemoved', self.storage_device_manager),
            ]
        )
        if self.storage_mgr:
            devices = self.storage_mgr.GetManagedObjects().keys()
            drives = filter(
                lambda x: x.startswith('/org/freedesktop/UDisks2/block_devices/'),
                devices)
            self.storage_mgr_num_devices = len(list(drives))
            enabled_events.append(EVENT_SYSTEM_DEVICE_ATTACH)
            enabled_events.append(EVENT_SYSTEM_DEVICE_DETACH)

        self.network_mgr = _signal_manager(
            self.system_bus,
            'org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager',
            'org.freedesktop.NetworkManager',
            [
                ('StateChanged', self.network_manager),
            ]
        )
        if self.network_mgr:
            enabled_events.append(EVENT_SYSTEM_NETWORK_JOIN)
            enabled_events.append(EVENT_SYSTEM_NETWORK_LEAVE)

        self.battery_mgr = _signal_manager(
            self.system_bus,
            'org.freedesktop.UPower', '/org/freedesktop/UPower',
            'org.freedesktop.UPower',
            [
                ('Changed', self.battery_manager),
            ]
        )
        if self.battery_mgr:
            enabled_events.append(EVENT_SYSTEM_BATTERY_CHARGE)
            enabled_events.append(EVENT_SYSTEM_BATTERY_DISCHARGING)
            enabled_events.append(EVENT_SYSTEM_BATTERY_LOW)

        # Template for standard (not custom DBus) signal handlers
        # self.MANAGER = _signal_manager(
        #     self.TYPE_BUS,
        #     'BUSNAME', '/BUSPATH',
        #     'BUSINT',
        #     [
        #         ('SIGNAL', self.HANDLER),
        #     ]
        # )
        # if self.MANAGER:
        #     enabled_events.append(EVENT_NAME)

        enabled_events.append(EVENT_COMMAND_LINE)
        set_applet_enabled_events(enabled_events)

        # we can build required dialog boxes since all needed data is present
        self.dialog_add_task = None
        self.dialog_add_condition = None
        self.dialog_about = None
        self.dialog_settings = None
        self.dialog_history = None
        self.dialog_add_dbus_signal = None
        if not config.get('General', 'minimalistic mode'):
            self.dialog_add_task = TaskDialog()
            self.dialog_add_condition = ConditionDialog()
            self.dialog_about = AboutDialog()
            self.dialog_settings = SettingsDialog()
            self.dialog_history = HistoryDialog()
            self.dialog_add_dbus_signal = SignalDialog()
        else:
            self.dialog_about = AboutDialog()
            self.dialog_settings = SettingsDialog()
            self.dialog_history = HistoryDialog()

    def applet_activate(self, applet_instance):
        self.main()

    def main(self):
        # GUI management
        settings = Gtk.Settings.get_default()
        icon_suffix = config.get('General', 'icon theme').lower()
        if icon_suffix not in ('dark', 'light', 'color'):
            theme_name = settings.get_property('gtk-icon-theme-name').lower()
            if 'dark' in theme_name:
                icon_suffix = 'dark'
            elif 'light' in theme_name:
                icon_suffix = 'light'
            else:
                icon_suffix = 'color'
        self.indicator = AppIndicator.Indicator.new(
            APPLET_NAME, 'alarm', AppIndicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_icon_theme_path(
            os.path.join(APP_ICON_FOLDER, icon_suffix))
        if config.get('General', 'show icon'):
            self.indicator.set_icon('alarm')
            self.indicator.set_attention_icon('warning')
            if config.get('General', 'show icon'):
                self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            self.indicator.set_menu(self.build_menu())
        if config.get('General', 'notifications'):
            Notify.init(APPLET_NAME)
            self._notify = Notify.Notification()

        # load items if any, otherwise save empty lists
        try:
            tasks.load()
        except FileNotFoundError:
            tasks.save()
        try:
            conditions.load()
        except FileNotFoundError:
            conditions.save()
        try:
            signal_handlers.load()
        except FileNotFoundError:
            signal_handlers.save()

        if signal_handlers.not_empty:
            applet_log.info("MAIN: signal handlers found, enabling user events")
            config.set('General', 'user events', True)
            config.save()

        applet_log.info("MAIN: trying to run startup tasks")
        sysevent_condition_check(EVENT_APPLET_STARTUP)
        Gtk.main()

    # system and session DBus event managers
    def screensaver_manager(self, *args):
        try:
            if self.screensaver_mgr.GetActive():
                applet_log.debug("MAIN: screensaver is active")
                deferred_events.append(EVENT_SESSION_SCREENSAVER)
            else:
                applet_log.debug("MAIN: screensaver deactivated")
                deferred_events.append(EVENT_SESSION_SCREENSAVER_EXIT)
        except dbus.exceptions.DBusException:
            applet_log.warning("MAIN: screensaver activity query failed")

    # def session_login_lock(self, *args):
    #     applet_log.debug("MAIN: session lock")
    #     deferred_events.append(EVENT_SESSION_LOCK)

    # def session_login_unlock(self, *args):
    #     applet_log.debug("MAIN: session unlock")
    #     deferred_events.append(EVENT_SESSION_UNLOCK)

    # this is apparently valid for ubuntu 14.04 and above
    # see: http://unix.stackexchange.com/a/211863/125979
    def upstart_lock_manager(self, *args):
        message = args[0]
        if message == 'desktop-lock':
            applet_log.debug("MAIN: session lock")
            deferred_events.append(EVENT_SESSION_LOCK)
        elif message == 'desktop-unlock':
            applet_log.debug("MAIN: session unlock")
            deferred_events.append(EVENT_SESSION_UNLOCK)

    def system_sleep_manager(self, *args):
        entering_sleep = args[0]
        if entering_sleep:
            applet_log.debug("MAIN: about to enter sleep state")
            sysevent_condition_check(EVENT_SYSTEM_SUSPEND)
        else:
            applet_log.debug("MAIN: woke up from sleep state")
            deferred_events.append(EVENT_SYSTEM_RESUME)

    def storage_device_manager(self, *args):
        applet_log.debug("MAIN: storage change detected")
        try:
            devices = self.storage_mgr.GetManagedObjects().keys()
            drives = filter(
                lambda x: x.startswith('/org/freedesktop/UDisks2/block_devices/'),
                devices)
            num_devices = len(list(drives))
            if self.storage_mgr_num_devices > num_devices:
                applet_log.debug("MAIN: device detached")
                deferred_events.append(EVENT_SYSTEM_DEVICE_DETACH)
            elif self.storage_mgr_num_devices < num_devices:
                applet_log.debug("MAIN: new device attached")
                deferred_events.append(EVENT_SYSTEM_DEVICE_ATTACH)
            self.storage_mgr_num_devices = num_devices
        except dbus.exceptions.DBusException:
            applet_log.warning("MAIN: storage objects query failed")

    def network_manager(self, *args):
        applet_log.debug("MAIN: network state changed")
        try:
            state = self.network_mgr.state()
            if state in [NM_STATE_CONNECTED_LOCAL, NM_STATE_CONNECTED_SITE,
                         NM_STATE_CONNECTED_GLOBAL]:
                applet_log.debug("MAIN: joined network")
                deferred_events.append(EVENT_SYSTEM_NETWORK_JOIN)
            elif state in [NM_STATE_DISCONNECTED]:
                applet_log.debug("MAIN: left network")
                deferred_events.append(EVENT_SYSTEM_NETWORK_LEAVE)
        except dbus.exceptions.DBusException:
            applet_log.warning("MAIN: network state query failed")

    def battery_manager(self, *args):
        applet_log.debug("MAIN: battery state changed")
        try:
            proxy = self.battery_mgr.proxy_object
            drain = proxy.Get('org.freedesktop.UPower', 'OnBattery',
                              dbus_interface='org.freedesktop.DBus.Properties')
            low = proxy.Get('org.freedesktop.UPower', 'OnLowBattery',
                            dbus_interface='org.freedesktop.DBus.Properties')
            if low:
                applet_log.debug("MAIN: battery low")
                deferred_events.append(EVENT_SYSTEM_BATTERY_LOW)
            elif drain:
                applet_log.debug("MAIN: battery discharging")
                deferred_events.append(EVENT_SYSTEM_BATTERY_DISCHARGING)
            else:
                applet_log.debug("MAIN: battery charging or charged")
                deferred_events.append(EVENT_SYSTEM_BATTERY_CHARGE)
        except:
            applet_log.warning("MAIN: battery state query failed")

    def before_shutdown(self, *args):
        if not self.leaving:
            applet_log.info("MAIN: trying to run shutdown tasks")
            sysevent_condition_check(EVENT_APPLET_SHUTDOWN)
            self.leaving = True

    def start_event_condition(self, cond_name, deferred):
        if cond_name not in conditions.names:
            applet_log.warning("MAIN: non existing condition %s will not trigger" % cond_name)
            return False
        cond = conditions.get(cond_name=cond_name)
        event = EVENT_COMMAND_LINE_PREAMBLE + ':' + cond_name
        if cond.event != event:
            applet_log.warning("MAIN: wrong event type for condition %s" % cond_name)
            return False
        if deferred:
            deferred_events.append(event)
        else:
            sysevent_condition_check(event)
        return True

    def export_task_history(self, filename):
        try:
            items = history.items()
            rv = len(items)
            if rv == 0:
                return HISTORY_ERR_EMPTY
            f = open(filename, 'w')
            f.write(HISTORY_SEPARATOR.join(HISTORY_HEADERS) + '\n')
            for x in items:
                f.write(
                    HISTORY_SEPARATOR.join(map(str, [
                        x.item_id,
                        time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(x.startup_time)),
                        '%.4f' % x.run_time,
                        x.task_name,
                        x.trigger_cond,
                        HISTORY_ENTRY_SUCCESS if x.success else HISTORY_ENTRY_FAILURE,
                        x.exit_code,
                        x.failure_reason if x.failure_reason else HISTORY_ENTRY_SUCCESS
                    ])) + "\n")
            f.close()
            return rv
        except IOError as e:
            return HISTORY_ERR_IOERROR

    def add_items(self, item_data):
        try:
            interpreter = ItemDataFileInterpreter(item_data)
            interpreter.create_items()
        except Exception as e:
            return _x(e)
        tasks.save()
        conditions.save()
        signal_handlers.save()
        return None

    def quit(self, _):
        self.before_shutdown()
        Notify.uninit()
        Gtk.main_quit()

    def pause(self, o):
        if o.get_active():
            applet_log.info("MAIN: pausing the scheduler")
            periodic.stop()
            if config.get('Scheduler', 'preserve pause'):
                create_pause_file()
            self.indicator.set_icon('alarm-off')
            self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        else:
            self.indicator.set_icon('alarm')
            self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            if config.get('Scheduler', 'preserve pause'):
                unlink_pause_file()
            periodic.start()
            applet_log.info("MAIN: scheduler resumed operation")

    def icon_change(self, name='alarm'):
        self.indicator.set_icon(name)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

    def icon_dialog(self, active=True):
        if active:
            name = 'alarm-add'
        else:
            if periodic.stopped:
                name = 'alarm-off'
            else:
                name = 'alarm'
        self.indicator.set_icon(name)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

    def dlgtask(self, _):
        if self.dialog_add_task:
            self.icon_dialog()
            applet_log.debug("MAIN: opening task dialog")
            self.dialog_add_task.run()
            self.icon_dialog(False)

    def dlgcondition(self, _):
        if self.dialog_add_condition:
            self.icon_dialog()
            applet_log.debug("MAIN: opening condition dialog")
            self.dialog_add_condition.run()
            self.icon_dialog(False)

    def dlgdbussignal(self, _):
        if self.dialog_add_dbus_signal:
            self.icon_dialog()
            applet_log.debug("MAIN: opening DBus signal definition dialog")
            self.dialog_add_dbus_signal.run()
            self.icon_dialog(False)

    def dlgabout(self, _):
        if self.dialog_about:
            applet_log.debug("MAIN: opening about dialog")
            self.dialog_about.run()

    def dlgsettings(self, _):
        if self.dialog_settings:
            self.icon_dialog()
            applet_log.debug("MAIN: opening settings dialog")
            self.dialog_settings.run()
            self.icon_dialog(False)

    def dlghistory(self, _):
        if self.dialog_history:
            applet_log.debug("MAIN: opening task history dialog")
            self.set_attention(False)
            self.dialog_history.run()

    def set_attention(self, warn=True):
        if warn and config.get('General', 'notifications'):
            self.indicator.set_status(AppIndicator.IndicatorStatus.ATTENTION)
        else:
            if periodic.stopped:
                self.indicator.set_icon('alarm-off')
                self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            else:
                self.indicator.set_icon('alarm')
                self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

    def hide_icon(self, hide=True):
        if hide:
            self.indicator.set_status(AppIndicator.IndicatorStatus.PASSIVE)
        else:
            self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

    def notify(self, message, icon='dialog-warning'):
        if config.get('General', 'notifications'):
            self._notify.update(APPLET_SHORTNAME, message, icon)
            self._notify.show()

    # TODO: use this instead of 'xprintidle' to save system resources
    def session_idle_seconds(self):
        return self.screensaver_mgr.getSessionIdleTime()

    def build_menu(self):
        menu = Gtk.Menu()

        if config.get('General', 'minimalistic mode'):
            minimalistic = True
        else:
            minimalistic = False

        if not minimalistic:
            item_newtask = Gtk.MenuItem(label=resources.MENU_EDIT_TASKS)
            item_newtask.connect('activate', self.dlgtask)
            item_newtask.show()
            menu.append(item_newtask)

        if not minimalistic:
            item_newcond = Gtk.MenuItem(label=resources.MENU_EDIT_CONDITIONS)
            item_newcond.connect('activate', self.dlgcondition)
            item_newcond.show()
            menu.append(item_newcond)

        item_settings = Gtk.MenuItem(label=resources.MENU_SETTINGS)
        item_settings.connect('activate', self.dlgsettings)
        item_settings.show()
        menu.append(item_settings)

        if not minimalistic:
            separator = Gtk.SeparatorMenuItem()
            separator.show()
            menu.append(separator)

        item_history = Gtk.MenuItem(label=resources.MENU_TASK_HISTORY)
        item_history.connect('activate', self.dlghistory)
        item_history.show()
        menu.append(item_history)

        if not minimalistic:
            separator = Gtk.SeparatorMenuItem()
            separator.show()
            menu.append(separator)

        item_pause = Gtk.CheckMenuItem(label=resources.MENU_PAUSE)
        if config.get('Scheduler', 'preserve pause') and check_pause_file():
            item_pause.set_active(True)
            self.indicator.set_icon('alarm-off')
            self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        item_pause.connect('activate', self.pause)
        item_pause.show()
        menu.append(item_pause)

        separator = Gtk.SeparatorMenuItem()
        separator.show()
        menu.append(separator)

        item_about = Gtk.MenuItem(label=resources.MENU_ABOUT)
        item_about.connect('activate', self.dlgabout)
        item_about.show()
        menu.append(item_about)

        item_quit = Gtk.MenuItem(label=resources.MENU_QUIT)
        item_quit.connect('activate', self.quit)
        item_quit.show()
        menu.append(item_quit)
        menu.show_all()
        return menu


# signal handler (see http://stackoverflow.com/questions/26388088): this is
# needed in order to handle the logout event (until it is managed by dbus)
def init_signal_handler(applet_instance):
    def signal_action(signum):
        if signum is signal.SIGHUP:
            applet_log.info("SIGHANDLER: caught SIGHUP")
        elif signum is signal.SIGINT:
            applet_log.info("SIGHANDLER: caught SIGINT")
        elif signum is signal.SIGTERM:
            applet_log.info("SIGHANDLER: caught SIGTERM")
        applet_instance.before_shutdown()

    def idle_handler(*args):
        applet_log.info("SIGHANDLER: handler activated (system)")
        GLib.idle_add(signal_action, priority=GLib.PRIORITY_HIGH)

    def handler(*args):
        applet_log.info("SIGHANDLER: handler activated (desktop)")
        signal_action(args[0])

    def install_glib_handler(signum):
        unix_signal_add = None
        if hasattr(GLib, 'unix_signal_add'):
            unix_signal_add = GLib.unix_signal_add
        elif hasattr(GLib, 'unix_signal_add_full'):
            unix_signal_add = GLib.unix_signal_add_full
        if unix_signal_add:
            applet_log.info("SIGHANDLER: register desktop handler for signal: %r" % signum)
            unix_signal_add(GLib.PRIORITY_HIGH, signum, handler, signum)
        else:
            applet_log.warning("SIGHANDLER: cannot install signal handler")

    SIGS = [getattr(signal, s, None) for s in "SIGINT SIGTERM SIGHUP".split()]
    for signum in SIGS:
        applet_log.info("SIGHANDLER: register system handler for signal: %r" % signum)
        signal.signal(signum, idle_handler)
        GLib.idle_add(install_glib_handler, signum, priority=GLib.PRIORITY_HIGH)


def set_applet_enabled_events(evts):
    global applet_enabled_events
    applet_enabled_events = evts


def get_applet_idle_seconds():
    if applet:
        return applet.session_idle_seconds()
    else:
        return 0


def kill_existing(verbose=False, shutdown=False):
    oerr(resources.OERR_SHUTDOWN_BEGIN %
         (resources.OERR_SHUTDOWN_SHUTDOWN if shutdown
          else resources.OERR_SHUTDOWN_KILL), verbose)
    bus = dbus.SessionBus()
    proxy = bus.get_object(APPLET_BUS_NAME, APPLET_BUS_PATH)
    try:
        if shutdown:
            proxy.quit_instance()
        else:
            proxy.kill_instance()
        oerr(resources.OERR_SHUTDOWN_FINISH, verbose)
    except dbus.exceptions.DBusException:
        oerr(resources.OERR_ERR_DBUS_SERVICE, verbose)


def oerr(s, verbose=True):
    if verbose:
        sys.stderr.write("%s: %s\n" % (APPLET_NAME, s))


def install_icons(overwrite=True):
    create_desktop_file(overwrite=overwrite)
    create_autostart_file(overwrite=overwrite)


# the horrible hack below is because no way was found to set the timeout for
# introspective DBus methods to infinite (that is: GObject.G_MAXINT)
def show_box(box='about', verbose=False):
    oerr(resources.OERR_SHOW_BOX % box, verbose)
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    proxy = Gio.DBusProxy.new_sync(bus, Gio.DBusProxyFlags.NONE, None,
                                   APPLET_BUS_NAME, APPLET_BUS_PATH,
                                   APPLET_BUS_NAME, None)
    try:
        proxy.call_sync('show_dialog', GLib.Variant('(s)', (box,)),
                        Gio.DBusCallFlags.NONE, GObject.G_MAXINT, None)
    except dbus.exceptions.DBusException:
        oerr(resources.OERR_ERR_DBUS_SERVICE, verbose)


def show_icon(show=True, running=True):
    if running:
        bus = dbus.SessionBus()
        proxy = bus.get_object(APPLET_BUS_NAME, APPLET_BUS_PATH)
        try:
            proxy.show_icon(show)
        except dbus.exceptions.DBusException:
            oerr(resources.OERR_ERR_DBUS_SERVICE, verbose)
    config.set('General', 'show icon', show)
    config.save()


def run_condition(cond_name, deferred, verbose=False):
    oerr(resources.OERR_RUN_CONDITION % cond_name, verbose)
    bus = dbus.SessionBus()
    proxy = bus.get_object(APPLET_BUS_NAME, APPLET_BUS_PATH)
    if not proxy.run_condition(cond_name, deferred):
        oerr(resources.OERR_RUN_CONDITION_FAIL % cond_name, verbose)
        return False
    else:
        return True


def export_running_history(filename, verbose=False):
    oerr(resources.OERR_EXPORT_HISTORY % filename, verbose)
    bus = dbus.SessionBus()
    proxy = bus.get_object(APPLET_BUS_NAME, APPLET_BUS_PATH)
    try:
        rv = proxy.export_history(filename)
    except dbus.exceptions.DBusException:
        oerr(resources.OERR_EXPORT_HISTORY_UNKNOWN, verbose)
        return False
    if rv < 0:
        if rv == HISTORY_ERR_EMPTY:
            s = resources.OERR_EXPORT_HISTORY_EMPTY
        elif rv == HISTORY_ERR_IOERROR:
            s = resources.OERR_EXPORT_HISTORY_IOERROR
        else:
            s = resources.OERR_EXPORT_HISTORY_UNKNOWN
        oerr(resources.OERR_EXPORT_HISTORY_FAIL % s, verbose)
        return False
    else:
        oerr(resources.OERR_EXPORT_HISTORY_FINISH % rv, verbose)
        return True


def call_add_items(filename, verbose=False):
    bus = dbus.SessionBus()
    proxy = bus.get_object(APPLET_BUS_NAME, APPLET_BUS_PATH)
    if filename == '-':
        applet_log.info("MAIN: reading items from standard input")
        data = sys.stdin.read()
    else:
        applet_log.info("MAIN: reading items from %s" % filename)
        try:
            with open(filename) as f:
                data = f.read()
        except Exception as e:
            oerr(resources.OERR_ITEMOPS_ADD_NOREAD, verbose)
            return False
    try:
        rv = proxy.add_items(data)
    except dbus.exceptions.DBusException:
        oerr(resources.OERR_ERR_ITEMOPS_DBUS, verbose)
        return False
    if rv:
        applet_log.error("MAIN: failed to add items: %s" % rv)
        oerr(resources.OERR_ITEMOPS_ADD_FAIL, verbose)
        return False
    else:
        applet_log.info("MAIN: items added successfully")
        return True


def do_add_items(filename, verbose=False):
    if filename == '-':
        applet_log.info("MAIN: reading items from standard input")
        data = sys.stdin.read()
    else:
        applet_log.info("MAIN: reading items from %s" % filename)
        try:
            with open(filename) as f:
                data = f.read()
        except Exception as e:
            oerr(resources.OERR_ITEMOPS_ADD_NOREAD, verbose)
            return False
    try:
        tasks.load()
    except FileNotFoundError:
        pass
    try:
        conditions.load()
    except FileNotFoundError:
        pass
    try:
        signal_handlers.load()
    except FileNotFoundError:
        pass
    try:
        interpreter = ItemDataFileInterpreter(data)
        interpreter.create_items()
    except Exception as e:
        applet_log.error("MAIN: failed to add items: %s" % _x(e))
        oerr(resources.OERR_ITEMOPS_ADD_FAIL, verbose)
        return False
    tasks.save()
    conditions.save()
    signal_handlers.save()
    applet_log.info("MAIN: items added successfully")
    return True


def call_remove_item(item_spec, verbose=False):
    # TODO: the symbols should be converted to constants
    bus = dbus.SessionBus()
    proxy = bus.get_object(APPLET_BUS_NAME, APPLET_BUS_PATH)
    try:
        rv = proxy.del_item(item_spec)
    except dbus.exceptions.DBusException:
        oerr(resources.OERR_ERR_ITEMOPS_DBUS, verbose)
        return False
    if rv:
        li = rv.split('/')
        if len(li) > 1:
            oerr(resources.OERR_ITEMOPS_DEL_FAIL %
                 resources.OERR_ERR_ITEMOPS_DBUS, verbose)
            return False
        elif len(li) == 1:
            try:
                item_type, item_name, errcode = li[0].split(':')
                errcode = int(errcode)
                if errcode == ITEM_OPERATION_OK:
                    reason = resources.OERR_ERR_ITEMOPS_OK
                elif errcode == ITEM_OPERATION_ERR_TYPE:
                    reason = resources.OERR_ERR_ITEMOPS_OK
                elif errcode == ITEM_OPERATION_ERR_NOTFOUND:
                    reason = resources.OERR_ERR_ITEMOPS_NOTFOUND
                elif errcode == ITEM_OPERATION_ERR_CONFLICT:
                    reason = resources.OERR_ERR_ITEMOPS_CONFLICT
                else:
                    reason = resources.OERR_ERR_ITEMOPS_GENERIC
            except ValueError:
                reason = resources.OERR_ERR_ITEMOPS_DBUS
            oerr(resources.OERR_ITEMOPS_DEL_FAIL % reason, verbose)
            return False
    else:
        oerr(resources.OERR_ITEMOPS_DEL_FINISH % item_spec, verbose)
        return True


def do_remove_item(item_spec, verbose=False):
    try:
        tasks.load()
    except FileNotFoundError:
        pass
    try:
        conditions.load()
    except FileNotFoundError:
        pass
    try:
        signal_handlers.load()
    except FileNotFoundError:
        pass
    li = remove_item_specs(item_spec)
    if len(li) > 1:
        oerr(resources.OERR_ITEMOPS_DEL_FAIL %
             resources.OERR_ERR_ITEMOPS_DBUS, verbose)
        return False
    elif len(li) == 1:
        try:
            item_type, item_name, errcode = li[0]
            errcode = int(errcode)
            if errcode == ITEM_OPERATION_OK:
                reason = resources.OERR_ERR_ITEMOPS_OK
            elif errcode == ITEM_OPERATION_ERR_TYPE:
                reason = resources.OERR_ERR_ITEMOPS_OK
            elif errcode == ITEM_OPERATION_ERR_NOTFOUND:
                reason = resources.OERR_ERR_ITEMOPS_NOTFOUND
            elif errcode == ITEM_OPERATION_ERR_CONFLICT:
                reason = resources.OERR_ERR_ITEMOPS_CONFLICT
            else:
                reason = resources.OERR_ERR_ITEMOPS_GENERIC
        except ValueError:
            reason = resources.OERR_ERR_ITEMOPS_DBUS
        oerr(resources.OERR_ITEMOPS_DEL_FAIL % reason, verbose)
        return False
    else:
        oerr(resources.OERR_ITEMOPS_DEL_FINISH % item_spec, verbose)
        return True


def print_items(item_type=None):
    if item_type is not None:
        if item_type == ITEM_TYPE_TASKS:
            try:
                tasks.load()
                for name in tasks.names:
                    sys.stdout.write("%s:%s\n" % (ITEM_TYPE_TASKS, name))
            except FileNotFoundError:
                pass
            return ITEM_OPERATION_OK
        elif item_type == ITEM_TYPE_CONDITIONS:
            try:
                conditions.load()
                for name in conditions.names:
                    sys.stdout.write("%s:%s\n" % (ITEM_TYPE_CONDITIONS, name))
            except FileNotFoundError:
                pass
            return ITEM_OPERATION_OK
        elif item_type == ITEM_TYPE_SIGNAL_HANDLERS:
            try:
                signal_handlers.load()
                for name in signal_handlers.names:
                    sys.stdout.write(
                        "%s:%s\n" % (ITEM_TYPE_SIGNAL_HANDLERS, name))
            except FileNotFoundError:
                pass
            return ITEM_OPERATION_OK
        else:
            return ITEM_OPERATION_ERR_TYPE
    else:
        try:
            tasks.load()
            for name in tasks.names:
                sys.stdout.write("%s:%s\n" % (ITEM_TYPE_TASKS, name))
        except FileNotFoundError:
            pass
        try:
            conditions.load()
            for name in conditions.names:
                sys.stdout.write("%s:%s\n" % (ITEM_TYPE_CONDITIONS, name))
        except FileNotFoundError:
            pass
        try:
            signal_handlers.load()
            for name in signal_handlers.names:
                sys.stdout.write("%s:%s\n" % (ITEM_TYPE_SIGNAL_HANDLERS, name))
        except FileNotFoundError:
            pass
        return ITEM_OPERATION_OK


def clear_item_data(verbose=False):
    oerr(resources.OERR_CLEAR_DATA, verbose)
    try:
        tasks.load()
    except FileNotFoundError:
        tasks.save()
    try:
        conditions.load()
    except FileNotFoundError:
        conditions.save()
    try:
        signal_handlers.load()
    except FileNotFoundError:
        signal_handlers.save()
    l = list(conditions.names)
    for x in l:
        conditions.remove(cond_name=x)
    conditions.save()
    file_name = os.path.join(USER_CONFIG_FOLDER, FILE_CONFIG_LIST_CONDITIONS)
    try:
        os.unlink(file_name)
    except OSError:
        oerr(resources.OERR_CLEAR_DATA_CONDFAIL, verbose)
    l = list(tasks.names)
    for x in l:
        tasks.remove(task_name=x)
    tasks.save()
    file_name = os.path.join(USER_CONFIG_FOLDER, FILE_CONFIG_LIST_TASKS)
    try:
        os.unlink(file_name)
    except OSError:
        oerr(resources.OERR_CLEAR_DATA_TASKFAIL, verbose)
    l = list(signal_handlers.names)
    for x in l:
        signal_handlers.remove(handler_name=x)
    signal_handlers.save()
    file_name = os.path.join(
        USER_CONFIG_FOLDER, FILE_CONFIG_LIST_SIGNAL_HANDLERS)
    try:
        os.unlink(file_name)
    except OSError:
        oerr(resources.OERR_CLEAR_DATA_SIGFAIL, verbose)


def export_item_data(filename=None, verbose=False):
    task_dict_list = []
    condition_dict_list = []
    signal_handler_dict_list = []
    try:
        tasks.load()
    except FileNotFoundError:
        tasks.save()
    try:
        conditions.load()
    except FileNotFoundError:
        conditions.save()
    try:
        signal_handlers.load()
    except FileNotFoundError:
        signal_handlers.save()
    for name in tasks.names:
        t = tasks.get(task_name=name)
        d = Task_to_dict(t)
        task_dict_list.append(d)
    for name in conditions.names:
        c = conditions.get(cond_name=name)
        condtype = type(c)
        if condtype == EventBasedCondition:
            d = EventBasedCondition_to_dict(c)
        elif condtype == IdleTimeBasedCondition:
            d = IdleTimeBasedCondition_to_dict(c)
        elif condtype == CommandBasedCondition:
            d = CommandBasedCondition_to_dict(c)
        elif condtype == TimeBasedCondition:
            d = TimeBasedCondition_to_dict(c)
        elif condtype == IntervalBasedCondition:
            d = IntervalBasedCondition_to_dict(c)
        # TODO: add further condition type converters here
        elif condtype == PathNotifyBasedCondition:
            d = PathNotifyBasedCondition_to_dict(c)
        else:
            d = Condition_to_dict(c)
        condition_dict_list.append(d)
    for name in signal_handlers.names:
        t = signal_handlers.get(handler_name=name)
        d = SignalHandler_to_dict(t)
        signal_handler_dict_list.append(d)
    oerr(resources.OERR_EXPORT_DATA_BEGIN, verbose)
    oerr(resources.OERR_EXPORT_DATA_TASKS % len(task_dict_list), verbose)
    oerr(resources.OERR_EXPORT_DATA_CONDITIONS
         % len(condition_dict_list), verbose)
    oerr(resources.OERR_EXPORT_DATA_SIGHANDLERS
         % len(signal_handler_dict_list), verbose)
    json_dic = {
        'tasks': task_dict_list,
        'conditions': condition_dict_list,
        'signalhandlers': signal_handler_dict_list,
    }
    if not filename:
        filename = os.path.join(USER_CONFIG_FOLDER, '%s.dump' % APPLET_NAME)
    with open(filename, 'w') as f:
        json.dump(json_dic, f, indent=2)
    oerr(resources.OERR_EXPORT_DATA_FINISH % filename, verbose)


def import_item_data(filename=None, verbose=False):
    if not filename:
        filename = os.path.join(USER_CONFIG_FOLDER, '%s.dump' % APPLET_NAME)
    oerr(resources.OERR_IMPORT_DATA % filename, verbose)
    try:
        with open(filename, 'r') as f:
            json_dic = json.load(f)
    except:
        oerr(resources.OERR_IMPORT_DATA_FAIL)
        sys.exit(2)
    clear_item_data(verbose)
    oerr(resources.OERR_IMPORT_DATA_BEGIN, verbose)
    if 'tasks' in json_dic.keys():
        for task_dic in json_dic['tasks']:
            task = dict_to_Task(task_dic)
            tasks.add(task)
        oerr(resources.OERR_IMPORT_DATA_TASKS
             % len(json_dic['tasks']), verbose)
    if 'conditions' in json_dic.keys():
        for condition_dic in json_dic['conditions']:
            condition = None
            condtype = condition_dic['subtype']
            if condtype == 'IntervalBasedCondition':
                condition = dict_to_IntervalBasedCondition(condition_dic)
            elif condtype == 'TimeBasedCondition':
                condition = dict_to_TimeBasedCondition(condition_dic)
            elif condtype == 'CommandBasedCondition':
                condition = dict_to_CommandBasedCondition(condition_dic)
            elif condtype == 'IdleTimeBasedCondition':
                condition = dict_to_IdleTimeBasedCondition(condition_dic)
            elif condtype == 'EventBasedCondition':
                condition = dict_to_EventBasedCondition(condition_dic)
            # TODO: add further condition loaders here
            elif condtype == 'PathNotifyBasedCondition':
                condition = dict_to_PathNotifyBasedCondition(condition_dic)
            else:
                condition = dict_to_Condition(condition_dic)
            if condition:
                conditions.add(condition)
        oerr(resources.OERR_IMPORT_DATA_CONDITIONS
             % len(json_dic['conditions']), verbose)
    if 'signalhandlers' in json_dic.keys():
        for handler_dic in json_dic['signalhandlers']:
            handler = dict_to_SignalHandler(handler_dic)
            signal_handlers.add(handler)
        oerr(resources.OERR_IMPORT_DATA_SIGHANDLERS
             % len(json_dic['signalhandlers']), verbose)
    tasks.save()
    conditions.save()
    signal_handlers.save()
    oerr(resources.OERR_IMPORT_DATA_FINISH, verbose)


# Configure services and start the application
def gui_applet_main():
    init_signal_handler(applet)
    # signal.signal(signal.SIGINT, signal.SIG_DFL)
    preserve_pause = config.get('Scheduler', 'preserve pause')
    if not (preserve_pause and check_pause_file()):
        periodic.start()
    # the following two cases should be useless, but do some cleanup anyway
    elif not preserve_pause:
        unlink_pause_file()
    else:
        periodic.stop()
    # start the threaded file notifier if enabled
    if watch_path_notifier is not None:
        watch_path_notifier.start()
    # If we have come here, the command line had no arguments so we clear it
    applet.run([])
    if watch_path_notifier is not None:
        watch_path_notifier.stop()
    if not periodic.stopped:
        periodic.stop()


# the main() function enables running the applet via an import
def main():
    global config
    global tasks
    global conditions
    global signal_handlers
    global history
    global applet
    global periodic
    global main_dbus_loop
    global watch_path_manager
    global watch_path_notifier
    global deferred_events
    global deferred_watch_paths
    global ui_add_task
    global ui_add_condition
    global ui_settings
    global ui_task_history
    global ui_about
    global ui_add_signal

    if GRAPHIC_ENVIRONMENT:
        main_dbus_loop = DBusGMainLoop(set_as_default=True)
        GObject.threads_init()

    # check user folders and configure applet
    verify_user_folders()
    config = Config()
    config_loghandler()
    config_loglevel()

    # load dialog boxes
    if not config.get('General', 'minimalistic mode'):
        minimalistic = False
        ui_add_task = load_applet_dialog('when-command-edit-task')
        ui_add_condition = load_applet_dialog('when-command-edit-condition')
        ui_settings = load_applet_dialog('when-command-settings')
        ui_task_history = load_applet_dialog('when-command-task-history')
        ui_about = load_applet_dialog('when-command-about')
        ui_add_signal = load_applet_dialog('when-command-edit-dbus-signal')
    else:
        minimalistic = True
        ui_settings = load_applet_dialog('when-command-settings')
        ui_task_history = load_applet_dialog('when-command-task-history')
        ui_about = load_applet_dialog('when-command-about')

    # create main collections
    tasks = Tasks()
    conditions = Conditions()
    signal_handlers = SignalHandlers()
    applet = AppletIndicator()

    if len(sys.argv) == 1:
        if not GRAPHIC_ENVIRONMENT:
            oerr(resources.OERR_ERR_REQUIRE_DESKTOP)
            sys.exit(2)

        if applet.get_is_remote():
            oerr(resources.OERR_ERR_ALREADY_RUNNING)
            sys.exit(2)

        applet_log.info("MAIN: starting %s version %s" % (APPLET_FULLNAME, APPLET_VERSION))
        if FILE_NOTIFY_ENABLED:
            applet_log.info("MAIN: optional file notifications can be enabled")

        # if pyinotify was imported and enabled, activate watch path manager
        if FILE_NOTIFY_ENABLED and config.get('General', 'file notifications'):
            class LocalEventHandler(pyinotify.ProcessEvent):
                def process_default(self, event):
                    if event.mask & FN_IN_MODIFY_EVENTS:
                        applet_log.debug("PATHNOTIFY: notifying changes (%s) in %s" % (event.maskname, event.pathname))
                        deferred_watch_paths.append(event.pathname)
                    else:
                        applet_log.debug("PATHNOTIFY: event ignored (%s) for %s" % (event.maskname, event.pathname))
            watch_path_manager = pyinotify.WatchManager()
            watch_path_notifier = pyinotify.ThreadedNotifier(
                watch_path_manager, LocalEventHandler())
            applet_log.debug("MAIN: filesystem change based conditions are enabled")

        # initialize global variables that require running environment
        periodic = Periodic(config.get('Scheduler', 'tick seconds'),
                            periodic_condition_check, autostart=False)
        history = HistoryQueue()
        deferred_events = DeferredEvents()
        deferred_watch_paths = DeferredWatchPaths()
        create_desktop_file(False)
        create_autostart_file(False)
        gui_applet_main()

    else:
        parser = argparse.ArgumentParser(
            prog=APPLET_NAME,
            description=resources.COMMAND_LINE_PREAMBLE,
            epilog=resources.COMMAND_LINE_EPILOG,
        )
        parser.add_argument(
            '-v', '--verbose',
            dest='verbose', action='store_true',
            help=resources.COMMAND_LINE_HELP_VERBOSE
        )
        parser.add_argument(
            '-V', '--version',
            dest='version', action='store_true',
            help=resources.COMMAND_LINE_HELP_VERSION
        )
        parser.add_argument(
            '-s', '--show-settings',
            dest='show_settings', action='store_true',
            help=resources.COMMAND_LINE_HELP_SHOW_SETTINGS
        )
        parser.add_argument(
            '-l', '--show-history',
            dest='show_history', action='store_true',
            help=resources.COMMAND_LINE_HELP_SHOW_HISTORY
        )
        parser.add_argument(
            '-t', '--show-tasks',
            dest='show_tasks', action='store_true',
            help=resources.COMMAND_LINE_HELP_SHOW_TASKS
        )
        parser.add_argument(
            '-c', '--show-conditions',
            dest='show_conditions', action='store_true',
            help=resources.COMMAND_LINE_HELP_SHOW_CONDITIONS
        )
        parser.add_argument(
            '-d', '--show-signals',
            dest='show_dbus_signals', action='store_true',
            help=resources.COMMAND_LINE_HELP_SHOW_DBUS_SIGNALS
        )
        parser.add_argument(
            '-R', '--reset-config',
            dest='reset_config', action='store_true',
            help=resources.COMMAND_LINE_HELP_RESET_CONFIG
        )
        parser.add_argument(
            '-I', '--show-icon',
            dest='show_icon', action='store_true',
            help=resources.COMMAND_LINE_HELP_SHOW_ICON
        )
        parser.add_argument(
            '-C', '--clear',
            dest='clear', action='store_true',
            help=resources.COMMAND_LINE_HELP_CLEAR
        )
        parser.add_argument(
            '-T', '--install',
            dest='install', action='store_true',
            help=resources.COMMAND_LINE_HELP_INSTALL
        )
        parser.add_argument(
            '-Q', '--query',
            dest='query', action='store_true',
            help=resources.COMMAND_LINE_HELP_QUERY
        )
        parser.add_argument(
            '-H', '--export-history',
            dest='export_history', metavar='FILE', default=None,
            help=resources.COMMAND_LINE_HELP_EXPORT_HISTORY
        )
        parser.add_argument(
            '-r', '--run-condition',
            dest='run_condition', metavar='CONDITION', default=None,
            help=resources.COMMAND_LINE_HELP_RUN_CONDITION
        )
        parser.add_argument(
            '-f', '--defer-condition',
            dest='defer_condition', metavar='CONDITION', default=None,
            help=resources.COMMAND_LINE_HELP_DEFER_CONDITION
        )
        parser.add_argument(
            '--item-list',
            dest='item_list', metavar='ITEMTYPE', nargs='?', const='*',
            help=resources.COMMAND_LINE_HELP_ITEM_LIST
        )
        parser.add_argument(
            '--item-del',
            dest='item_delete', metavar='ITEMSPEC', default=None,
            help=resources.COMMAND_LINE_HELP_ITEM_DELETE
        )
        parser.add_argument(
            '--item-add',
            dest='item_add', metavar='FILE', nargs='?', const='-',
            help=resources.COMMAND_LINE_HELP_ITEM_ADD
        )
        parser.add_argument(
            '--export',
            dest='export_items', metavar='FILE', nargs='?', const='*',
            help=resources.COMMAND_LINE_HELP_EXPORT
        )
        parser.add_argument(
            '--import',
            dest='import_items', metavar='FILE', nargs='?', const='*',
            help=resources.COMMAND_LINE_HELP_IMPORT
        )
        parser.add_argument(
            '--shutdown',
            dest='shutdown', action='store_true',
            help=resources.COMMAND_LINE_HELP_SHUTDOWN
        )
        parser.add_argument(
            '--kill',
            dest='kill', action='store_true',
            help=resources.COMMAND_LINE_HELP_KILL
        )

        args = parser.parse_args()
        verbose = args.verbose

        running = False
        if GRAPHIC_ENVIRONMENT:
            running = applet.get_is_remote()

        if args.version:
            print(resources.COMMAND_LINE_SHOWVERSION
                  % (APPLET_NAME, APPLET_FULLNAME, APPLET_VERSION))
            if verbose and running:
                show_box('about', False)

        if args.show_icon:
            show_icon(True, running)

        if args.show_settings:
            if not running:
                oerr(resources.OERR_ERR_REQUIRE_INSTANCE, verbose)
                sys.exit(2)
            else:
                show_box('settings', verbose)
        elif args.show_history:
            if not running:
                oerr(resources.OERR_ERR_REQUIRE_INSTANCE, verbose)
                sys.exit(2)
            else:
                show_box('history', verbose)
        elif args.show_tasks:
            if not running:
                oerr(resources.OERR_ERR_REQUIRE_INSTANCE, verbose)
                sys.exit(2)
            elif minimalistic:
                oerr(resources.OERR_ERR_MINIMALISTIC, verbose)
                sys.exit(2)
            else:
                show_box('task', verbose)
        elif args.show_conditions:
            if not running:
                oerr(resources.OERR_ERR_REQUIRE_INSTANCE, verbose)
                sys.exit(2)
            elif minimalistic:
                oerr(resources.OERR_ERR_MINIMALISTIC, verbose)
                sys.exit(2)
            else:
                show_box('condition', verbose)
        elif args.show_dbus_signals:
            if not running:
                oerr(resources.OERR_ERR_REQUIRE_INSTANCE, verbose)
                sys.exit(2)
            elif minimalistic:
                oerr(resources.OERR_ERR_MINIMALISTIC, verbose)
                sys.exit(2)
            else:
                if not config.get('General', 'user events'):
                    oerr(resources.OERR_ERR_DBUS_DISABLED, verbose)
                    sys.exit(1)
                show_box('dbus_signal', verbose)

        if args.export_items:
            if args.export_items == '*':
                filename = None
            else:
                filename = args.export_items
            try:
                export_item_data(filename, verbose)
            except Exception as e:
                applet_log.critical("MAIN: exception %s occurred while performing 'export'" % _x(e))
                oerr(resources.OERR_ERR_EXPORT_GENERIC, verbose)
                sys.exit(2)
            oerr(resources.OERR_EXPORT, verbose)

        if args.export_history:
            if not running:
                oerr(resources.OERR_ERR_DBUS_DISABLED, verbose)
                sys.exit(2)
            else:
                filename = os.path.realpath(args.export_history)
                if not export_running_history(filename, verbose):
                    sys.exit(2)

        if args.run_condition:
            if not running:
                oerr(resources.OERR_ERR_DBUS_DISABLED, verbose)
                sys.exit(2)
            else:
                if not(run_condition(args.run_condition, False, verbose)):
                    sys.exit(2)
        if args.defer_condition:
            if not running:
                oerr(resources.OERR_ERR_DBUS_DISABLED, verbose)
                sys.exit(2)
            else:
                if not(run_condition(args.defer_condition, True, verbose)):
                    sys.exit(2)

        if args.item_delete:
            if running:
                if not call_remove_item(args.item_delete, verbose):
                    sys.exit(2)
            else:
                if not do_remove_item(args.item_delete, verbose):
                    sys.exit(2)

        if args.item_add:
            if running:
                if not call_add_items(args.item_add, verbose):
                    sys.exit(2)
            else:
                if not do_add_items(args.item_add, verbose):
                    sys.exit(2)

        if args.item_list:
            if args.item_list == '*':
                print_items()
            else:
                s = args.item_list.lower()
                if ITEM_TYPE_TASKS.startswith(s):
                    s = ITEM_TYPE_TASKS
                elif ITEM_TYPE_CONDITIONS.startswith(s):
                    s = ITEM_TYPE_CONDITIONS
                elif ITEM_TYPE_SIGNAL_HANDLERS.startswith(s):
                    s = ITEM_TYPE_SIGNAL_HANDLERS
                else:
                    oerr(resources.OERR_ERR_ITEMOPS_TYPE, verbose)
                    sys.exit(1)
                if print_items(s) != ITEM_OPERATION_OK:
                    oerr(resources.OERR_ERR_ITEMOPS_GENERIC, verbose)
                    sys.exit(2)

        if args.shutdown:
            if running:
                kill_existing(verbose=verbose, shutdown=True)
                running = False
            else:
                oerr(resources.OERR_ERR_NO_INSTANCE, verbose)
                sys.exit(1)
        elif args.kill:
            if running:
                kill_existing(verbose=verbose, shutdown=False)
                running = False
            else:
                oerr(resources.OERR_ERR_NO_INSTANCE, verbose)
                sys.exit(1)

        if args.reset_config:
            if running:
                oerr(resources.OERR_ERR_RESET_RUNNING, verbose)
                sys.exit(2)
            else:
                try:
                    config.reset()
                    unlink_pause_file()
                except Exception as e:
                    applet_log.critical("MAIN: exception %s occurred while performing 'reset-config'" % _x(e))
                    oerr(resources.OERR_ERR_RESET_GENERIC, verbose)
                    sys.exit(2)
                oerr(resources.OERR_RESET, verbose)

        if args.clear:
            if running:
                oerr(resources.OERR_ERR_CLEAR_RUNNING, verbose)
                sys.exit(2)
            else:
                try:
                    clear_item_data(verbose)
                except Exception as e:
                    applet_log.critical("MAIN: exception %s occurred while performing 'clear'" % _x(e))
                    oerr(resources.OERR_ERR_CLEAR_GENERIC, verbose)
                    sys.exit(2)
                oerr(resources.OERR_CLEAR, verbose)

        if args.import_items:
            if running:
                oerr(resources.OERR_ERR_IMPORT_RUNNING, verbose)
                sys.exit(2)
            else:
                if args.import_items == '*':
                    filename = None
                else:
                    filename = args.import_items
                try:
                    import_item_data(filename, verbose)
                except Exception as e:
                    applet_log.critical("MAIN: exception %s occurred while performing 'import'" % _x(e))
                    oerr(resources.OERR_ERR_IMPORT_GENERIC, verbose)
                    sys.exit(2)

        if args.install:
            if running:
                oerr(resources.OERR_ERR_INSTALL_RUNNING, verbose)
                sys.exit(2)
            else:
                try:
                    install_icons(True)
                except Exception as e:
                    applet_log.critical("MAIN: exception %s occurred while performing 'install'" % _x(e))
                    oerr(resources.OERR_ERR_INSTALL_GENERIC, verbose)
                    sys.exit(2)
                oerr(resources.OERR_INSTALL, verbose)

        if args.query:
            if running:
                oerr(resources.OERR_FOUND_INSTANCE, verbose)
                sys.exit(0)
            else:
                oerr(resources.OERR_NO_INSTANCE, verbose)
                sys.exit(1)


# Build the applet and start
if __name__ == '__main__':
    main()


# end.
