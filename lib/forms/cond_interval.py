# interval condition form

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import APP_ICON32 as APP_ICON

from lib.forms.cond import form_Condition
from lib.items.cond_interval import IntervalCondition


# (extra) layout generator
def _form_layout():
    return [
        [ sg.Frame(UI_FORM_DELAY, [[
            sg.T(UI_FORM_DELAYSPEC),
            sg.I(key='-INTERVAL-', expand_x=True),
            sg.Combo([UI_TIME_SECONDS, UI_TIME_MINUTES, UI_TIME_HOURS], default_value=UI_TIME_SECONDS, key='-INTERVAL_UNIT-'),
        ]], expand_x=True, expand_y=True) ]
    ]


# specialized subform
class form_IntervalCondition(form_Condition):
    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, IntervalCondition))
        else:
            item = IntervalCondition()
        extra_layout = _form_layout()
        form_Condition.__init__(self, UI_TITLE_INTERVALCOND, tasks_available, extra_layout, item)

    def _updatedata(self):
        form_Condition._updatedata(self)
        if self._item:
            if self._item.interval_seconds is not None and self._item.interval_seconds % 3600 == 0:
                intv = int(self._item.interval_seconds / 3600)
                intvu = UI_TIME_HOURS
            elif self._item.interval_seconds is not None and self._item.interval_seconds % 60 == 0:
                intv = int(self._item.interval_seconds / 60)
                intvu = UI_TIME_MINUTES
            else:
                intv = self._item.interval_seconds
                intvu = UI_TIME_SECONDS
            self._data['-INTERVAL-'] = intv
            self._data['-INTERVAL_UNIT-'] = intvu
        else:
            self._data['-INTERVAL-'] = ''
            self._data['-INTERVAL_UNIT-'] = UI_TIME_SECONDS

    def _updateitem(self):
        form_Condition._updateitem(self)
        if self._data['-INTERVAL-']:
            if self._data['-INTERVAL_UNIT-'] == UI_TIME_HOURS:
                self._item.interval_seconds = int(self._data['-INTERVAL-']) * 3600
            elif self._data['-INTERVAL_UNIT-'] == UI_TIME_MINUTES:
                self._item.interval_seconds = int(self._data['-INTERVAL-']) * 60
            else:
                self._item.interval_seconds = int(self._data['-INTERVAL-'])
        else:
            self._item.interval_seconds = None

    def process_event(self, event, values):
        return super().process_event(event, values)


# end.
