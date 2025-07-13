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
_MSECS_BETWEEN_READS = AppConfig.get("MSECS_BETWEEN_READS")

# max length of task execution history
_HISTORY_LENGTH = AppConfig.get("HISTORY_LENGTH")


# the following function will be used to start a thread that actually
# reads subprocess output and possibly provides input to the subprocess
# itself: it has to be aware of the wrapper instance that calls it
def _logreader(wrapper):
    pipe = wrapper.pipe()
    sleep_seconds = _MSECS_BETWEEN_READS / 1000.0
    while wrapper.running():
        for line in iter(pipe.stdout.readline, ""):
            wrapper.process_output(line.strip())
        time.sleep(sleep_seconds)


# wrapper around the scheduler process
class Wrapper(object):

    def __init__(self, configpath, exepath, app=None):
        self._exepath = exepath
        self._config = configpath
        self._history = History(_HISTORY_LENGTH)
        self._logger = get_logger()
        self._thread = None
        self._pipe = None
        self._running = False
        self._log = self._logger.context().use(emitter="wrapper")
        app.set_wrapper(self)

    # used by the log reader
    def pipe(self):
        return self._pipe

    def running(self):
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
    def whenever_exit(self):
        if self._pipe.poll() is None and self._thread:
            sleep_seconds = _MSECS_BETWEEN_READS / 1000.0
            self._log.use(
                action="shutdown",
                level=self._log.LEVEL_INFO,
                when=self._log.WHEN_END,
                status=self._log.STATUS_MSG,
            ).log("shutdown the scheduler, waiting for activity to finish")
            self._pipe.stdin.write("exit\n")
            self._pipe.stdin.flush()
            self._running = False
            time.sleep(sleep_seconds)
            self._thread.join()
            for line in iter(self._pipe.stdout.readline, ""):
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

    def whenever_kill(self):
        if self._pipe.poll() is None and self._thread:
            sleep_seconds = _MSECS_BETWEEN_READS / 1000.0
            self._log.use(
                action="shutdown",
                level=self._log.LEVEL_INFO,
                when=self._log.WHEN_END,
                status=self._log.STATUS_MSG,
            ).log("shutdown the scheduler, forcing end of all activity")
            self._pipe.stdin.write("kill\n")
            self._pipe.stdin.flush()
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

    def whenever_pause(self):
        self._log.use(
            action="pause",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to pause the scheduler")
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("pause\n")
            self._pipe.stdin.flush()
            return True
        else:
            self._log.use(
                action="pause",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to pause")
            return False

    def whenever_resume(self):
        self._log.use(
            action="resume",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to resume the scheduler")
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("resume\n")
            self._pipe.stdin.flush()
            return True
        else:
            self._log.use(
                action="resume",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to resume")
            return False

    def whenever_reset_conditions(self, names=[]):
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
            self._pipe.stdin.write("reset_conditions %s\n" % " ".join(names))
            self._pipe.stdin.flush()
            return True
        else:
            self._log.use(
                action="reset",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to reset conditions")
            return False

    def whenever_suspend_condition(self, name):
        self._log.use(
            action="suspend",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to suspend condition `%s`" % name)
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("suspend_condition %s\n" % name)
            self._pipe.stdin.flush()
            return True
        else:
            self._log.use(
                action="suspend",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to suspend condition")
            return False

    def whenever_resume_condition(self, name):
        self._log.use(
            action="unsuspend",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to resume condition `%s`" % name)
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("resume_condition %s\n" % name)
            self._pipe.stdin.flush()
            return True
        else:
            self._log.use(
                action="unsuspend",
                level=self._log.LEVEL_ERROR,
                when=self._log.WHEN_PROC,
                status=self._log.STATUS_FAIL,
            ).log("no active scheduler, failed to resume condition")
            return False

    def whenever_reload_configuration(self):
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("configure %s\n" % self._config)
            self._pipe.stdin.flush()
            return True
        else:
            return False

    def whenever_trigger(self, name):
        self._log.use(
            action="trigger",
            level=self._log.LEVEL_DEBUG,
            when=self._log.WHEN_PROC,
            status=self._log.STATUS_MSG,
        ).log("attempting to trigger event `%s`" % name)
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("trigger %s\n" % name)
            self._pipe.stdin.flush()
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
    def start(self):
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
            for line in iter(self._pipe.stdout.readline, ""):
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
