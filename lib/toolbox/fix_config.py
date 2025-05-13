# Fix configuration from legacy names and item types to new ones

from ..items.item import ALL_AVAILABLE_ITEMS, ALL_AVAILABLE_ITEMS_D
from ..configurator.reader import read_whenever_config
from ..configurator.writer import write_whenever_config

from tomlkit import item, parse

# the following is a list of conversions, identified by the current signature
# which represents the target item that should be built from the table that
# is found in the old-style table: the old style and new style signatures are
# matched and the appropriate conversion function is called on the old table
# in order to produce a new one for the specific item; to achieve this the
# old and new item factories are used, taken from the respective factory mods
CONVERSIONS = {
    # ('cond:wmi:sysload', 'cond:command:sysload'): cond_wmi_sysload__cond_command_sysload,
    # ...
}