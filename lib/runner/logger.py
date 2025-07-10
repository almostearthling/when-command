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

from ..repocfg import AppConfig

# levels are fixed, format mimics original **whenever** format
_LOGLEVELS = ["trace", "debug", "info", "warn", "error"]
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
            ln = _LOGLEVELS.index(level.lower())
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


# end.
