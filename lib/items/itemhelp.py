# itemhelp.py
#
# item helper class

from tomlkit import table, array, aot, items

import re


# an error class that reports some more information about where the error is
class ConfigurationError(Exception):
    def __init__(
        self,
        item_name: str | None = None,
        entry_name: str | None = None,
        item_line: int | None = None,
        message: str | None = None,
    ):
        self.item_name = item_name
        self.entry_name = entry_name
        self.item_line = item_line
        self.message = message

    def __str__(self):
        iname = f"`{self.item_name}`" if self.item_name is not None else "<unknown>"
        iline = f"@{self.item_line}" if self.item_line is not None else ""
        ename = f"[`{self.entry_name}`]" if self.entry_name is not None else ""
        msg = f"`{self.message}`" if self.message is not None else "<unknown>"
        return f"{self.__class__.__name__}/item {iname}{ename}{iline}: {msg}"

    def __repr__(self):
        return str(self)


# this object can be used in place of an items.Table object, and it provides
# more fine-grained control on errors that could be found in a document
class CheckedTable(object):

    def __init__(self, t: items.Table, table_line: int|None=None):
        self._table = t
        self._table_line = table_line

    def get(self, entry: str, default=None):
        return self._table.get(entry, default)

    def get_check(self, entry: str, check=lambda _: True, default=None):
        v = self.get(entry, default)
        name = self.get("name")
        assert isinstance(name, str)
        if name is None:
            raise ConfigurationError(
                name,
                entry_name=entry,
                item_line=self._table_line,
                message=f"item has no name",
            )
        if not check(v):
            raise ConfigurationError(
                name,
                entry_name=entry,
                item_line=self._table_line,
                message=f"invalid value: {v}",
            )
        return v

    # booleans: the checking version is pretty useless but it is here for
    # thee sake of completeness
    def get_bool_check(self, entry, check=lambda _: True, default=None) -> bool | None:
        return self.get_check(
            entry,
            check=lambda x: (isinstance(x, bool) or x is None) and check(x),
            default=default,
        )

    def get_bool(self, entry, default=None) -> bool | None:
        return self.get_bool_check(entry, default=default)

    # integers: the unsigned and interval versions are common cases
    def get_int_check(self, entry, check=lambda _: True, default=None) -> int | None:
        return self.get_check(
            entry,
            check=lambda x: (isinstance(x, int) or x is None) and check(x),
            default=default,
        )

    def get_int(self, entry, default=None) -> int | None:
        return self.get_int_check(entry, default=default)

    def get_int_between(self, entry, min=0, max=None, default=None) -> int | None:
        assert max is None or (isinstance(max, int) and max >= min)
        chk = lambda x: x is None or (x >= min and (max is None or x <= max))
        return self.get_int_check(entry, check=chk, default=default)

    def get_int_unsigned(self, entry, default=None) -> int | None:
        return self.get_int_between(entry, default=default)

    # floats: integers are also accepted as floats
    def get_float_check(
        self, entry, check=lambda _: True, default=None
    ) -> float | None:
        v = self.get_check(
            entry,
            check=lambda x: (isinstance(x, int) or isinstance(x, float) or x is None)
            and check(x),
            default=default,
        )
        if v is not None:
            return float(v)
        else:
            return None

    def get_float(self, entry, default=None) -> float | None:
        return self.get_float_check(entry, default=default)

    def get_float_between(self, entry, min=0.0, max=None, default=None) -> float | None:
        assert max is None or (
            (isinstance(max, int) or isinstance(max, float)) and max >= min
        )
        chk = lambda x: x is None or (x >= min and (max is None or x <= max))
        return self.get_float_check(entry, check=chk, default=default)

    # strings: special cases are REs and being within a list of known strings
    def get_str_check(self, entry, check=lambda _: True, default=None) -> str | None:
        return self.get_check(
            entry,
            check=lambda x: (isinstance(x, str) or x is None) and check(x),
            default=default,
        )

    def get_str(self, entry, default=None) -> str | None:
        return self.get_str_check(entry, default=default)

    def get_str_check_re(self, entry, chkre: re.Pattern, default=None) -> str | None:
        chk = lambda x: x is None or bool(chkre.match(x))
        return self.get_str_check(entry, check=chk, default=default)

    def get_str_check_in(self, entry, chklist: list, default=None) -> str | None:
        chk = lambda x: x is None or x in chklist
        return self.get_str_check(entry, check=chk, default=default)

    # lists: the check function is applied to items
    def get_list_check(
        self, entry, check=lambda _: True, default=None
    ) -> items.Array | None:
        v = self.get_check(
            entry,
            check=lambda x: (isinstance(x, list) or x is None),
            default=default,
        )
        if v is None:
            return None
        ret = array()
        for x in v:
            if not check(x):
                # an unnamed item would have raised an exception above in `get_check()`
                name = self.get("name")
                raise ConfigurationError(
                    name,
                    entry_name=entry,
                    item_line=self._table_line,
                    message=f"invalid value: {x} in {v}",
                )
            ret.append(x)
        return ret

    def get_list(self, entry, default=None) -> items.Array | None:
        return self.get_list_check(entry, default=default)

    def get_list_of_type_check(
        self, entry, ty: type, check=lambda _: True, default=None
    ) -> items.Array | None:
        return self.get_list_check(
            entry, check=lambda x: isinstance(x, ty) and check(x), default=default
        )

    def get_list_of_type(self, entry, ty: type, default=None) -> items.Array | None:
        return self.get_list_of_type_check(entry, ty=ty, default=default)

    def get_list_of_int_check(
        self, entry, check=lambda _: True, default=None
    ) -> items.Array | None:
        return self.get_list_of_type_check(entry, ty=int, check=check, default=default)

    def get_list_of_int(
        self, entry, check=lambda _: True, default=None
    ) -> items.Array | None:
        return self.get_list_of_int_check(entry, default=default)

    def get_list_of_int_between(
        self, entry, min=0, max=None, default=None
    ) -> items.Array | None:
        assert max is None or (isinstance(max, int) and max >= min)
        chk = lambda x: x is None or (x >= min and (max is None or x <= max))
        return self.get_list_of_int_check(entry, check=chk, default=default)

    def get_list_of_int_unsigned(self, entry, default=None) -> items.Array | None:
        return self.get_list_of_int_between(entry, default=default)

    def get_list_of_float_check(
        self, entry, check=lambda _: True, default=None
    ) -> items.Array | None:
        return self.get_list_of_type_check(
            entry, ty=float, check=check, default=default
        )

    def get_list_of_float(
        self, entry, check=lambda _: True, default=None
    ) -> items.Array | None:
        return self.get_list_of_float_check(entry, default=default)

    def get_list_of_float_between(
        self, entry, min=0.0, max=None, default=None
    ) -> items.Array | None:
        assert max is None or (
            (isinstance(max, int) or isinstance(max, float)) and max >= min
        )
        chk = lambda x: x is None or (x >= min and (max is None or x <= max))
        return self.get_list_of_float_check(entry, check=chk, default=default)

    def get_list_of_str_check(
        self, entry, check=lambda _: True, default=None
    ) -> items.Array | None:
        return self.get_list_of_type_check(entry, ty=str, check=check, default=default)

    def get_list_of_str(
        self, entry, check=lambda _: True, default=None
    ) -> items.Array | None:
        return self.get_list_of_str_check(entry, default=default)

    def get_list_of_str_re(
        self, entry, chkre: re.Pattern, default=None
    ) -> items.Array | None:
        chk = lambda x: x is None or bool(chkre.match(x))
        return self.get_list_of_str_check(entry, check=chk, default=default)

    def get_list_of_str_in(
        self, entry, chklist: list, default=None
    ) -> items.Array | None:
        chk = lambda x: x is None or x in chklist
        return self.get_list_of_str_check(entry, check=chk, default=default)

    # dicts: keys are always strings, check functions applied to keys/items
    def get_dict_check(
        self, entry, k_check=lambda _: True, e_check=lambda _: True, default=None
    ) -> items.Table | None:
        v = self.get_check(
            entry,
            check=lambda x: isinstance(x, dict) or x is None,
            default=default,
        )
        if v is None:
            return None
        ret = table()
        for k in v:
            if not isinstance(k, str) or not k_check(k):
                # an unnamed item would have raised an exception above in `get_check()`
                name = self.get("name")
                raise ConfigurationError(
                    name,
                    entry_name=entry,
                    item_line=self._table_line,
                    message=f"invalid sub-entry name: '{k}' in {v}",
                )
            x = v[k]
            if not e_check(x):
                # an unnamed item would have raised an exception above in `get_check()`
                name = self.get("name")
                raise ConfigurationError(
                    name,
                    entry_name=entry,
                    item_line=self._table_line,
                    message=f"invalid value: {x} in {v}['{k}']",
                )
            ret.append(k, x)
        return ret

    def get_dict_check_keys_vs_values(
        self, entry, check=lambda _k, _v: True, default=None
    ) -> items.Table | None:
        v = self.get_check(
            entry,
            check=lambda x: isinstance(x, dict) or x is None,
            default=default,
        )
        if v is None:
            return None
        ret = table()
        for k in v:
            x = v[k]
            if not isinstance(k, str) or not check(k, x):
                # an unnamed item would have raised an exception above in `get_check()`
                name = self.get("name")
                raise ConfigurationError(
                    name,
                    entry_name=entry,
                    item_line=self._table_line,
                    message=f"invalid sub-entry: '{k}' in {v} is {x}",
                )
            ret.append(k, x)
        return ret

    def get_dict_check_keys(
        self, entry, k_check=lambda _: True, default=None
    ) -> items.Table | None:
        return self.get_dict_check(entry, k_check=k_check, default=default)

    def get_dict(self, entry, default=None) -> items.Table | None:
        return self.get_dict_check(entry, default=None)

    def get_dict_check_keys_in(
        self, entry, k_list: list, default=None
    ) -> items.Table | None:
        return self.get_dict_check_keys(
            entry, k_check=lambda x: x in k_list, default=default
        )

    def get_dict_check_keys_re(
        self, entry, k_re: re.Pattern, default=None
    ) -> items.Table | None:
        return self.get_dict_check_keys(
            entry, k_check=lambda x: bool(k_re.match(x)), default=default
        )

    def get_dict_check_and_keys_re(
        self, entry, k_re: re.Pattern, e_check=lambda _: True, default=None
    ) -> items.Table | None:
        return self.get_dict_check(
            entry,
            k_check=lambda x: bool(k_re.match(x)),
            e_check=e_check,
            default=default,
        )

    def get_dict_check_and_keys_in(
        self, entry, k_list: list, e_check=lambda _: True, default=None
    ) -> items.Table | None:
        return self.get_dict_check(
            entry, k_check=lambda x: x in k_list, e_check=e_check, default=default
        )

    # arrays of dicts: checks applied to each dict
    def get_array_of_dict_check(
        self, entry, k_check=lambda _: True, e_check=lambda _: True, default=None
    ) -> items.AoT | None:
        v = self.get_check(
            entry,
            check=lambda x: isinstance(x, list) or x is None,
            default=default,
        )
        if v is None:
            return None
        i = 0
        ret = aot()
        for elem in v:
            telem = table()
            for k in elem:
                if not isinstance(k, str) or not k_check(k):
                    # an unnamed item would have raised an exception above in `get_check()`
                    name = self.get("name")
                    raise ConfigurationError(
                        name,
                        entry_name=entry,
                        item_line=self._table_line,
                        message=f"invalid sub-entry name (in table array at element {i}): '{k}' in {v}",
                    )
                x = elem[k]
                if not e_check(x):
                    # an unnamed item would have raised an exception above in `get_check()`
                    name = self.get("name")
                    raise ConfigurationError(
                        name,
                        entry_name=entry,
                        item_line=self._table_line,
                        message=f"invalid value (in table array at element {i}): {x} in {v}['{k}']",
                    )
                telem.append(k, x)
            ret.append(telem)
            i += 1
        return ret

    def get_array_of_dict_check_keys_vs_values(
        self, entry, check=lambda _k, _v: True, default=None
    ) -> items.AoT | None:
        v = self.get_check(
            entry,
            check=lambda x: isinstance(x, list) or x is None,
            default=default,
        )
        if v is None:
            return None
        i = 0
        ret = aot()
        for elem in v:
            telem = table()
            for k in elem:
                x = elem[k]
                if not isinstance(k, str) or not check(k, x):
                    # an unnamed item would have raised an exception above in `get_check()`
                    name = self.get("name")
                    raise ConfigurationError(
                        name,
                        entry_name=entry,
                        item_line=self._table_line,
                        message=f"invalid sub-entry (in table array at element {i}): '{k}' in {v} is {x}",
                    )
                telem.append(k, x)
            ret.append(telem)
            i += 1
        return ret

    def get_array_of_dict_check_keys(
        self, entry, k_check=lambda _: True, default=None
    ) -> items.AoT | None:
        return self.get_array_of_dict_check(entry, k_check=k_check, default=default)

    def get_array_of_dict(self, entry, default=None) -> items.AoT | None:
        return self.get_array_of_dict_check(entry, default=None)

    def get_array_of_dict_check_keys_in(
        self, entry, k_list: list, default=None
    ) -> items.AoT | None:
        return self.get_array_of_dict_check_keys(
            entry, k_check=lambda x: x in k_list, default=default
        )

    def get_array_of_dict_check_keys_re(
        self, entry, k_re: re.Pattern, default=None
    ) -> items.AoT | None:
        return self.get_array_of_dict_check_keys(
            entry, k_check=lambda x: bool(k_re.match(x)), default=default
        )

    def get_array_of_dict_check_and_keys_re(
        self, entry, k_re: re.Pattern, e_check=lambda _: True, default=None
    ) -> items.AoT | None:
        return self.get_array_of_dict_check(
            entry,
            k_check=lambda x: bool(k_re.match(x)),
            e_check=e_check,
            default=default,
        )

    def get_array_of_dict_check_and_keys_in(
        self, entry, k_list: list, e_check=lambda _: True, default=None
    ) -> items.AoT | None:
        return self.get_array_of_dict_check(
            entry, k_check=lambda x: x in k_list, e_check=e_check, default=default
        )


# end.
