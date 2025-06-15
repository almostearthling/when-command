# global application configuration repository: this repository is implemented
# so that only one object of its type can be created, and the items that are
# inserted are _read-only_: the only way to update a configuration item is to
# delete it and add it back

_singleton_lock = False

from pygments.styles import get_style_by_name


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

    def __getitem__(self, key: str):
        return self.get(key)

    def __setitem__(self, key: str, value):
        self.set(key, value)

    def __delitem__(self, key: str):
        self.delete(key)

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
AppConfig = _AppConfiguration(
    {
        # this flag should be set to False on normal operation
        "DEBUG": True,

        # the application base name for configuration directory determination
        "CFGNAME": "Whenever",

        # milliseconds between log reads by the secondary thread
        "MSECS_BETWEEN_READS": 100.0,

        # history queue length
        "HISTORY_LENGTH": 100,

        # whether or not to reset conditions on workstation resume
        "RESET_CONDS_ON_RESUME": True,

        # configuration window size
        "SIZE_MAIN_FORM": (960, 640),

        # editor form size
        "SIZE_EDITOR_FORM": (960, 640),

        # new item chooser size
        "SIZE_NEWITEM_FORM": (640, 400),

        # history box size
        "SIZE_HISTORY_FORM": (960, 640),

        # about box size
        "SIZE_ABOUT_BOX": (480, 300),

        # menu box size
        "SIZE_MENU_BOX": (272, 440),

        # themes
        "DEFAULT_THEME_DARK": "darkly",
        "DEFAULT_THEME_LIGHT": "flatly",
        "DEFAULT_THEME_DEBUG": "morph",

        # editor themes
        "EDITOR_THEME_DARK": "ayu-dark",
        "EDITOR_THEME_LIGHT": "ayu-light",
        "EDITOR_THEME_DEBUG": "ayu-light",

        # ...
    }
)


__all__ = ["AppConfig"]


# end.
