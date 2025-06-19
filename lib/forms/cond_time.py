# time specification condition form

from time import localtime
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from ..i18n.strings import *
from .ui import *

from .cond import form_Condition
from ..items.cond_time import TimeCondition, TimeSpec


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
    UI_DOW_MON: "mon",
    UI_DOW_TUE: "tue",
    UI_DOW_WED: "wed",
    UI_DOW_THU: "thu",
    UI_DOW_FRI: "fri",
    UI_DOW_SAT: "sat",
    UI_DOW_SUN: "sun",
}

_WEEKDAYS_DISPLAY = {
    "mon": UI_DOW_MON,
    "tue": UI_DOW_TUE,
    "wed": UI_DOW_WED,
    "thu": UI_DOW_THU,
    "fri": UI_DOW_FRI,
    "sat": UI_DOW_SAT,
    "sun": UI_DOW_SUN,
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


# specialized subform
class form_TimeCondition(form_Condition):

    def __init__(self, tasks_available, item=None):
        if item:
            assert isinstance(item, TimeCondition)
        else:
            item = TimeCondition()
        super().__init__(UI_TITLE_TIMECOND, tasks_available, item)

        # form data
        self._timespecs = []
        if self._item.time_specifications:
            for ts in self._item.time_specifications:
                timespec = TimeSpec(ts)
                self._timespecs.append(timespec)

        # build the UI: build widgets, arrange them in the box, bind data

        # client area
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # time specification section
        # the time specification area is quite complex and must be
        # carefully built, therefore it deserves a frame
        area_tspec = ttk.Frame(area)
        l_tsDate = ttk.Label(area_tspec, text=UI_FORM_DATE_SC)
        cb_tsYear = ttk.Combobox(area_tspec, width=5, values=_YEARS, state="readonly")
        l_sep1 = ttk.Label(area_tspec, text="/")
        cb_tsMonth = ttk.Combobox(
            area_tspec, width=11, values=_MONTHS, state="readonly"
        )
        l_sep2 = ttk.Label(area_tspec, text="/")
        cb_tsDay = ttk.Combobox(area_tspec, width=3, values=_DAYS, state="readonly")
        l_tsOr = ttk.Label(area_tspec, text=UI_FORM_OR)
        l_tsDayOfWeek = ttk.Label(area_tspec, text=UI_FORM_DOW_SC)
        cb_tsDayOfWeek = ttk.Combobox(
            area_tspec, width=12, values=_WEEKDAYS, state="readonly"
        )
        f_sep3 = ttk.Frame(area_tspec)
        l_tsTime = ttk.Label(area_tspec, text=UI_FORM_TIME_SC)
        e_tsHour = ttk.Entry(area_tspec, width=4, justify=tk.RIGHT)
        l_sep4 = ttk.Label(area_tspec, text=":")
        e_tsMin = ttk.Entry(area_tspec, width=4, justify=tk.RIGHT)
        l_sep5 = ttk.Label(area_tspec, text=":")
        e_tsSec = ttk.Entry(area_tspec, width=4, justify=tk.RIGHT)
        f_sep5 = ttk.Frame(area_tspec)
        b_tsClear = ttk.Button(area_tspec, text=UI_CLEAR, command=self.clear_timespec)
        # alternate layout: looks more polished than the other one
        b_tsAdd = ttk.Button(
            area_tspec,
            width=BUTTON_STANDARD_WIDTH_SMALL,
            text=UI_ADD,
            command=self.add_timespec,
        )
        b_tsDel = ttk.Button(
            area_tspec,
            width=BUTTON_STANDARD_WIDTH_SMALL,
            text=UI_DEL,
            command=self.del_timespec,
        )

        # time specification section: arrange items in frame
        l_tsDate.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cb_tsYear.grid(row=0, column=1, sticky=tk.W, padx=PAD, pady=PAD)
        l_sep1.grid(row=0, column=2, sticky=tk.W, pady=PAD)
        cb_tsMonth.grid(row=0, column=3, sticky=tk.W, padx=PAD, pady=PAD)
        l_sep2.grid(row=0, column=4, sticky=tk.W, pady=PAD)
        cb_tsDay.grid(row=0, column=5, sticky=tk.W, padx=PAD, pady=PAD)
        l_tsOr.grid(row=0, column=6, sticky=tk.W, padx=PAD, pady=PAD)
        l_tsDayOfWeek.grid(row=0, column=7, sticky=tk.W, padx=PAD, pady=PAD)
        cb_tsDayOfWeek.grid(row=0, column=8, sticky=tk.W, padx=PAD, pady=PAD)
        f_sep3.grid(row=0, column=9, sticky=tk.W, padx=PAD, pady=PAD)
        l_tsTime.grid(row=0, column=10, sticky=tk.W, padx=PAD, pady=PAD)
        e_tsHour.grid(row=0, column=11, sticky=tk.W, padx=PAD, pady=PAD)
        l_sep4.grid(row=0, column=12, sticky=tk.W, pady=PAD)
        e_tsMin.grid(row=0, column=13, sticky=tk.W, padx=PAD, pady=PAD)
        l_sep5.grid(row=0, column=14, sticky=tk.W, pady=PAD)
        e_tsSec.grid(row=0, column=15, sticky=tk.W, padx=PAD, pady=PAD)
        f_sep5.grid(row=0, column=16, sticky=tk.W, padx=PAD, pady=PAD)
        b_tsClear.grid(row=0, column=17, sticky=tk.W, padx=PAD, pady=PAD)
        b_tsAdd.grid(row=0, column=18, sticky=tk.EW, padx=PAD, pady=PAD)
        b_tsDel.grid(row=0, column=19, sticky=tk.EW, padx=PAD, pady=PAD)

        s_sep10 = ttk.Separator(area)

        # timespec list section
        area_tslist = ttk.Frame(area)
        l_timeSpecs = ttk.Label(area_tslist, text=UI_FORM_CURRENTTIMESPECS_SC)
        # build a scrolled frame for the treeview
        sftv_timeSpecs = ttk.Frame(area_tslist)
        tv_timeSpecs = ttk.Treeview(
            sftv_timeSpecs,
            columns=("seq", "specs"),
            show="",
            displaycolumns=(1,),
            height=5,
        )
        sb_timeSpecs = ttk.Scrollbar(
            sftv_timeSpecs, orient=tk.VERTICAL, command=tv_timeSpecs.yview
        )
        tv_timeSpecs.configure(yscrollcommand=sb_timeSpecs.set)
        tv_timeSpecs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_timeSpecs.pack(side=tk.RIGHT, fill=tk.Y)

        # timespec list section: arrange items in frame
        l_timeSpecs.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        sftv_timeSpecs.grid(row=1, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        tv_timeSpecs.bind("<ButtonRelease-1>", lambda _: self.recall_timespec())

        # arrange top items in the grid
        area_tspec.grid(row=0, column=0, sticky=tk.EW)
        s_sep10.grid(row=10, column=0, sticky=tk.EW, pady=PAD)
        area_tslist.grid(row=11, column=0, sticky=tk.NSEW)

        # expand appropriate sections
        area.columnconfigure(0, weight=1)
        area.rowconfigure(11, weight=1)
        area_tspec.columnconfigure(9, weight=1)
        area_tspec.columnconfigure(16, weight=1)
        area_tslist.columnconfigure(0, weight=1)
        area_tslist.rowconfigure(1, weight=1)

        # bind data to widgets
        self.data_bind("ts_year", cb_tsYear, TYPE_INT)
        self.data_bind("ts_month", cb_tsMonth, TYPE_STRING)
        self.data_bind("ts_day", cb_tsDay, TYPE_INT)
        self.data_bind("ts_dow", cb_tsDayOfWeek, TYPE_STRING)
        self.data_bind("ts_hour", e_tsHour, TYPE_INT, lambda x: 0 <= x < 24)
        self.data_bind("ts_min", e_tsMin, TYPE_INT, lambda x: 0 <= x < 60)
        self.data_bind("ts_sec", e_tsSec, TYPE_INT, lambda x: 0 <= x < 60)
        self.data_bind("timespec_selection", tv_timeSpecs)

        # propagate widgets that need to be accessed
        self._tv_timeSpecs = tv_timeSpecs

        # update the form
        self._updateform()

    def clear_timespec(self):
        self.data_set("ts_year")
        self.data_set("ts_month")
        self.data_set("ts_day")
        self.data_set("ts_dow")
        self.data_set("ts_hour")
        self.data_set("ts_min")
        self.data_set("ts_sec")

    def add_timespec(self):
        if m := self.data_get("ts_month"):
            try:
                month = _MONTHS_MAP[m]
            except ValueError:
                # come on, you can do better
                month = None
        else:
            month = None
        if d := self.data_get("ts_dow"):
            try:
                dow = _WEEKDAYS_MAP[d]
            except ValueError:
                # see above
                dow = None
        else:
            dow = None
        year = self.data_get("ts_year")
        day = self.data_get("ts_day")
        hour = self.data_get("ts_hour")
        min = self.data_get("ts_min")
        sec = self.data_get("ts_sec")
        try:
            spec = TimeSpec(
                year=year,
                month=month,
                day=day,
                weekday=dow,
                hour=hour,
                minute=min,
                second=sec,
            )
        except ValueError:
            spec = None
        if spec:
            self._timespecs.append(spec)
            self._updatedata()
            self._updateform()

    def del_timespec(self):
        idx = self.data_get("timespec_selection")[0]
        del self._timespecs[idx]
        self._updatedata()
        self._updateform()

    def recall_timespec(self):
        sel = self.data_get("timespec_selection")
        if sel:
            spec = self._timespecs[self.data_get("timespec_selection")[0]]
            self.data_set("ts_year", spec.year)
            self.data_set(
                "ts_month", _MONTHS[spec.month] if spec.month is not None else None
            )
            self.data_set("ts_day", spec.day)
            self.data_set(
                "ts_dow", _WEEKDAYS_DISPLAY[spec.weekday] if spec.weekday else None
            )
            self.data_set("ts_hour", spec.hour)
            self.data_set("ts_min", spec.minute)
            self.data_set("ts_sec", spec.second)

    def clear_alltimespecs(self):
        # TODO: ask for confirmation
        self._timespecs = []
        self._updatedata()
        self._updateform()

    def _updatedata(self):
        e = []
        for timespec in self._timespecs:
            e.append(timespec.as_dict())
        self._item.time_specifications = e or None
        return super()._updatedata()

    def _updateform(self):
        self._tv_timeSpecs.delete(*self._tv_timeSpecs.get_children())
        idx = 0
        for ts in self._timespecs:
            hrspec = str(ts)
            self._tv_timeSpecs.insert("", iid=idx, values=(idx, hrspec), index=tk.END)
            idx += 1
        self.clear_timespec()
        return super()._updateform()


# end.
