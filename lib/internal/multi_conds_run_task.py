# multiple conditions to run tasks (aka confluence)
#
# private items that enable the condition "confluence" feature (issue #187),
# that is the possibility for a task to depend on more than one condition.
#
# The idea is to have a persistence file where *all* the conditions that are
# defined as concurring to the triggering of tasks are recorded: this file is
# periodically read, and when all the conditions that concur to a specific
# task (or list/set of tasks) are found in the file, the following happens:
#
# 1. the conditions are _removed_ from the file
# 2. the corresponding task or list/set of tasks is executed
#
# For this purpose, the conditions that concur to tasks will all be bound to
# a single Lua-based task, which writes their name in the file, while multiple
# conditions will be built for each task group to be activated by multiple
# conditions.
#
# The persistence file does not need to be structured, it only has to be read,
# operated on, and written quickly. No concurrent reads or writes should be
# allowed, assuming that one instance of a verified condition cannot concur to
# multiple task groups (this is arbitrary, but cleaner than the opposite), and
# that once a certain set of conditions that concur to a task group is verified
# it has to be atomically removed from the list.
#
# The condition names are "mangled" before being written to the persistence
# file, but the mangling is simple and effective: it only consists of a pair
# of colons around the name. This ensures that no name given to other items
# can conflict with the mangled name, since brackets are not allowed chars
# for item names. This also allow for a quick and precise search without the
# need for special considerations: if the name of a condition is "Cond1", for
# instance, searching for the string ":Cond1:" will match only the presence
# of "Cond1" and not, for instance, "ThatCond1" - which is mangled, instead,
# as ":ThatCond1:". This also eliminates the need for multiple lines, regex
# search, and other complications. The colon character is used because it has
# no special meaning in Lua pattern syntax, so the `string.gsub` function can
# be used.

import sys
import os

from ..utility import get_tempdir



# constants
_MCRT_PERSIST_FILE = ".mcrt_persist"
_MCRT_LOCK_FILE = ".mcrt_persist.lock"


_LUA_LIBRARY = '''
-- to be eventually replaced by the contents of ../../support/mcrt_lib.lua
'''





# the persistence file is the file that contains the list of conditions that
# concur to task triggering which have been successfully checked
def mcrt_persist_file():
    return os.path.join(get_tempdir(), _MCRT_PERSIST_FILE)

# the lock file is checked when trying to access the persistence file: no other
# access (including read-only access) will be performed when the lock file is
# present, which indicates a current access
def mcrt_lock_file():
    return os.path.join(get_tempdir(), _MCRT_LOCK_FILE)


# ...to be continued




# end.
