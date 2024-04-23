# main
# the application main form

import os

from lib.i18n.strings import *

from lib.utility import sg, get_configfile
from lib.icons import APP_ICON32 as APP_ICON
from lib.icons import QMARK_ICON48 as QMARK_ICON
from lib.icons import XMARK_ICON48 as XMARK_ICON

from lib.forms.task_command import form_CommandTask
from lib.forms.task_lua import form_LuaScriptTask

from lib.forms.cond_lua import form_LuaScriptCondition
from lib.forms.cond_command import form_CommandCondition
from lib.forms.cond_interval import form_IntervalCondition
from lib.forms.cond_idle import form_IdleCondition
from lib.forms.cond_event import form_EventCondition
from lib.forms.cond_time import form_TimeCondition

from lib.forms.event_cli import form_CommandEvent
from lib.forms.event_fschange import form_FilesystemChangeEvent

from lib.forms.newitem import form_NewItem

from lib.configurator.reader import read_whenever_config
from lib.configurator.writer import write_whenever_config


# layout generator (fixed)
def layout_main():
    return [
        [ sg.Frame(UI_FORM_FILE, [
            [
                # NOTE: the configuration file is fixed and its path only
                # depends on the location of the application data and config
                # folder: usually the default should be used so that the
                # actual **whenever** configuration can also be used by other
                # wrappers such as **whenever_tray**
                sg.T(UI_FORM_PATH_SC), sg.I(key='-CONFIG_FILE-', expand_x=True, disabled=True),
                # sg.FileBrowse(UI_BROWSE, file_types=['TOML \{toml\}']),
            ],
        ], expand_x=True) ],

        [ sg.Frame(UI_FORM_GLOBALS, [[
            sg.T(UI_FORM_TICKINTERVAL_SC),
            sg.I(key='-TICK_INTERVAL-', size=(5, None)),
            sg.Push(),
            sg.CB(UI_FORM_RANDCHECKSINTICKS, key='-RANDOM_CHECKS-', default=False),
        ]], expand_x=True) ],

        [ sg.Frame(UI_FORM_ITEMS, [
            [ sg.T(UI_FORM_CURRENTITEMS_SC) ],
            [ sg.Table(
                [['' for x in range(3)] for y in range(5)],
                auto_size_columns=True,
                visible_column_map=(True, True, False),
                headings=[UI_FORM_NAME, UI_FORM_TYPE, 'TYPE_CODE'],
                key='-ITEMS-',
                num_rows=6,
                justification='left',
                expand_x=True, expand_y=True,
            ) ],
            [ sg.B(UI_NEW, key='-ADD_ITEM-'), sg.Push(), sg.B(UI_EDIT, key='-EDIT_ITEM-'), sg.B(UI_DEL, key='-DEL_ITEM-') ]
        ], expand_x=True, expand_y=True) ],

        [ sg.Push(), sg.B(UI_LOAD, key='-LOAD-'), sg.B(UI_SAVE, key='-SAVE-'), sg.B(UI_EXIT, key='-EXIT-') ],
    ]


# configuration editor form: this is a work in progress as new types of item
# are created on top of the items directly supported by **whenever**; also
# this is a fixed form and will not be derived for specialized purposes
class form_Config(object):

    def __init__(self):
        self._form = sg.Window(UI_APP, layout=layout_main(), icon=APP_ICON, size=(960, 640), finalize=True)

        # reset data, both actuaal and visualizable
        self._tasks = {}
        self._conditions = {}
        self._events = {}
        self._data = {}
        self._itemlistentries = []
        self._globals = {
            'scheduler_tick_seconds': 5,
            'randomize_checks_within_ticks': False,
        }
        self._changed = False
        self._form['-RANDOM_CHECKS-'].bind('<Button-1>' , '+-click-')
        self._form['-TICK_INTERVAL-'].bind('<KeyRelease>' , '+-keyrelease-')

        # the configuration file should be well formed, so load it
        cfgfile = get_configfile()
        self._form['-CONFIG_FILE-'].update(cfgfile)
        self._load_config(cfgfile)
        self._updatedata()
        self._updateform()


    # update the associated data according to what is in the form
    def _updatedata(self):
        self._itemlistentries = []
        for key in self._tasks:
            item = self._tasks[key]
            self._itemlistentries.append([item.name, item.hrtype, 'task:%s' % item.type])
        for key in self._conditions:
            item = self._conditions[key]
            self._itemlistentries.append([item.name, item.hrtype, 'condition:%s' % item.type])
        for key in self._events:
            item = self._events[key]
            self._itemlistentries.append([item.name, item.hrtype, 'event:%s' % item.type])
        self._itemlistentries.sort(key=lambda x: x[0])
        try:
            t = int(self._data['-TICK_INTERVAL-'])
        except ValueError:
            t = None
        self._globals['scheduler_tick_seconds'] = t
        self._globals['randomize_checks_within_ticks'] = self._data['-RANDOM_CHECKS-']

    # update the form fields according to the associated actual data
    def _updateform(self):
        self._form['-ITEMS-'].update(self._itemlistentries)
        t = self._globals['scheduler_tick_seconds']
        self._form['-TICK_INTERVAL-'].update(str(t) if t else '')
        self._form['-RANDOM_CHECKS-'].update(self._globals['randomize_checks_within_ticks'])

    # reset all associated data in the form (does not update fields)
    def _resetdata(self):
        self._tasks = {}
        self._conditions = {}
        self._events = {}
        self._globals = {
            'scheduler_tick_seconds': 5,
            'randomize_checks_within_ticks': False,
        }


    # load the configuration from a TOML file
    def _load_config(self, fn):
        self._resetdata()
        tasks, conditions, events, self._globals = read_whenever_config(fn)
        for item in tasks:
            self._tasks[item.name] = item
        for item in conditions:
            self._conditions[item.name] = item
        for item in events:
            self._events[item.name] = item
        # the following updates are necessary to avoid retrieved form data to
        # overwrite the inner data that has just been loaded from the file
        if self._globals['randomize_checks_within_ticks']:
            self._data['-RANDOM_CHECKS-'] = self._globals['randomize_checks_within_ticks']
        if self._globals['scheduler_tick_seconds']:
            self._data['-TICK_INTERVAL-'] = self._globals['scheduler_tick_seconds']

    # save the configuration to a TOML file
    def _save_config(self, fn):
        write_whenever_config(
            fn,
            [self._tasks[k] for k in self._tasks],
            [self._conditions[k] for k in self._conditions],
            [self._events[k] for k in self._events],
            self._globals,
        )


    # form event loop: react to events and update the inner data accordingly
    def run(self):
        self._updateform()
        while True:             # Event Loop
            event, values = self._form.read()
            self._data = values

            # exit from the form and possibly the application itself
            if event in [sg.WIN_CLOSED, '-EXIT-']:
                break

            # load the configuration file: if the configuration had changed
            # ask for confirmation as all changes would be lost on load
            elif event == '-LOAD-':
                fn = values['-CONFIG_FILE-']
                if os.path.exists(fn):
                    if self._changed:
                        if sg.PopupYesNo(UI_POPUP_DISCARDCONFIG_Q, title=UI_POPUP_T_CONFIRM, icon=QMARK_ICON).upper() == 'YES':
                            self._load_config(fn)
                            self._changed = False
                    else:
                        self._load_config(fn)
                        self._changed = False
                    self._updateform()
                else:
                    sg.popup_error(UI_POPUP_FILENOTFOUND_ERR, title=UI_POPUP_T_ERR, icon=XMARK_ICON)

            # save the configuration file, asking for confirmation if it
            # exists, which is almost always true
            elif event == '-SAVE-':
                fn = values['-CONFIG_FILE-']
                if os.path.exists(fn):
                    if self._changed:
                        if sg.PopupYesNo(UI_POPUP_OVERWRITEFILE_Q, title=UI_POPUP_T_CONFIRM, icon=QMARK_ICON).upper() == 'YES':
                            self._save_config(fn)
                            self._changed = False
                else:
                    self._save_config(fn)
                    self._changed = False

            # edit an existing item: this opens the appropriate form, which
            # in turn displays the actual data for the provided item; this
            # part will possibly grow as new item typer are supported
            elif event == '-EDIT_ITEM-':
                t = values['-ITEMS-']
                if t:
                    item_row = self._itemlistentries[t[0]]
                    item_name = item_row[0]
                    item_type, item_sub = item_row[2].split(':')

                    # task items
                    if item_type == 'task':
                        if item_sub == 'command':
                            e = form_CommandTask(self._tasks[item_name])
                        elif item_sub == 'lua':
                            e = form_LuaScriptTask(self._tasks[item_name])
                        # ...
                        # newly supported task items will be inserted here
                        else:
                            e = None
                        if e:
                            new_item = e.run()
                            if new_item:
                                if new_item.name != item_name:
                                    del(self._tasks[item_name])
                                self._tasks[new_item.name] = new_item
                                self._changed = True
                            del e

                    # condition items
                    elif item_type == 'condition':
                        if item_sub == 'lua':
                            e = form_LuaScriptCondition(list(self._tasks.keys()), self._conditions[item_name])
                        elif item_sub == 'command':
                            e = form_CommandCondition(list(self._tasks.keys()), self._conditions[item_name])
                        elif item_sub == 'interval':
                            e = form_IntervalCondition(list(self._tasks.keys()), self._conditions[item_name])
                        elif item_sub == 'idle':
                            e = form_IdleCondition(list(self._tasks.keys()), self._conditions[item_name])
                        elif item_sub == 'time':
                            e = form_TimeCondition(list(self._tasks.keys()), self._conditions[item_name])
                        elif item_sub == 'event':
                            e = form_EventCondition(list(self._tasks.keys()), self._conditions[item_name])
                        # ...
                        # newly supported condition items will be inserted here
                        else:
                            e = None
                        if e:
                            new_item = e.run()
                            if new_item:
                                if new_item.name != item_name:
                                    del(self._conditions[item_name])
                                self._conditions[new_item.name] = new_item
                                self._changed = True
                            del e

                    # event items
                    elif item_type == 'event':
                        event_conds = list(x for x in self._conditions if self._conditions[x].type == 'event')
                        if item_sub == 'cli':
                            e = form_CommandEvent(event_conds, self._events[item_name])
                        if item_sub == 'fschange':
                            e = form_FilesystemChangeEvent(event_conds, self._events[item_name])
                        # ...
                        # newly supported event items will be inserted here
                        else:
                            e = None
                        if e:
                            new_item = e.run()
                            if new_item:
                                if new_item.name != item_name:
                                    del(self._events[item_name])
                                self._events[new_item.name] = new_item
                                self._changed = True
                            del e

            # delete an item: ask for confirmation before actual removal
            elif event == '-DEL_ITEM-':
                t = values['-ITEMS-']
                if t:
                    if sg.PopupYesNo(UI_POPUP_DELETEITEM_Q, title=UI_POPUP_T_CONFIRM, icon=QMARK_ICON).upper() == 'YES':
                        item_row = self._itemlistentries[t[0]]
                        item_name = item_row[0]
                        item_type, item_sub = item_row[2].split(':')
                        if item_type == 'task':
                            del self._tasks[item_name]
                        elif item_type == 'condition':
                            del self._conditions[item_name]
                        elif item_type == 'event':
                            del self._events[item_name]
                        self._changed = True
            elif event == '-ADD_ITEM-':
                e = form_NewItem()
                r = e.run()
                del e
                if r:
                    t, form_class = r
                    if t == 'task':
                        form = form_class()
                    elif t == 'cond':
                        form = form_class(list(self._tasks.keys()))
                    # note that, since providing a suitable event based
                    # condition is mandatory for an event, the form will
                    # refuse to create a new event
                    elif t == 'event':
                        event_conds = list(x for x in self._conditions if self._conditions[x].type == 'event')
                        if event_conds:
                            form = form_class(event_conds)
                        else:
                            sg.popup_error(UI_POPUP_NOEVENTCONDITIONS_ERR, title=UI_POPUP_T_ERR, icon=XMARK_ICON)
                            form = None
                    try:
                        if form is not None:
                            new_item = form.run()
                    except ValueError:
                        new_item = None
                    if form is not None:
                        del form
                    if new_item:
                        if t == 'task':
                            self._tasks[new_item.name] = new_item
                        elif t == 'cond':
                            self._conditions[new_item.name] = new_item
                        elif t == 'event':
                            self._events[new_item.name] = new_item

            # reactions to input that cause the form to consider data changed
            elif event == '-RANDOM_CHECKS-+-click-':
                self._changed = True
            elif event == '-TICK_INTERVAL-+-keyrelease-':
                self._changed = True
            # ...
            # more events might be added here

            # perform the usual chores: first update the inner data, then refresh
            self._updatedata()
            self._updateform()

        # destroy the form
        self._form.close()


# end.
