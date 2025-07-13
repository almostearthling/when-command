# logging module: log all records issued by the subprocess according to the
# chosen log level.
#
# As per **whenever** documentation, a log record has the following format:
#
# {
#     "header": {
#         "application": "whenever",
#         "level": "TRACE",
#         "time": "2023-11-04T11:17:25.257970"
#     },
#     "contents": {
#         "context": {
#             "action": "scheduler_tick",
#             "emitter": "MAIN",
#             "item": null,
#             "item_id": null
#         },
#         "message": "condition Cond_TIME tested with no outcome (tasks not executed)",
#         "message_type": {
#             "status": "MSG",
#             "when": "PROC"
#         }
#     }
# }


from threading import Lock
from datetime import datetime

from ..i18n.strings import CLI_APP

from ..repocfg import AppConfig

# levels are fixed, format mimics original **whenever** format
_LOGLEVELS = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR"]
_LOGFMT = "{time} ({application}) {level} {emitter} {action}{itemstr}: [{when}/{status}]: {message}"


# for now a very basic logger: improvements will be rotation and persistence
class Logger(object):

    def __init__(self, filename, level, app=None):
        self._logfile = open(filename, "w")
        self._level = level
        self._level_num = _LOGLEVELS.index(self._level)
        self._app = app
        self._mutex = Lock()

    def log(self, record):
        with self._mutex:
            time = record["header"]["time"]
            application = record["header"]["application"]
            level = record["header"]["level"]
            emitter = record["contents"]["context"]["emitter"]
            action = record["contents"]["context"]["action"]
            item = record["contents"]["context"]["item"]
            item_id = record["contents"]["context"]["item_id"]
            when = record["contents"]["message_type"]["when"]
            status = record["contents"]["message_type"]["status"]
            message = record["contents"]["message"]
            if item is not None and item_id is not None:
                itemstr = " %s/%s" % (item, item_id)
            else:
                itemstr = ""
            ln = _LOGLEVELS.index(level)
            if when == "HIST":
                if AppConfig.get("DEBUG"):
                    self._logfile.write(
                        "%s\n"
                        % _LOGFMT.format(
                            time=time,
                            application=application,
                            level=level,
                            emitter=emitter,
                            action=action,
                            itemstr=itemstr,
                            when=when,
                            status=status,
                            message=message,
                        )
                    )
                    self._logfile.flush()
                return False
            elif when == "BUSY":
                if self._app:
                    if status == "YES":
                        self._app.send_event("<<SchedSetBusy>>")
                    else:
                        self._app.send_event("<<SchedSetNotBusy>>")
            elif when == "PAUSE":
                if self._app:
                    if status == "YES":
                        self._app.send_event("<<SchedSetPaused>>")
                    else:
                        self._app.send_event("<<SchedSetNotPaused>>")
            else:
                if ln >= self._level_num:
                    self._logfile.write(
                        "%s\n"
                        % _LOGFMT.format(
                            time=time,
                            application=application,
                            level=level,
                            emitter=emitter,
                            action=action,
                            itemstr=itemstr,
                            when=when,
                            status=status,
                            message=message,
                        )
                    )
                    self._logfile.flush()
            return True

    # return a valid logging context
    def context(self):
        return Context(logger=self)


class Context(object):

    # constants
    LEVEL_ERROR = "ERROR"
    LEVEL_WARNING = "WARN"
    LEVEL_INFO = "INFO"
    LEVEL_DEBUG = "DEBUG"
    LEVEL_TRACE = "TRACE"

    WHEN_START = "START"
    WHEN_PROC = "PROC"
    WHEN_END = "END"

    STATUS_OK = "OK"
    STATUS_FAIL = "FAIL"
    STATUS_ERR = "ERR"
    STATUS_MSG = "MSG"

    # create a logging context
    def __init__(
        self,
        level=None,
        emitter=None,
        action=None,
        item=None,
        item_id=None,
        when=None,
        status=None,
        message=None,
        logger=None,
    ):
        self._level = level or self.LEVEL_INFO
        self._emitter = emitter
        self._action = action
        self._item = item or None
        self._item_id = item_id or None
        self._when = when or "PROC"
        self._status = status or "OK"
        self._message = message
        self._logger = logger


    def update(
        self,
        level=None,
        emitter=None,
        action=None,
        item=None,
        item_id=None,
        when=None,
        status=None,
        message=None,
    ):
        if level is not None:
            self._level = level
        if emitter is not None:
            self._emitter = emitter
        if action is not None:
            self._action = action
        if item is not None:
            self._item = item
        if item_id is not None:
            self._item_id = item_id
        if when is not None:
            self._when = when
        if status is not None:
            self._status = status
        if message is not None:
            self._message = message

    def use(
        self,
        level=None,
        emitter=None,
        action=None,
        item=None,
        item_id=None,
        when=None,
        status=None,
        message=None,
    ):
        self.update(
            level,
            emitter,
            action,
            item,
            item_id,
            when,
            status,
            message,
        )
        return self

    def as_record(self):
        assert(self._message is not None)
        assert(self._emitter is not None)
        assert(self._action is not None)
        timestr = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        return {
            "header": {
                "time": timestr,
                "application": CLI_APP,
                "level": self._level.upper(),
            },
            "contents": {
                "context": {
                    "emitter": self._emitter,
                    "action": self._action,
                    "item": self._item,
                    "item_id": self._item_id,
                },
                "message_type": {
                    "when": self._when,
                    "status": self._status,
                },
                "message": self._message,
            },
        }

    def log(self, message=None):
        assert(self._logger is not None)
        if message is not None:
            self._message = str(message)
        self._logger.log(self.as_record())


# end.
