# scheduler runner: implementation of the scheduler runner along with a
# secondary thread dedicated to reading its output

import time
import subprocess
import threading

import json

from lib.runner.logger import Logger
from lib.runner.history import History

from lib.repocfg import AppConfig


# some constants:

# milliseconds between log reads
_MSECS_BETWEEN_READS = AppConfig.get('MSECS_BETWEEN_READS')

# max length of task execution history
_HISTORY_LENGTH = AppConfig.get('HISTORY_LENGTH')


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

    def __init__(self, configpath, exepath, logfile, loglevel):
        self._exepath = exepath
        self._logfile = logfile
        self._config = configpath
        self._history = History(_HISTORY_LENGTH)
        self._logger = Logger(logfile, loglevel)
        self._thread = None
        self._pipe = None
        self._running = False


    # utilities to read inner values
    # def thread(self):
    #     return self._thread

    # def logfile(self):
    #     return self._logfile

    # used by the log reader
    def pipe(self):
        return self._pipe

    def running(self):
        return self._running

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
            self._pipe.stdin.write("exit\n")
            self._pipe.stdin.flush()
            self._running = False
            time.sleep(sleep_seconds)
            self._thread.join()
            for line in iter(self._pipe.stdout.readline, ""):
                self.process_output(line.strip())
            return True
        else:
            return False

    def whenever_kill(self):
        if self._pipe.poll() is None and self._thread:
            sleep_seconds = _MSECS_BETWEEN_READS / 1000.0
            self._pipe.stdin.write("kill\n")
            self._pipe.stdin.flush()
            self._running = False
            time.sleep(sleep_seconds)
            self._thread.join()
            return True
        else:
            return False

    def whenever_pause(self):
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("pause\n")
            self._pipe.stdin.flush()
            return True
        else:
            return False

    def whenever_resume(self):
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("resume\n")
            self._pipe.stdin.flush()
            return True
        else:
            return False

    def whenever_reset_conditions(self, names=[]):
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("reset_conditions %s\n" % " ".join(names))
            self._pipe.stdin.flush()
            return True
        else:
            return False

    def whenever_suspend_condition(self, name):
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("suspend_condition %s\n" % name)
            self._pipe.stdin.flush()
            return True
        else:
            return False

    def whenever_resume_condition(self, name):
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("resume_condition %s\n" % name)
            self._pipe.stdin.flush()
            return True
        else:
            return False

    def whenever_trigger(self, name):
        if self._pipe.poll() is None and self._thread:
            self._pipe.stdin.write("trigger %s\n" % name)
            self._pipe.stdin.flush()
            return True
        else:
            return False

    # start the wrapper and spawn both **whenever** and the reader
    def start(self):
        self._pipe = subprocess.Popen(
            [self._exepath, '--log-level', 'trace', '--log-json', self._config],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            text=True,
        )
        self._thread = threading.Thread(target=_logreader, args=[self])
        self._running = True
        self._thread.start()
        sleep_seconds = _MSECS_BETWEEN_READS / 1000.0
        time.sleep(sleep_seconds)
        if self._pipe.poll() is not None:
            if self._thread.is_alive():
                self._thread.join()
            for line in iter(self._pipe.stdout.readline, ""):
                self.process_output(line.strip())
            self._running = False
            return False
        return True


# end.
