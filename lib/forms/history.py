# history box

from lib.i18n.strings import *

from lib.utility import sg
from lib.icons import APP_ICON32 as APP_ICON

from datetime import datetime, timedelta

from lib.runner.history import History


# layout generator (fixed)
def layout_main():
    return [
        [ sg.T(UI_FORM_HISTORYITEMS_SC) ],
        [ sg.Table(
            [['' for x in range(6)] for y in range(5)],
            auto_size_columns=False,
            headings=[
                UI_FORM_HS_TIME,
                UI_FORM_HS_TASK,
                UI_FORM_HS_TRIGGER,
                UI_FORM_HS_DURATION,
                UI_FORM_HS_SUCCESS,
                UI_FORM_HS_MESSAGE,
            ],
            key='-HISTORY-',
            num_rows=10,
            # NOTE: the following is not supported
            # cols_justification=('center', 'left', 'left', 'center', 'center', 'left'),
            justification='center',
            # NOTE: widths are empirically determined, should be tested on
            # other platform to verify that they are suitable anyway
            col_widths=(15, 16, 16, 7, 4, 38),
            expand_x=True, expand_y=True,
        ) ],
        [ sg.Push(), sg.B_OK(UI_OK, key='-OK-') ]
    ]


# form class: this form is fixed and will not be derived
class form_History(object):

    def __init__(self, history=None):
        self._form = sg.Window(UI_TITLE_HISTORY, layout=layout_main(), icon=APP_ICON, size=(960, 640), finalize=True)
        self.__dont_update = []
        self._history = []
        if history:
            self.set_history(history)
        self._data = {}     # for compatibility
        self._item = None   # for compatibility

    def _updateform(self):
        self._form['-HISTORY-'].update(self._history)
        for k in self._data:
            if k not in self.__dont_update:
                v = self._data[k]
                if v is None:
                    v = ''
                self._form[k].update(v)
        self._form.refresh()

    def _updateitem(self):
        pass

    def dont_update(self, *keys):
        self.__dont_update += keys

    def set_history(self, history):
        h = list(
            [
                x['time'][:-7].replace("T", " "),
                x['task'],
                x['trigger'],
                ("%.2fs" % x['duration'].total_seconds()).ljust(7),
                SYM_OK if x['success'] == 'OK' else SYM_UNKNOWN if x['success'] == 'IND' else SYM_FAIL,
                x['message'],
            ]
            for x in history
        )
        h.reverse()
        self._history = h

    def process_event(self, event, values):
        if values:
            self._data = values.copy()
        if event in [sg.WIN_CLOSED, '-CANCEL-']:
            self._form.close()
            return False
        elif event == '-OK-':
            self._form.close()
            return True
        return None

    def run(self):
        self._updateform()
        while True:             # Event Loop
            event, values = self._form.read()
            ret = self.process_event(event, values)
            if ret is not None:
                if ret:
                    break
                else:
                    return None
            self._updateform()
        self._updateitem()
        self._form.close()
        return self._item


# end.
