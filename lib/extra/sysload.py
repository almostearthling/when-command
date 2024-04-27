# sysloadlow condition module
#
# use a command to check whether the system load is low: it uses
# - vmstat on Linux
# - (Get-CimInstance -Class Win32_Processor).LoadPercentage on Windows
#
# for now no availability on Mac

# this header is common to all extra modules
from lib.i18n.strings import *
from lib.utility import sg, check_not_none, append_not_none

import os
import sys
from tomlkit import items, table

# since a condition is defined, the base form is the one for conditions
from lib.forms.cond import form_Condition

# import item to derive from
from lib.items.cond_command import CommandCondition


# resource strings (not internationalized)
ITEM_COND_SYSLOAD = "System Load Below Treshold Condition"

_UI_TITLE_SYSLOAD = "%s: System Load Condition Editor"
_UI_FORM_SYSLOAD = "System Load"
_UI_FORM_SYSLOADTRESHOLD_SC = "Load is Below:"


# default values
_DEFAULT_LOW_LOAD_PERC = 3


# check for availability: for now only check platform
def _available():
    if sys.platform in ('win32', 'linux'):
        return True
    else:
        return False


# specific item is derived from the actual parent item
class SystemLoadCondition(CommandCondition):

    # availability at class level
    available = _available()

    def __init__(self, t: items.Table=None) -> None:
        CommandCondition.__init__(self, t)
        self.subtype = 'sysload'
        self.hrtype = ITEM_COND_SYSLOAD
        if t:
            assert(t.get('type') == self.type)
            self.tags = t.get('tags')
            assert(isinstance(self.tags, items.Table))
            assert(self.tags.get('subtype') == self.subtype)
        else:
            self.tags = table()
            self.tags.append('subtype', self.subtype)
            self.tags.append('treshold', _DEFAULT_LOW_LOAD_PERC)
        self.updateitem()

    def updateitem(self):
        if sys.platform == 'win32':
            self.command = "pwsh.exe"
            self.command_arguments = [
                "-Command",
                "If ((Get-CimInstance -Class Win32_Processor).LoadPercentage -lt %s) { echo OK }" % self.tags.get('treshold', _DEFAULT_LOW_LOAD_PERC),
            ]
            self.startup_path = "."
            self.success_stdout = "OK"
        elif sys.platform == 'linux':
            self.command = "bash"
            self.command_arguments = [
                "-c",
                "echo '%s <' `vmstat | tail -1 | awk '{print \$14}'` | bc" % self.tags.get('treshold', _DEFAULT_LOW_LOAD_PERC),
            ]
            self.startup_path = "."
            self.success_stdout = "1"


# the specialized form is directly derived from the generic condition form
def _form_layout():
    return [
        [ sg.Frame(_UI_FORM_SYSLOAD, [[
            sg.T(_UI_FORM_SYSLOADTRESHOLD_SC),
            sg.I(key='-TRESHOLD-', expand_x=True),
            sg.T("%"),
        ]], expand_x=True, expand_y=True) ]
    ]

class form_SystemLoadCondition(form_Condition):
    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, SystemLoadCondition))
        else:
            item = SystemLoadCondition()
        extra_layout = _form_layout()
        form_Condition.__init__(self, _UI_TITLE_SYSLOAD, tasks_available, extra_layout, item)
        self.add_checks(
            ('-TRESHOLD-', UI_FORM_IDLEDURATION, lambda x: 0 < int(x) < 100),
        )

    def _updatedata(self):
        form_Condition._updatedata(self)
        if self._item:
            self._data['-TRESHOLD-'] = self._item.tags.get('treshold')
        else:
            self._data['-TRESHOLD-'] = str(_DEFAULT_LOW_LOAD_PERC)

    def _updateitem(self):
        form_Condition._updateitem(self)
        if self._data['-TRESHOLD-']:
            self._item.tags['treshold'] = int(self._data['-TRESHOLD-'])
        else:
            self._item.tags['treshold'] = None

    def process_event(self, event, values):
        return super().process_event(event, values)


# end.
