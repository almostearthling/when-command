# history manager
#
# builds a limited log that only holds history records and task duration


from datetime import datetime


class History(object):

    def __init__(self, maxlen):
        self._history = []
        self._maxlen = maxlen
        self._open_records_timing = {}

    def append(self, record):
        time = record["header"]["time"]
        # application = record['header']['application']
        # level = record['header']['level']
        # emitter = record['contents']['context']['emitter']
        # action = record['contents']['context']['action']
        item = record["contents"]["context"]["item"]
        item_id = record["contents"]["context"]["item_id"]
        when = record["contents"]["message_type"]["when"]
        status = record["contents"]["message_type"]["status"]
        message = record["contents"]["message"]
        itemstr = "%s/%s" % (item, item_id)
        if when == "HIST":
            if status == "START":
                self._open_records_timing[itemstr] = time
            else:
                end = datetime.fromisoformat(time)
                start = datetime.fromisoformat(self._open_records_timing[itemstr])
                del self._open_records_timing[itemstr]
                duration = end - start
                if len(self._history) == self._maxlen:
                    self._history = self._history[1:]
                ident, msg = message.split(" ", 1)
                outcome, t = ident.split("/")
                _, trigger = t.split(":")
                self._history.append(
                    {
                        "time": time,
                        "task": item,
                        "task_id": item_id,
                        "trigger": trigger,
                        "duration": duration,
                        "success": outcome,
                        "message": msg,
                    }
                )
        else:
            # ignore the message
            pass

    def get(self):
        return self._history

    def get_copy(self):
        return self._history.copy()


# end.
