# time specification condition item

from lib.i18n.strings import *

from tomlkit import table
from lib.utility import check_not_none, append_not_none

from lib.items.cond import Condition


# two converters that may also return None, to improve readability
def _int_or_none(v):
    if v is not None and v != "":
        return int(v)
    else:
        return None

def _str_or_none(v):
    if v is not None and v != "":
        return str(v)
    else:
        return None

# data used to create readable time strings and the values accepted by
# **whenever** TOM configuration file, used by the `TimeSpec` class which
# helps rendering time condition time specifications
_WEEKDAYS_TOML = [
    'mon',
    'tue',
    'wed',
    'thu',
    'fri',
    'sat',
    'sun',
]

_MONTHS_DISPLAY = [
    UI_STR_UNKNOWN, # index 0 is invalid
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

_WEEKDAYS_DISPLAY = {
    'mon': UI_DOW_MON,
    'tue': UI_DOW_TUE,
    'wed': UI_DOW_WED,
    'thu': UI_DOW_THU,
    'fri': UI_DOW_FRI,
    'sat': UI_DOW_SAT,
    'sun': UI_DOW_SUN,
}


# the following is a helper that helps in hiding complexity of time
# specifications: it also truncates weekday names to three characters; also
# a `TimeSpec` differs from an usual time specifications in the sense that
# it can be partial (see initialization code)
class TimeSpec(object):
    def __init__(self, dict_=None, **kwargs):
        if dict_:
            if not isinstance(dict_, dict):
                raise TypeError("non-dictionary parameter")
            self.year = _int_or_none(dict_.get('year'))
            self.month = _int_or_none(dict_.get('month'))
            self.day = _int_or_none(dict_.get('day'))
            self.weekday = _str_or_none(dict_.get('weekday'))
            self.hour = _int_or_none(dict_.get('hour'))
            self.minute = _int_or_none(dict_.get('minute'))
            self.second = _int_or_none(dict_.get('second'))
        else:
            self.year = _int_or_none(kwargs.get('year'))
            self.month = _int_or_none(kwargs.get('month'))
            self.day = _int_or_none(kwargs.get('day'))
            self.weekday = _str_or_none(kwargs.get('weekday'))
            self.hour = _int_or_none(kwargs.get('hour'))
            self.minute = _int_or_none(kwargs.get('minute'))
            self.second = _int_or_none(kwargs.get('second'))
        if self.month is not None and (self.month < 1 or self.month > 12):
            raise ValueError("invalid month: %s" % self.month)
        if self.day is not None and (self.day < 1 or self.day > 31):
            raise ValueError("invalid day: %s" % self.day)
        if self.hour is not None and (self.hour < 0 or self.hour > 23):
            raise ValueError("invalid hour: %s" % self.hour)
        if self.minute is not None and (self.minute < 0 or self.minute > 59):
            raise ValueError("invalid minute: %s" % self.minute)
        if self.second is not None and (self.second < 0 or self.second > 59):
            raise ValueError("invalid second: %s" % self.second)
        if self.weekday is not None:
            self.weekday = self.weekday.lower()[:3]
            if self.weekday not in _WEEKDAYS_TOML:
                raise ValueError("invalid weekday: '%s'" % self.weekday)

    def as_dict(self):
        ret = dict()
        if self.year:
            ret['year'] = self.year
        if self.month:
            ret['month'] = self.month
        if self.day:
            ret['day'] = self.day
        if self.weekday:
            ret['weekday'] = self.weekday
        if self.hour:
            ret['hour'] = self.hour
        if self.minute:
            ret['minute'] = self.minute
        if self.second:
            ret['second'] = self.second
        return ret

    def __eq__(self, other) -> bool:
        assert(isinstance(other, TimeSpec))
        # luckily '==' also works for None
        return (
            self.year == other.year and
            self.month == other.month and
            self.day == other.day and
            self.weekday == other.weekday and
            self.hour == other.hour and
            self.minute == other.minute and
            self.second == other.second
        )

    def __ne__(self, other) -> bool:
        return not self == other

    def __str__(self) -> str:
        attime = None
        onday = None
        # transform into readable strings: many of these conversions may look
        # bizarre to say the very least
        if self.hour is not None or self.minute is not None or self.second is not None:
            if self.hour is not None and self.minute is not None and self.second is not None:
                attime = UI_TIMEFORMAT_ATFULLTIME.format(hour=self.hour, minute=self.minute, second=self.second)
            elif self.hour is not None and self.minute is not None:
                attime = UI_TIMEFORMAT_ATHOURMIN.format(hour=self.hour, minute=self.minute)
            elif self.hour is not None and self.second is not None:
                attime = UI_TIMEFORMAT_ATHOURSEC.format(hour=self.hour, second=self.second)
            elif self.minute is not None and self.second is not None:
                attime = UI_TIMEFORMAT_ATMINSEC.format(minute=self.minute, second=self.second)
            elif self.hour is not None:
                attime = UI_TIMEFORMAT_ATHOUR.format(hour=self.hour)
            elif self.minute is not None:
                attime = UI_TIMEFORMAT_ATMIN.format(minute=self.minute)
            elif self.second is not None:
                attime = UI_TIMEFORMAT_ATSEC.format(second=self.second)
        if self.year or self.month or self.day:
            if self.year and self.month and self.day:
                onday = UI_TIMEFORMAT_ONFULLDATE.format(year=self.year, month=_MONTHS_DISPLAY[self.month], day=self.day)
            elif self.month and self.day:
                onday = UI_TIMEFORMAT_ONMONTHDAY.format(month=_MONTHS_DISPLAY[self.month], day=self.day)
            elif self.year and self.day:
                onday = UI_TIMEFORMAT_ONFULLDATE.format(year=self.year, month=UI_TIMEFORMAT_ANY_MONTH, day=self.day)
            elif self.year and self.month:
                onday = UI_TIMEFORMAT_ONFULLDATE.format(year=self.year, month=_MONTHS_DISPLAY[self.month], day=UI_TIMEFORMAT_ANY_DAY)
            elif self.year:
                onday = UI_TIMEFORMAT_ONFULLDATE.format(year=self.year, month=UI_TIMEFORMAT_ANY_MONTH, day=UI_TIMEFORMAT_ANY_DAY)
            elif self.month:
                onday = UI_TIMEFORMAT_ONFULLDATE.format(year=UI_TIMEFORMAT_ANY_YEAR, month=_MONTHS_DISPLAY[self.month], day=UI_TIMEFORMAT_ANY_DAY)
            elif self.day:
                onday = UI_TIMEFORMAT_ONDAY.format(day=self.day)
        if self.weekday:
            if onday:
                onday = "%s (%s)" % (UI_TIMEFORMAT_ONWEEKDAY.format(weekday=_WEEKDAYS_DISPLAY[self.weekday]), onday)
            else:
                onday = UI_TIMEFORMAT_ONWEEKDAY.format(weekday=_WEEKDAYS_DISPLAY[self.weekday])
        if onday and attime:
            timespec = "%s %s" % (onday, attime)
        elif onday:
            timespec = onday
        elif attime:
            timespec = attime
        else:
            timespec = ""
        return timespec

    # a `TimeSpec` evaluates as False if no component is defined
    def __bool__(self):
        return (
            self.year is not None or
            self.month is not None or
            self.day is not None or
            self.weekday is not None or
            self.hour is not None or
            self.minute is not None or
            self.second is not None
        )


# default values for non-optional parameters
DEFAULT_TIME_SPECIFICATIONS = [{ 'hour': 12, 'minute': 30 }]


# a time based condition
class TimeCondition(Condition):

    # availability at class level
    available = True

    def __init__(self, t: table=None) -> None:
        Condition.__init__(self, t)
        self.type = 'time'
        self.hrtype = ITEM_COND_TIME
        if t:
            self.time_specifications = t.get('time_specifications')
        else:
            self.time_specifications = DEFAULT_TIME_SPECIFICATIONS

    def as_table(self):
        if not check_not_none(
            self.time_specifications,
        ):
            raise ValueError("Invalid Time Condition: mandatory field(s) missing")
        t = Condition.as_table(self)
        t = append_not_none(t, 'time_specifications', self.time_specifications)
        return t


# end.
