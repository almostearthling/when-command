# writer
# write a configuration file according to passed values and items

from tomlkit import document, comment, item, aot
from time import strftime

from ..utility import is_private_item_name
from ..i18n.strings import UI_APP


# the comment text constants for the configuration file are defined here
COMMENT_PUBLIC_SECTION = "global parameters and user defined items"
COMMENT_PRIVATE_ITEMS = "private items: please do not modify below this line"


# all items have an `as_table()` utility that converts them to TOML tables
# this writer separates private items from user created ones
def write_whenever_config(filename, tasks, conditions, events, globals):
    head = document()
    doc = document()
    priv = document()
    mod_time = strftime("%Y-%m-%d @%H:%M:%S")
    head.add(comment(f"{UI_APP}: {mod_time}"))
    head.add(comment(COMMENT_PUBLIC_SECTION))
    for k in globals:
        if globals[k] is not None:
            doc.add(k, item(globals[k]))
    priv.add(comment(COMMENT_PRIVATE_ITEMS))
    p = aot()
    t = aot()
    for elem in tasks:
        if is_private_item_name(elem.name):
            p.append(elem.as_table())
        else:
            t.append(elem.as_table())
    doc.append("task", t)
    priv.append("task", p)
    p = aot()
    t = aot()
    for elem in conditions:
        if is_private_item_name(elem.name):
            p.append(elem.as_table())
        else:
            t.append(elem.as_table())
    doc.append("condition", t)
    priv.append("condition", p)
    p = aot()
    t = aot()
    for elem in events:
        if is_private_item_name(elem.name):
            p.append(elem.as_table())
        else:
            t.append(elem.as_table())
    doc.append("event", t)
    priv.append("event", p)
    with open(filename, "w") as f:
        f.write(head.as_string())
        f.write("\n")
        f.write(doc.as_string())
        f.write("\n")
        f.write(priv.as_string())


# end.
