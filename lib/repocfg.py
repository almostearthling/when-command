# global application configuration repository: this repository is implemented
# so that only one object of its type can be created, and the items that are
# inserted are _read-only_: the only way to update a configuration item is to
# delete it and add it back

_singleton_lock = False

class _AppConfiguration(object):

    def __init__(self, initial_table=None):
        global _singleton_lock
        if _singleton_lock:
            raise TypeError("only an instance of the configuration can exist")
        _singleton_lock = True
        if initial_table is None:
            self._table = {}
        else:
            assert isinstance(initial_table, dict)
            self._table = {}
            for k in initial_table:
                self._table[k] = initial_table[k]

    def set(self, key: str, value):
        if key in self._table:
            raise ValueError("value already set for '%s': delete it first" % key)
        self._table[key] = value

    def delete(self, key: str):
        if key in self._table:
            del self._table[key]

    def get(self, key: str, default=None):
        if key in self._table:
            return self._table[key]
        else:
            return default

    def __str__(self) -> str:
        keys = list(self._table.keys())
        keys.sort()
        s = ""
        for k in keys:
            s += "%s: %s\n" % (k, repr(self._table[k]))
        return s


# the unique instance of the configuration object: note that it also contains
# some initial configuration values that might have to be modified according
# to the type of release (eg. the DEBUG flag, see below)
AppConfig = _AppConfiguration({
    # this flag should be set to False on normal operation
    'DEBUG': True,

    # the application base name for configuration directory determination
    'CFGNAME': 'Whenever',

    # milliseconds between log reads by the secondary thread
    'MSECS_BETWEEN_READS': 100.0,

    # history queue length
    'HISTORY_LENGTH': 100,

    # ...
})


# end.
