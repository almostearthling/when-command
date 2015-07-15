#!/usr/bin/env python3
#
# When
#
# Copyright (c) 2015 Francesco Garosi
# Released under the BSD License (see LICENSE.md)
#
# Small startup application that runs tasks when particular conditions are met.
#
#############################################################################
# SOME NOTES ABOUT THE CODE
# The code tries to follow the usual guidelines for Python 3.x, and takes
# inspiration from other Gnome applets that sit in the indicator tray.
# I tried to reduce the comments to the very least, and let the code speak
# for itself. Some of the conventions here are the following:
#
# * system wide constants are spelled in all uppercase (as usual in C/C++)
# * variables tend to be all lowercase, both globals and locals
# * class names start with an uppercase letter and are in camelcase
# * global instances of classes are lowercase
# * private members start, as usual, with an underscore
# * function names are all lowercase with underscores
# * transitional (or debug) functions start with underscores
# * the core classes implement their own loggers, borrowing from global
# * user interaction strings (as log messages) use double quotes
# * program internal strings use single quotes
# * log messages mostly sport a prefix to determine what part generated them
# * log messages containing the NTBS strings are *never to be seen*
# * commented functions are due to be removed soon
# * classes don't expose variables directly, but will after some debugging

from gi.repository import GLib, Gtk, Gio
from gi.repository import GObject
from gi.repository import AppIndicator3 as AppIndicator
from gi.repository import Notify
from gi.repository import Pango

import os
import sys
import time
import signal
import subprocess
import threading
import configparser
import pickle
import logging
import logging.config
import logging.handlers
import shutil

import dbus
from dbus.mainloop.glib import DBusGMainLoop

from concurrent.futures import ThreadPoolExecutor

from collections import OrderedDict, deque, namedtuple


#############################################################################
# constants

# base constants
APPLET_NAME = 'when-command'
APPLET_FULLNAME = "When Gnome Scheduler"
APPLET_SHORTNAME = "When"
APPLET_VERSION = "0.2.0-beta.2"
APPLET_ID = "it.jks.WhenCommand"

# logging constants
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_MAX_BACKUPS = 4

# action constants
ACTION_OK = 0
ACTION_CANCEL = -1
ACTION_DELETE = 9

# folders
USER_FOLDER = os.path.expanduser('~')
USER_DATA_FOLDER = os.path.join(USER_FOLDER, '.local', 'share', APPLET_NAME)
USER_LAUNCHER_FOLDER = os.path.join(USER_FOLDER, '.local', 'share', 'applications')
USER_AUTOSTART_FOLDER = os.path.join(USER_FOLDER, '.config', 'autostart')
USER_CONFIG_FOLDER = os.path.join(USER_FOLDER, '.config', APPLET_NAME)
USER_LOG_FOLDER = os.path.join(USER_DATA_FOLDER, 'log')
USER_LOG_FILE = os.path.join(USER_LOG_FOLDER, "%s.log" % APPLET_NAME)
USER_CONFIG_FILE = os.path.join(USER_CONFIG_FOLDER, "%s.conf" % APPLET_NAME)
USER_PAUSE_FILE = os.path.join(USER_CONFIG_FOLDER, "%s.pause" % APPLET_NAME)


# verify that the user folders are present, otherwise create them
def verify_user_folders():
    if not os.path.exists(USER_DATA_FOLDER):
        os.mkdir(USER_DATA_FOLDER)
    if not os.path.exists(USER_LOG_FOLDER):
        os.mkdir(USER_LOG_FOLDER)
    if not os.path.exists(USER_CONFIG_FOLDER):
        os.mkdir(USER_CONFIG_FOLDER)

verify_user_folders()


#############################################################################
# Support these installation schemes:
#
# * default: LSB standard (/usr/bin/when-applet, /usr/share/when-applet/*)
# * /opt based (/opt/when-applet/when-applet, /opt/when-applet/share/*)
# * LSB local (/usr/local/bin/when-applet, /usr/local/share/when-applet/*)
# * $HOME generic (~/.local/bin/when-applet, ~/.local/when-applet/share/*)
# * own folder ($FOLDER/when-applet, $FOLDER/share/*)
#
# where the first element is the invoked command, the second one is the
# prefix of the applet data folder (where dialogs, icons and other resources
# have to be installed); icons have their own subtree in the data folder
APP_BASE_FOLDER = '/usr'
APP_BIN_FOLDER = os.path.join(APP_BASE_FOLDER, 'bin')
APP_DATA_FOLDER = os.path.join(APP_BASE_FOLDER, 'share', APPLET_NAME)
APP_ICON_FOLDER = os.path.join(APP_DATA_FOLDER, 'icons')

INVOKED_CMD = sys.argv[0]
INVOKED_DIR = os.path.dirname(INVOKED_CMD)
if INVOKED_DIR == os.path.join('/opt', APPLET_NAME):
    APP_BIN_FOLDER = INVOKED_DIR
    APP_BASE_FOLDER = INVOKED_DIR
    APP_DATA_FOLDER = os.path.join(APP_BASE_FOLDER, 'share')
    APP_ICON_FOLDER = os.path.join(APP_DATA_FOLDER, 'icons')
elif INVOKED_DIR == '/usr/local/bin':
    APP_BASE_FOLDER = '/usr/local'
    APP_BIN_FOLDER = INVOKED_DIR
    APP_DATA_FOLDER = os.path.join(APP_BASE_FOLDER, 'share', APPLET_NAME)
    APP_ICON_FOLDER = os.path.join(APP_DATA_FOLDER, 'icons')
elif INVOKED_DIR == os.path.join(USER_FOLDER, '.local', 'bin'):
    APP_BIN_FOLDER = INVOKED_DIR
    APP_BASE_FOLDER = USER_DATA_FOLDER
    APP_DATA_FOLDER = os.path.join(USER_DATA_FOLDER)
    APP_ICON_FOLDER = os.path.join(USER_DATA_FOLDER, 'icons')
elif not INVOKED_DIR.startswith('/usr'):
    APP_BIN_FOLDER = INVOKED_DIR
    APP_BASE_FOLDER = INVOKED_DIR
    APP_DATA_FOLDER = os.path.join(APP_BASE_FOLDER, 'share')
    APP_ICON_FOLDER = os.path.join(APP_DATA_FOLDER, 'icons')

# update Python path
sys.path.insert(0, APP_DATA_FOLDER)


# dialog boxes
def load_applet_dialog(name):
    base = os.path.dirname(sys.argv[0])
    with open(os.path.join(APP_DATA_FOLDER, '%s.glade' % name)) as f:
        dialog_xml = f.read()
    return dialog_xml


# actual dialog box definitions (could be packed in .py files)
DIALOG_ADD_TASK = load_applet_dialog('when-command-edit-task')
DIALOG_ADD_CONDITION = load_applet_dialog('when-command-edit-condition')
DIALOG_SETTINGS = load_applet_dialog('when-command-settings')
DIALOG_TASK_HISTORY = load_applet_dialog('when-command-task-history')
DIALOG_ABOUT = load_applet_dialog('when-command-about')


# resource strings (consider making a module out of them)
class Resources(object):
    pass
resources = Resources()
resources.DLG_CONFIRM_DELETE_TASK = "Are you sure you want to delete task %s?"
resources.DLG_CONFIRM_DELETE_CONDITION = "Are you sure you want to delete condition %s?"
resources.DLG_CANNOT_DELETE_TASK = "Task %s could not be deleted."
resources.DLG_CANNOT_DELETE_CONDITION = "Condition %s could not be deleted."
resources.DLG_CANNOT_FIND_TASK = "Task %s could not be found."
resources.DLG_CANNOT_FIND_CONDITION = "Condition %s could not be found."
resources.DLG_WRONG_EXIT_STATUS = "Wrong value for exit status specified.\nPlease consider reviewing it."
resources.DLG_ABOUT_VERSION_STRING = "Version: %s"

resources.NOTIFY_TASK_FAILED = "Task failed: %s"

resources.MENU_EDIT_TASKS = "Edit Tasks..."
resources.MENU_EDIT_CONDITIONS = "Edit Conditions..."
resources.MENU_SETTINGS = "Settings..."
resources.MENU_TASK_HISTORY = "Task History..."
resources.MENU_PAUSE = "Pause"
resources.MENU_ABOUT = "About..."
resources.MENU_QUIT = "Quit"

resources.LISTCOL_ENVVARS_NAME = "Variable"
resources.LISTCOL_ENVVARS_VALUE = "Value"
resources.LISTCOL_TASKS_NAME = "Task Name"
resources.LISTCOL_HISTORY_TIMESTAMP = "Time / Duration"
resources.LISTCOL_HISTORY_TASK = "Task Name"
resources.LISTCOL_HISTORY_TRIGGER = "Trigger"
resources.LISTCOL_HISTORY_EXITCODE = "Exit Code"
resources.LISTCOL_HISTORY_SUCCESS = "Result"
resources.LISTCOL_HISTORY_REASON = "Reason"
resources.LISTCOL_HISTORY_ROWID = "Row ID"


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


# utility to create a desktop file
def create_desktop_file(overwrite=False):
    filename = "%s.desktop" % APPLET_NAME
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
                os.symlink(pathname, os.path.join(USER_LAUNCHER_FOLDER, filename))
            except Error:
                applet_log.error("MAIN: could not create the launcher")


# utility to create the autostart file
def create_autostart_file(overwrite=True):
    filename = "%s-startup.desktop" % APPLET_NAME
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
            except Error:
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


# logger
applet_log_handler = logging.NullHandler()
applet_log_formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
applet_log_handler.setFormatter(applet_log_formatter)
applet_log = logging.getLogger(APPLET_NAME)
applet_log.addHandler(applet_log_handler)


def config_loglevel(level=None):
    if level is None:
        try:
            level = config.get('General', 'log level').lower()
        except Error:
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
    handler = logging.handlers.RotatingFileHandler(USER_LOG_FILE, 'a', max_size, max_backups)
    handler.setFormatter(applet_log_formatter)
    applet_log.removeHandler(applet_log_handler)
    applet_log_handler = handler
    applet_log.addHandler(applet_log_handler)


# critical section
applet_lock = threading.Lock()


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
            applet_log.warning("CONFIG: cannot set option %s:%s = %s [%s]" % (section, entry, value, e))

    def load(self):
        try:
            self._config_parser.read(self._config_file)
        except configparser.Error as e:
            applet_log.warning("CONFIG: malformed configuration file, using default [%s]" % e)
            self._default()
            self.save()

    def save(self):
        try:
            with open(self._config_file, mode='w') as f:
                self._config_parser.write(f)
        except IOError as e:
            applet_log.error("CONFIG: cannot write file %s [%s]" % (_config_file, e))

config = Config()


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
    with ThreadPoolExecutor(config.get('Concurrency', 'max threads')) as e:
        e.map(lambda c: c.tick(), conditions)


# the module level scheduler
periodic = Periodic(config.get('Scheduler', 'tick seconds'), periodic_condition_check, autostart=False)


# utilities to check for system events
current_system_event = None


# check among the system event conditions setting the global system event
def sysevent_condition_check(event):
    global current_system_event
    current_system_event = event
    try:
        if periodic.stopped:
            applet_log.info("SYSEVENT: check skipped due to scheduler pause")
            return
        conds = filter(lambda c: type(c) == EventBasedCondition, conditions)
        with ThreadPoolExecutor(config.get('Concurrency', 'max threads')) as e:
            e.map(lambda c: c.tick(), conds)
    finally:
        current_system_event = None


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
        file_name = os.path.join(USER_CONFIG_FOLDER, 'task.list')
        with open(file_name, 'wb') as f:
            pickle.dump(l, f)

    def load(self):
        self._list = []
        self._last_id = 0
        file_name = os.path.join(USER_CONFIG_FOLDER, 'task.list')
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
            l = list(filter(lambda x: x.task_name != task.task_name, self._list))
            l.append(task)
            self._list = l
            self._lock.release()
        else:
            # FIXME: there should be a way to deduplicate these ops
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
                    break
            if removable:
                self._list.remove(task)
                task.unlink_file()
                return True
            else:
                return False
        else:
            return False

    def get(self, task_id=None, task_name=None):
        if task_id:
            try:
                return list(filter(lambda x: task_id == x.task_id, self._list))[0]
            except IndexError as e:
                return None
        elif task_name:
            try:
                return list(filter(lambda x: task_name == x.task_name, self._list))[0]
            except IndexError as e:
                return None

tasks = Tasks()


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
        file_name = os.path.join(USER_CONFIG_FOLDER, 'condition.list')
        with open(file_name, 'wb') as f:
            pickle.dump(l, f)

    def load(self):
        self._list = []
        self._last_id = 0
        file_name = os.path.join(USER_CONFIG_FOLDER, 'condition.list')
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
            l = list(filter(lambda x: x.cond_name != cond.cond_name, self._list))
            l.append(cond)
            self._list = l
            self._lock.release()
        else:
            # FIXME: there should be a way to deduplicate these ops
            self._lock.acquire()
            self._list.append(cond)
            self._lock.release()

    def remove(self, cond_name=None, cond_id=None):
        cond = None
        if cond_id:
            cond = next((c for c in self._list if c.cond_id == cond_id), None)
        elif cond_name:
            cond = next((c for c in self._list if c.cond_name == cond_name), None)
        if cond:
            self._list.remove(cond)
            cond.unlink_file()
            return True
        else:
            return False

    def get(self, cond_id=None, cond_name=None):
        if cond_id:
            try:
                return list(filter(lambda x: cond_id == x.cond_id, self._list))[0]
            except IndexError as e:
                return None
        elif cond_name:
            try:
                return list(filter(lambda x: cond_name == x.cond_name, self._list))[0]
            except IndexError as e:
                return None

conditions = Conditions()


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
        l = list([item for item in self._queue if item.item_id == item_id])
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

history = HistoryQueue()


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
        self.case_sensitive = False
        self.command = ""
        self.startup_dir = None
        self.running = False
        self._process_stdout = ""
        self._process_stderr = ""
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
        file_name = os.path.join(USER_CONFIG_FOLDER, "%s.task" % self.task_name)
        with open(file_name, 'wb') as f:
            pickle.dump(self, f)

    def unlink_file(self):
        file_name = os.path.join(USER_CONFIG_FOLDER, "%s.task" % self.task_name)
        if os.path.exists(file_name):
            os.unlink(file_name)

    @staticmethod
    def restore(name):
        file_name = os.path.join(USER_CONFIG_FOLDER, "%s.task" % name)
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
                env = os.environ
                for k in self.environment_vars:
                    env[k] = self.environment_vars[k]
            else:
                env = self.environment_vars
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
            self._warning("task failed, runtime error: %s" % e)
            failure_reason = 'overlap'
        except OSError as e:
            self._warning("task failed, system error: %s" % e)
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
            return success


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
        self.cond_name = None
        self.cond_id = None
        self.last_tested = None
        self.last_succeeded = None
        self.skip_seconds = config.get('Scheduler', 'skip seconds')
        self.startup_time = None
        self.task_names = []
        self.repeat = True
        self.exec_sequence = True
        self.suspended = False
        self.cond_name = name
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
        l = list(filter(lambda x: x != task_name, self.task_names))
        self.task_names = l
        self.task_names.append(task_name)

    def delete_task(self, task_name):
        l = list(filter(lambda x: x != task_name, self.task_names))
        self.task_names = l

    def renew_id(self):
        self.cond_id = conditions.get_id()

    def dump(self):
        if self.cond_name is None:
            raise RuntimeError("condition not initialized")
        file_name = os.path.join(USER_CONFIG_FOLDER, '%s.cond' % self.cond_name)
        with open(file_name, 'wb') as f:
            pickle.dump(self, f)

    def unlink_file(self):
        file_name = os.path.join(USER_CONFIG_FOLDER, "%s.cond" % self.cond_name)
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
                        task.run(self.cond_name)
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
        self._debug("checking %.3f - %.3f (=%.3f) in [0-%s]" % (cur_time, test_time, cur_time - test_time, self.skip_seconds))
        if 0 < cur_time - test_time <= self.skip_seconds:
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


class CommandBasedCondition(Condition):

    def _check_condition(self):
        self._debug("checking command based condition")
        try:
            self._debug("spawning test subprocess: %s" % self.command)
            with subprocess.Popen(self.command,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell=True) as proc:
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
                    if self.case_sensitive:
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
                    if self.case_sensitive:
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
            self._warning("condition failed, system error: %s" % e)
            return False
        except subprocess.CalledProcessError as e:
            self._warning("condition failed, called process error")
            return False
        except subprocess.TimeoutExpired as e:
            self._warning("condition failed, timeout expired")
            return False
        except Exception as e:
            self._error("condition failed (unexpected error: %s)" % e)
            return False

    def command_properties(self, **kwargs):
        for k in kwargs.keys():
            if k == 'match_exact':
                self.match_exact = bool(kwargs[k])
            elif k == 'case_sensitive':
                self.case_sensitive = bool(kwargs[k])

    def __init__(self, name, command, status=None, stdout=None, stderr=None, repeat=True, exec_sequence=True):
        self.match_exact = False
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


# as a bonus, and provided that the xprintidle command is present, the idle
# time condition is implemented as a special case of the command condition
class IdleTimeBasedCondition(CommandBasedCondition):

    def _check_condition(self):
        if self.idle_reset:
            if CommandBasedCondition._check_condition(self):
                self.idle_reset = False
                return True
            else:
                self.idle_reset = True
                return False
        else:
            if not CommandBasedCondition._check_condition(self):
                self.idle_reset = True
            return False

    def __init__(self, name, idle_secs, repeat=True, exec_sequence=True):
        self.idle_secs = idle_secs
        self.idle_reset = True
        command = """test $(xprintidle) -gt %s""" % (idle_secs * 1000)
        CommandBasedCondition.__init__(self, name, command, status=0, repeat=repeat, exec_sequence=exec_sequence)


# For now the system event based conditions for startup and shutdown assume
# that startup is when the applet is launched and shutdown is when the applet
# is closed: consider the idea of renaming both conditions and events
class EventBasedCondition(Condition):

    def _check_condition(self):
        self._debug("checking event based condition: %s" % self.event)
        if self.event == current_system_event:
            return True
        else:
            return False

    def __init__(self, name, event, no_skip=True, repeat=False, exec_sequence=True):
        self.event = event
        Condition.__init__(self, name, repeat, exec_sequence)
        if no_skip:
            self.skip_seconds = 0


#############################################################################
# dialog boxes and windows

# This dialog box is populated by loading a dummy task from a file, when the
# task is edited it goes directly to the loaded file (if existing or a new one
# otherwise) and is listed or replaced in the current task list.
class TaskDialog(object):

    def __init__(self):
        self.builder = Gtk.Builder().new_from_string(DIALOG_ADD_TASK, -1)
        self.builder.connect_signals(self)
        o = self.builder.get_object
        self.dialog = o('dlgAddTask')
        self.stored_tasks = tasks.names
        self.stored_tasks.sort()
        cb_tasks = o('cbTaskName')
        for x in self.stored_tasks:
            cb_tasks.append_text(x)
        l = o('listEnvVars')
        c = Gtk.TreeViewColumn(resources.LISTCOL_ENVVARS_NAME, Gtk.CellRendererText(), text=0)
        l.append_column(c)
        c = Gtk.TreeViewColumn(resources.LISTCOL_ENVVARS_VALUE, Gtk.CellRendererText(), text=1)
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

    def click_listEnvVars(self, selected):
        o = self.builder.get_object
        m, i = selected.get_selected()
        if i is not None:
            o('txtVarName').set_text(m[i][0])
            o('txtVarValue').set_text(m[i][1])

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

    def click_btnChooseDir(self, _):
        o = self.builder.get_object
        curpath = o('txtFolder').get_text()
        dirdlg = Gtk.FileChooserDialog(title="Choose Directory",
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
        name = box.get_active_text()
        self.default_box()
        if name in self.stored_tasks:
            task = tasks.get(task_name=name)
            o('txtVarName').set_text("")
            o('txtVarValue').set_text("")
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

    def default_box(self, include_name=False):
        o = self.builder.get_object
        if include_name:
            o('txtName').set_text('')
        o('txtVarName').set_text("")
        o('txtVarValue').set_text("")
        o('txtCommand').set_text("")
        o('txtFolder').set_text("")
        o('chkExactMatch').set_active(False)
        o('chkCaseSensitive').set_active(False)
        o('chkImportEnvironment').set_active(True)
        o('rdSuccess').set_active(True)
        o('cbCheckWhat').set_active(0)
        o('txtCheckValue').set_text("0")
        o('store_listEnvVars').clear()

    def run(self):
        o = self.builder.get_object
        self.stored_tasks = tasks.names
        self.stored_tasks.sort()
        cb_tasks = o('cbTaskName')
        cb_tasks.get_model().clear()
        for x in self.stored_tasks:
            cb_tasks.append_text(x)
        self.dialog.set_keep_above(True)
        self.dialog.present()
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
            task.case_sensitive = o('chkCaseSensitive').get_active()
            task.include_env = o('chkImportEnvironment').get_active()
            task.dump()
            tasks.add(task)
            tasks.save()
            self.stored_tasks = tasks.names
            self.stored_tasks.sort()
            cb_tasks = o('cbTaskName')
            cb_tasks.get_model().clear()
            for x in self.stored_tasks:
                cb_tasks.append_text(x)
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
                        cb_tasks.get_model().clear()
                        for x in self.stored_tasks:
                            cb_tasks.append_text(x)
                    else:
                        applet_log.error("DLGTASK: task %s could not be deleted" % name)
                        msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                                   buttons=Gtk.ButtonsType.OK)
                        msgbox.set_markup(resources.DLG_CANNOT_DELETE_TASK % name)
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
        self.builder = Gtk.Builder().new_from_string(DIALOG_ADD_CONDITION, -1)
        self.builder.connect_signals(self)
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
        self.update_box_type(None)
        l = o('listTasks')
        c = Gtk.TreeViewColumn(resources.LISTCOL_TASKS_NAME, Gtk.CellRendererText(), text=0)
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
        o('cbAddTask').set_active(-1)
        o('cbCheckWhat').set_active(0)
        o('chkRepeat').set_active(True)
        o('chkSequence').set_active(True)
        o('chkExactMatch').set_active(False)
        o('chkCaseSensitive').set_active(False)
        o('chkSuspend').set_active(False)
        o('store_listTasks').clear()

    def choose_condition(self, box):
        o = self.builder.get_object
        name = box.get_active_text()
        self.default_box()
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
                    o('cbMonth').set_active_item(cond.month - 1)
                if cond.day:
                    o('txtDay').set_text(str(cond.day))
                if cond.weekday:
                    o('cbWeekday').set_active_item(cond.weekday)
                if cond.hour:
                    o('txtHour').set_text(str(cond.hour))
                if cond.minute:
                    o('txtMinute').set_text(str(cond.minute))
                o('cbType').set_active(1)
            elif type(cond) == CommandBasedCondition:
                o('txtCommand').set_text(cond.command)
                o('chkExactMatch').set_active(cond.match_exact)
                o('chkCaseSensitive').set_active(cond.case_sensitive)
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
                if evt == 'startup':
                    o('cbSysEvent').set_active(0)
                elif evt == 'shutdown':
                    o('cbSysEvent').set_active(1)
                else:
                    o('cbSysEvent').set_active(-1)
                o('cbType').set_active(4)
            else:
                o('cbType').set_active(-1)
                pass
            o('chkRepeat').set_active(cond.repeat)
            o('chkSequence').set_active(cond.exec_sequence)
            o('chkSuspend').set_active(cond.suspended)
            m = o('store_listTasks')
            for x in cond.task_names:
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
            'canvasOptions_Empty',
        ]
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
        else:
            current_widget = 'canvasOptions_Empty'
        for w in widgets:
            if w == current_widget:
                o(w).show()
            else:
                o(w).hide()

    def run(self):
        self.default_box()
        o = self.builder.get_object
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
        self.dialog.set_keep_above(True)
        self.dialog.present()
        ret = self.dialog.run()
        self.dialog.hide()
        self.dialog.set_keep_above(False)
        if ret == ACTION_OK:
            name = o('txtName').get_text()
            repeat = o('chkRepeat').get_active()
            sequence = o('chkSequence').get_active()
            suspend = o('chkSuspend').get_active()
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
                c = CommandBasedCondition(name, command, status, stdout, stderr, repeat, sequence)
                c.command_properties(match_exact=o('chkExactMatch').get_active())
                c.command_properties(case_sensitive=o('chkCaseSensitive').get_active())
            elif idx == 3:
                idle_secs = int(o('txtIdleMins').get_text()) * 60
                c = IdleTimeBasedCondition(name, idle_secs, repeat, sequence)
                current_widget = 'canvasOptions_IdleTime'
            elif idx == 4:
                event_type = ('startup', 'shutdown')[
                    o('cbSysEvent').get_active()]
                c = EventBasedCondition(name, event_type, True, repeat, sequence)
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
            self.stored_conditions = conditions.names
            self.stored_conditions.sort()
            cb_conds = o('cbConditionName')
            cb_conds.get_model().clear()
            for x in self.stored_conditions:
                cb_conds.append_text(x)
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
                        cb_conds.get_model().clear()
                        for x in self.stored_conditions:
                            cb_conds.append_text(x)
                    else:
                        applet_log.error("DLGCOND: condition %s could not be deleted" % name)
                        msgbox = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                                   buttons=Gtk.ButtonsType.OK)
                        msgbox.set_markup(resources.DLG_CANNOT_DELETE_CONDITION % name)
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


# settings dialog
class SettingsDialog(object):

    def __init__(self):
        self.builder = Gtk.Builder().new_from_string(DIALOG_SETTINGS, -1)
        self.builder.connect_signals(self)
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
        log_level_idx = self.log_levels.index(config.get('General', 'log level'))
        icon_theme_idx = self.icon_themes.index(config.get('General', 'icon theme'))
        o('chkShowIcon').set_active(config.get('General', 'show icon'))
        o('chkAutostart').set_active(config.get('General', 'autostart'))
        o('chkNotifications').set_active(config.get('General', 'notifications'))
        o('chkPreservePause').set_active(config.get('Scheduler', 'preserve pause'))
        o('cbLogLevel').set_active(log_level_idx)
        o('cbIconTheme').set_active(icon_theme_idx)
        o('txtTickSeconds').set_text(str(config.get('Scheduler', 'tick seconds')))
        o('txtSkipSeconds').set_text(str(config.get('Scheduler', 'skip seconds')))
        o('txtMaxThreads').set_text(str(config.get('Concurrency', 'max threads')))
        o('txtMaxLogSize').set_text(str(config.get('History', 'log size')))
        o('txtMaxLogBackups').set_text(str(config.get('History', 'log backups')))
        o('txtMaxHistoryItems').set_text(str(config.get('History', 'max items')))

    def run(self):
        self.default_box()
        self.dialog.set_keep_above(True)
        self.dialog.present()
        ret = self.dialog.run()
        self.dialog.hide()
        self.dialog.set_keep_above(False)
        o = self.builder.get_object
        if ret == ACTION_OK:
            config_skip = []
            v = o('cbLogLevel').get_active()
            if v >= 0:
                config.set('General', 'log level', self.log_levels[v])
            else:
                config_skip.append('log level')
            config.set('General', 'icon theme', self.icon_themes[o('cbIconTheme').get_active()])
            config.set('General', 'show icon', o('chkShowIcon').get_active())
            config.set('General', 'autostart', o('chkAutostart').get_active())
            config.set('General', 'notifications', o('chkNotifications').get_active())
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
            # FIXME: find applet even when called by a second instance
            if applet:
                applet.hide_icon(not config.get('General', 'show icon'))


class HistoryDialog(object):

    def __init__(self):
        self.builder = Gtk.Builder().new_from_string(DIALOG_TASK_HISTORY, -1)
        self.builder.connect_signals(self)
        o = self.builder.get_object
        self.dialog = o('dlgHistory')
        self.image_success = Gtk.Image.new_from_file(os.path.join(APP_ICON_FOLDER, 'emblems', 'success.png'))
        self.image_failure = Gtk.Image.new_from_file(os.path.join(APP_ICON_FOLDER, 'emblems', 'failure.png'))
        l = o('listHistory')
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(resources.LISTCOL_HISTORY_TIMESTAMP, renderer, text=0)
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(resources.LISTCOL_HISTORY_TASK, renderer, text=1)
        c.props.expand = True
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(resources.LISTCOL_HISTORY_TRIGGER, renderer, text=2)
        c.props.expand = True
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(resources.LISTCOL_HISTORY_EXITCODE, renderer, text=3)
        l.append_column(c)
        renderer = Gtk.CellRendererPixbuf()
        c = Gtk.TreeViewColumn(resources.LISTCOL_HISTORY_SUCCESS, renderer, pixbuf=4)
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(resources.LISTCOL_HISTORY_REASON, renderer, text=5)
        l.append_column(c)
        renderer = Gtk.CellRendererText()
        c = Gtk.TreeViewColumn(resources.LISTCOL_HISTORY_ROWID, renderer, text=6)
        c.set_visible(False)
        l.append_column(c)
        o('txtStdOut').modify_font(Pango.FontDescription("Monospace"))
        o('txtStdErr').modify_font(Pango.FontDescription("Monospace"))

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
            s_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i.startup_time))
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
        self.image_logo = Gtk.Image.new_from_file(os.path.join(APP_ICON_FOLDER, 'alarmclock-128.png'))
        self.builder = Gtk.Builder().new_from_string(DIALOG_ABOUT, -1)
        self.builder.connect_signals(self)
        o = self.builder.get_object
        self.dialog = o('dlgAbout')
        self.dialog.set_logo(self.image_logo.get_pixbuf())
        self.dialog.set_version(resources.DLG_ABOUT_VERSION_STRING % APPLET_VERSION)
        self.dialog.set_icon_from_file(os.path.join(APP_ICON_FOLDER, 'alarmclock.png'))

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

    dialog_add_task = TaskDialog()
    dialog_add_condition = ConditionDialog()
    dialog_about = AboutDialog()
    dialog_settings = SettingsDialog()
    dialog_history = HistoryDialog()
    running = False

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id=APPLET_ID,
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.applet_activate)
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(self.before_shutdown,
                                     signal_name='PrepareForShutdown',
                                     dbus_interface='org.freedesktop.login1.Manager',
                                     bus_name='org.freedesktop.login1',
                                     path=None)

    def applet_activate(self, applet_instance):
        if self.running:
            applet_log.warning("MAIN: already running: show settings and quit")
            self.dlgsettings(None)
            self.quit(None)
        else:
            self.running = True
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
        self.indicator = AppIndicator.Indicator.new(APPLET_NAME, 'alarm', AppIndicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_icon_theme_path(os.path.join(APP_ICON_FOLDER, icon_suffix))
        if config.get('General', 'show icon'):
            self.indicator.set_icon('alarm')
            self.indicator.set_attention_icon('warning')
            if config.get('General', 'show icon'):
                self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            self.indicator.set_menu(self.build_menu())
        if config.get('General', 'notifications'):
            Notify.init(APPLET_NAME)
            self._notify = Notify.Notification()

        # load tasks and conditions, if there are any
        try:
            tasks.load()
        except FileNotFoundError:
            tasks.save()
        try:
            conditions.load()
        except FileNotFoundError:
            conditions.save()

        applet_log.info("MAIN: trying to run startup tasks")
        sysevent_condition_check('startup')
        Gtk.main()

    def before_shutdown(self, *args):
        applet_log.info("MAIN: trying to run shutdown tasks")
        sysevent_condition_check('shutdown')

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
        name = 'alarm-add' if active else 'alarm'
        self.indicator.set_icon(name)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

    def dlgtask(self, _):
        self.icon_dialog()
        applet_log.debug("MAIN: opening task dialog")
        self.dialog_add_task.run()
        self.icon_dialog(False)

    def dlgcondition(self, _):
        self.icon_dialog()
        applet_log.debug("MAIN: opening condition dialog")
        self.dialog_add_condition.run()
        self.icon_dialog(False)

    def dlgabout(self, _):
        applet_log.debug("MAIN: opening about dialog")
        self.dialog_about.run()

    def dlgsettings(self, _):
        self.icon_dialog()
        applet_log.debug("MAIN: opening settings dialog")
        self.dialog_settings.run()
        self.icon_dialog(False)

    def dlghistory(self, _):
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

    def build_menu(self):
        menu = Gtk.Menu()
        item_newtask = Gtk.MenuItem(label=resources.MENU_EDIT_TASKS)
        item_newtask.connect('activate', self.dlgtask)
        item_newtask.show()
        menu.append(item_newtask)

        item_newcond = Gtk.MenuItem(label=resources.MENU_EDIT_CONDITIONS)
        item_newcond.connect('activate', self.dlgcondition)
        item_newcond.show()
        menu.append(item_newcond)

        item_settings = Gtk.MenuItem(label=resources.MENU_SETTINGS)
        item_settings.connect('activate', self.dlgsettings)
        item_settings.show()
        menu.append(item_settings)

        separator = Gtk.SeparatorMenuItem()
        separator.show()
        menu.append(separator)

        item_history = Gtk.MenuItem(label=resources.MENU_TASK_HISTORY)
        item_history.connect('activate', self.dlghistory)
        item_history.show()
        menu.append(item_history)

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


#############################################################################
# this will be set up in the main loop to avoid polluting the process
# if another instance of the application is already running
applet = None


# signal handler (see http://stackoverflow.com/questions/26388088)
# def init_signal_handler(applet_instance):
#     def signal_action(signum):
#         if signum is signal.SIGHUP:
#             applet_log.info("SIGHANDLER: caught SIGHUP")
#         elif signum is signal.SIGINT:
#             applet_log.info("SIGHANDLER: caught SIGINT")
#         elif signum is signal.SIGTERM:
#             applet_log.info("SIGHANDLER: caught SIGTERM")
#         applet_instance.before_shutdown()
#
#     def idle_handler(*args):
#         applet_log.info("SIGHANDLER: handler activated (system)")
#         GLib.idle_add(signal_action, priority=GLib.PRIORITY_HIGH)
#
#     def handler(*args):
#         applet_log.info("SIGHANDLER: handler activated (desktop)")
#         signal_action(args[0])
#
#     def install_glib_handler(signum):
#         unix_signal_add = None
#         if hasattr(GLib, "unix_signal_add"):
#             unix_signal_add = GLib.unix_signal_add
#         elif hasattr(GLib, "unix_signal_add_full"):
#             unix_signal_add = GLib.unix_signal_add_full
#         if unix_signal_add:
#             applet_log.info("SIGHANDLER: register desktop handler for signal: %r" % signum)
#             unix_signal_add(GLib.PRIORITY_HIGH, signum, handler, signum)
#         else:
#             applet_log.warning("SIGHANDLER: cannot install signal handler")
#
#     SIGS = [getattr(signal, s, None) for s in "SIGINT SIGTERM SIGHUP".split()]
#     for signum in filter(None, SIGS):
#         applet_log.info("SIGHANDLER: register system handler for signal: %r" % signum)
#         signal.signal(signum, idle_handler)
#         GLib.idle_add(install_glib_handler, signum, priority=GLib.PRIORITY_HIGH)


# Check whether another instance of the application is running: if so the
# settings dialog box is shown in order to give the possibility to show the
# indicator icon if it was hidden. If no other instance is running, capture
# the signals, configure the logger, start the clock and run the applet.
def main():
    config_loghandler()
    config_loglevel()
    # init_signal_handler(applet)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    preserve_pause = config.get('Scheduler', 'preserve pause')
    if not (preserve_pause and check_pause_file()):
        periodic.start()
    # the following two cases should be useless, but do some cleanup anyway
    elif not preserve_pause:
        unlink_pause_file()
    else:
        periodic.stop()
    applet.run([])
    if not periodic.stopped:
        periodic.stop()


# implement the applet and start
if __name__ == '__main__':
    create_desktop_file()
    create_autostart_file(False)
    GObject.threads_init()
    applet = AppletIndicator()
    main()


# end.
