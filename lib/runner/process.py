# scheduler runner: implementation of the scheduler runner along with a
# secondary thread dedicated to reading its output

import sys
import time
import subprocess
import threading

import json

from ..utility import get_logger

from .history import History

from ..repocfg import AppConfig


# some constants:

# milliseconds between log reads
_MSECS_BETWEEN_READS: float = AppConfig.get("MSECS_BETWEEN_READS", 100.0)   # type: ignore

# max length of task execution history
_HISTORY_LENGTH = AppConfig.get("HISTORY_LENGTH")


# the following function will be used to start a thread that actually
# reads subprocess output and possibly provides input to the subprocess
# itself: it has to be aware of the wrapper instance that calls it
def _logreader(wrapper) -> None:
    pipe = wrapper.pipe()
    sleep_seconds = _MSECS_BETWEEN_READS / 1000.0
    while wrapper.running():
        for line in iter(pipe.stdout.readline, ""):
            wrapper.process_output(line.strip())
        time.sleep(sleep_seconds)


# wrapper around the scheduler process
class Wrapper(object):

    def __init__(self, configpath, exepath, app=None) -> None:
        self._exepath = exepath
        self._config = configpath
        self._history = History(_HISTORY_LENGTH)
        self._logger = get_logger()
        self._thread = None
        self._pipe = None
        self._running = False
        self._log = self._logger.context().use(emitter="FRONTEND")
        if app is not None:
            app.set_wrapper(self)

    # used by the log reader
    def pipe(self) -> None | subprocess.Popen[str]:
        return self._pipe

    def running(self) -> bool:
        return self._running and self._pipe is not None

    # used by the tray menu to feed the history box
    def get_history(self):
        return self._history.get_copy()

    # use the logger to determine whether a line is pertinent to history
    def process_output(self, line):
        if line:
            log_record = json.loads(line)
            if not self._logger.log(log_record):
                self._history.append(log_record)

    # the following functions, which have a `whenever_` prefix, are actually
    # commands that are sent to the spawned **whenever** process
    def whenever_exit(self) -> bool:
        if self._pipe is None:
            self._log.use(
                action="shutdown",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_ERR,
            ).log("scheduler not started, cannot shutdown")
            return False
        if self._pipe.poll() is None and self._thread:
            sleep_seconds = _MSECS_BETWEEN_READS / 1000.0
            self._log.use(
                action="shutdown",
                level=self._log.LEVEL_INFO,
                when=self._log.WHEN_END,
                status=self._log.STATUS_MSG,
            ).log("shutdown the scheduler, waiting for activity to finish")
            self._pipe.stdin.write("exit\n")    # type: ignore
            self._pipe.stdin.flush()            # type: ignore
            self._running = False
            time.sleep(sleep_seconds)
            self._thread.join()
            for line in iter(self._pipe.stdout.readline, ""):   # type: ignore
                self.process_output(line.strip())
            self._log.use(
                action="shutdown",
                level=self._log.LEVEL_INFO,
                when=self._log.WHEN_END,
                status=self._log.STATUS_OK,
            ).log("scheduler successfully exited")
            return True
        else:
            self._log.use(
                action="shutdown",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to shut down")
            return False

    def whenever_kill(self) -> bool:
        if self._pipe is None:
            self._log.use(
                action="shutdown",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_ERR,
            ).log("scheduler not started, cannot shutdown")
            return False
        if self._pipe.poll() is None and self._thread:
            sleep_seconds = _MSECS_BETWEEN_READS / 1000.0
            self._log.use(
                action="shutdown",
                level=self._log.LEVEL_INFO,
                when=self._log.WHEN_END,
                status=self._log.STATUS_MSG,
            ).log("shutdown the scheduler, forcing end of all activity")
            self._pipe.stdin.write("kill\n")    # type: ignore
            self._pipe.stdin.flush()            # type: ignore
            self._running = False
            time.sleep(sleep_seconds)
            self._thread.join()
            self._log.use(
                action="shutdown",
                level=self._log.LEVEL_INFO,
                when=self._log.WHEN_END,
                status=self._log.STATUS_OK,
            ).log("scheduler successfully exited")
            return True
        else:
            self._log.use(
                action="shutdown",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to shut down")
            return False

    def whenever_pause(self) -> bool:
        if self._pipe is None:
            self._log.use(
                action="pause",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_ERR,
            ).log("scheduler not started, cannot pause")
            return False
        self._log.use(
            action="pause",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to pause the scheduler")
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("pause\n")   # type: ignore
            self._pipe.stdin.flush()            # type: ignore
            return True
        else:
            self._log.use(
                action="pause",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to pause")
            return False

    def whenever_resume(self) -> bool:
        if self._pipe is None:
            self._log.use(
                action="resume",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_ERR,
            ).log("scheduler not started, cannot resume")
            return False
        self._log.use(
            action="resume",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to resume the scheduler")
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("resume\n")  # type: ignore
            self._pipe.stdin.flush()            # type: ignore
            return True
        else:
            self._log.use(
                action="resume",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to resume")
            return False

    def whenever_reset_conditions(self, names=[]) -> bool:
        if self._pipe is None:
            self._log.use(
                action="reset",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_ERR,
            ).log("scheduler not started, cannot reset conditions")
            return False
        self._log.use(
            action="reset",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to resume conditions: %s" % (
            "ALL" if len(names) == 0 else
            ", ".join(list("`%s`" % x for x in names))
        ))
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("reset_conditions %s\n" % " ".join(names))   # type: ignore
            self._pipe.stdin.flush()    # type: ignore
            return True
        else:
            self._log.use(
                action="reset",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to reset conditions")
            return False

    def whenever_suspend_condition(self, name) -> bool:
        if self._pipe is None:
            self._log.use(
                action="suspend",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_ERR,
            ).log("scheduler not started, cannot suspend condition")
            return False
        self._log.use(
            action="suspend",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to suspend condition `%s`" % name)
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("suspend_condition %s\n" % name) # type: ignore
            self._pipe.stdin.flush()    # type: ignore
            return True
        else:
            self._log.use(
                action="suspend",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to suspend condition")
            return False

    def whenever_resume_condition(self, name) -> bool:
        if self._pipe is None:
            self._log.use(
                action="unsuspend",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_ERR,
            ).log("scheduler not started, cannot resume condition")
            return False
        self._log.use(
            action="unsuspend",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to resume condition `%s`" % name)
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("resume_condition %s\n" % name)  # type: ignore
            self._pipe.stdin.flush()    # type: ignore
            return True
        else:
            self._log.use(
                action="unsuspend",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to resume condition")
            return False

    def whenever_reload_configuration(self) -> bool:
        if self._pipe is None:
            self._log.use(
                action="reload",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_ERR,
            ).log("scheduler not started, cannot reload configiration")
            return False
        self._log.use(
            action="reload",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to reload configuration")
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("configure %s\n" % self._config) # type: ignore
            self._pipe.stdin.flush()    # type: ignore
            return True
        else:
            self._log.use(
                action="reload",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to reload configuration")
            return False

    def whenever_trigger(self, name) -> bool:
        if self._pipe is None:
            self._log.use(
                action="reload",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_END,
                status=self._log.STATUS_ERR,
            ).log("scheduler not started, cannot trigger event")
            return False
        self._log.use(
            action="trigger",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to trigger event `%s`" % name)
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("trigger %s\n" % name)   # type: ignore
            self._pipe.stdin.flush()    # type: ignore
            return True
        else:
            self._log.use(
                action="trigger",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to reload configuration")
            return False

    # start the wrapper and spawn both **whenever** and the reader
    def start(self) -> bool:
        self._log.use(
            action="startup",
            level=self._log.LEVEL_INFO,
            when=self._log.WHEN_START,
            status=self._log.STATUS_MSG,
        ).log("starting the scheduler")
        self._pipe = subprocess.Popen(
            [self._exepath, "--log-level", "trace", "--log-json", self._config],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            text=True,
            creationflags=(
                subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
            ),
        )
        self._thread = threading.Thread(target=_logreader, args=[self])
        self._running = True
        self._thread.start()
        sleep_seconds = _MSECS_BETWEEN_READS / 1000.0
        time.sleep(sleep_seconds)
        if self._pipe.poll() is not None:
            if self._thread.is_alive():
                self._log.use(
                    action="startup",
                    level=self._log.LEVEL_ERROR,
                    when=self._log.WHEN_START,
                    status=self._log.STATUS_ERR,
                ).log("scheduler exited unexpectedly")
                self._thread.join()
            for line in iter(self._pipe.stdout.readline, ""):   # type: ignore
                self.process_output(line.strip())
            self._running = False
            return False
        self._log.use(
            action="startup",
            level=self._log.LEVEL_INFO,
            when=self._log.WHEN_END,
            status=self._log.STATUS_OK,
        ).log("scheduler successfully started")
        return True


# end.
