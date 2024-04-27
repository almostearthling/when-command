# time specification condition form

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import XMARK_ICON48 as XMARK_ICON
from lib.icons import QMARK_ICON48 as QMARK_ICON

from lib.forms.cond import form_Condition
from lib.items.cond_time import TimeCondition, TimeSpec

from time import localtime


# these lists and maps are used for visualization and conversion of dates
# from and into the time specifications that are supported by **whenever**
_MONTHS = [
    UI_MON_JAN,
    UI_MON_FEB,
    UI_MON_MAR,
    UI_MON_APR,
    UI_MON_MAY,
    UI_MON_JUN,
    UI_MON_JUL,
    UI_MON_AUG,
    UI_MON_SEP,
    UI_MON_OCT,
    UI_MON_NOV,
    UI_MON_DEC,
    ]

_WEEKDAYS = [
    UI_DOW_MON,
    UI_DOW_TUE,
    UI_DOW_WED,
    UI_DOW_THU,
    UI_DOW_FRI,
    UI_DOW_SAT,
    UI_DOW_SUN,
    ]

_WEEKDAYS_MAP = {
    UI_DOW_MON: 'mon',
    UI_DOW_TUE: 'tue',
    UI_DOW_WED: 'wed',
    UI_DOW_THU: 'thu',
    UI_DOW_FRI: 'fri',
    UI_DOW_SAT: 'sat',
    UI_DOW_SUN: 'sun',
}

_WEEKDAYS_DISPLAY = {
    'mon': UI_DOW_MON,
    'tue': UI_DOW_TUE,
    'wed': UI_DOW_WED,
    'thu': UI_DOW_THU,
    'fri': UI_DOW_FRI,
    'sat': UI_DOW_SAT,
    'sun': UI_DOW_SUN,
}

_MONTHS_MAP = {
    UI_MON_JAN: 1,
    UI_MON_FEB: 2,
    UI_MON_MAR: 3,
    UI_MON_APR: 4,
    UI_MON_MAY: 5,
    UI_MON_JUN: 6,
    UI_MON_JUL: 7,
    UI_MON_AUG: 8,
    UI_MON_SEP: 9,
    UI_MON_OCT: 10,
    UI_MON_NOV: 11,
    UI_MON_DEC: 12,
}

_DAYS = list(map(str, range(1, 32)))

_today = localtime()
_YEARS = list(map(str, range(_today.tm_year, _today.tm_year + 10)))


# (extra) layout generator
def _form_layout():
    return [
        [ sg.Frame(UI_FORM_TIMESPECS, [
            [
                sg.T(UI_FORM_DATE_SC),
                sg.Combo(_YEARS, key='-YEAR-'), sg.T("/"),
                sg.Combo(_MONTHS, key='-MONTH-'), sg.T("/"),
                sg.Combo(_DAYS, key='-DAY-'),
                sg.T(UI_FORM_OR),
                sg.T(UI_FORM_DOW_SC), sg.Combo(_WEEKDAYS, key='-DOW-'),
                sg.Push(),
                sg.T(UI_FORM_TIME_SC),
                sg.I(key='-HOUR-', size=(4, None), justification='right'), sg.T(":"),
                sg.I(key='-MINUTE-', size=(4, None), justification='right'), sg.T(":"),
                sg.I(key='-SECOND-', size=(4, None), justification='right'),
                sg.Push(),
                sg.B_NEW(UI_CLEAR, key='-CLEAR-'),
            ],
            [ sg.Push(), sg.B_ADD(UI_ADD, key='-ADD-'), sg.B_DEL(UI_DEL, key='-REMOVE-') ],
            [ sg.Push() ],
            [ sg.T(UI_FORM_CURRENTTIMESPECS_SC) ],
            [ sg.LBox([], key='-TIMESPECS-', expand_x=True, expand_y=True) ],
            [ sg.Push(), sg.B_BLANK(UI_CLEARALL, key='-CLEARALL-') ],
        ], expand_x=True, expand_y=True) ]
    ]


# specialized subform
class form_TimeCondition(form_Condition):
    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, TimeCondition))
        else:
            item = TimeCondition()
        extra_layout = _form_layout()
        form_Condition.__init__(self, UI_TITLE_TIMECOND, tasks_available, extra_layout, item)
        self._form['-TIMESPECS-'].bind('<Double-Button-1>' , '+-dblclick-')
        self._data['-TIMESPECS-'] = []
        self._timespecs = []
        if item:
            self.set_item(item)
        else:
            self.reset_item()

    def _updatedata(self):
        form_Condition._updatedata(self)
        self._timespecs = []
        if self._item:
            l = []
            if self._item.time_specifications:
                for elem in self._item.time_specifications:
                    timespec = TimeSpec(elem)
                    self._timespecs.append(timespec)
                    l.append(str(timespec))
            self._data['-TIMESPECS-'] = l
        else:
            self._data['-TIMESPECS-'] = []

    def _updateitem(self):
        form_Condition._updateitem(self)
        e = []
        for timespec in self._timespecs:
            e.append(timespec.as_dict())
        self._item.time_specifications = e or None

    def _getspec(self):
        if self._data['-MONTH-']:
            try:
                month = _MONTHS_MAP[self._data['-MONTH-']]
            except ValueError:
                # come on, you can do better
                month = None
        else:
            month = None
        if self._data['-DOW-']:
            try:
                dow = _WEEKDAYS_MAP[self._data['-DOW-']]
            except ValueError:
                # see above
                dow = None
        else:
            dow = None
        try:
            return TimeSpec(
                year=int(self._data['-YEAR-']) if self._data['-YEAR-'] else None,
                month=month,
                day=self._data['-DAY-'] if self._data['-DAY-'] else None,
                weekday=dow,
                hour=int(self._data['-HOUR-']) if self._data['-HOUR-'] != '' else None,
                minute=int(self._data['-MINUTE-']) if self._data['-MINUTE-'] != '' else None,
                second=int(self._data['-SECOND-']) if self._data['-SECOND-'] != '' else None,
            )
        except ValueError:
            return None

    def _setspec(self, spec: TimeSpec):
        self._data['-YEAR-'] = spec.year
        self._data['-MONTH-'] = "{:02}".format(spec.month) if spec.month is not None else None
        self._data['-DAY-'] = "{:02}".format(spec.day) if spec.day is not None else None
        self._data['-DOW-'] = _WEEKDAYS_DISPLAY.get(spec.weekday)
        self._data['-HOUR-'] = spec.hour
        self._data['-MINUTE-'] = "{:02}".format(spec.minute) if spec.minute is not None else None
        self._data['-SECOND-'] = "{:02}".format(spec.second) if spec.second is not None else None

    def _clearspec(self):
        self._data['-YEAR-'] = None
        self._data['-MONTH-'] = None
        self._data['-DAY-'] = None
        self._data['-DOW-'] = None
        self._data['-HOUR-'] = None
        self._data['-MINUTE-'] = None
        self._data['-SECOND-'] = None

    def process_event(self, event, values):
        ret = super().process_event(event, values)
        if ret is None:
            if event == '-TIMESPECS-+-dblclick-':
                idx = self._form['-TIMESPECS-'].get_indexes()[0]
                timespec = self._timespecs[idx]
                self._clearspec()
                self._setspec(timespec)
            elif event == '-ADD-':
                cur_spec = self._getspec()
                if cur_spec:
                    present = False
                    for timespec in self._timespecs:
                        if cur_spec == timespec:
                            present = True
                    if not present:
                        self._timespecs.append(cur_spec)
                    self._clearspec()
                else:
                    sg.popup(UI_POPUP_INVALIDTIMESPEC, title=UI_POPUP_T_ERR, icon=XMARK_ICON)
            elif event == '-REMOVE-':
                cur_spec = self._getspec()
                if cur_spec:
                    newspecs = []
                    for timespec in self._timespecs:
                        print("%s != %s ?" % (timespec, cur_spec))
                        if cur_spec != timespec:
                            newspecs.append(timespec)
                    self._timespecs = newspecs
            elif event == '-CLEAR-':
                self._clearspec()
            elif event == '-CLEARALL-':
                if sg.popup_yes_no(UI_POPUP_DELETETSPECS_Q, title=UI_POPUP_T_CONFIRM, icon=QMARK_ICON).upper() == 'YES':
                    self._timespecs = []
                    self._clearspec()
            # update list again because self._data['-TIMESPECS-'] now only
            # contains a line because of how it is updated
            l = []
            for timespec in self._timespecs:
                l.append(str(timespec))
            self._data['-TIMESPECS-'] = l
        else:
            return ret


# end.
