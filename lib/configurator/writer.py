# writer
# write a configuration file according to passed values and items

from tomlkit import document, comment, item, aot
from time import strftime

from ..i18n.strings import UI_APP


# all items have an `as_table()` utility that converts them to TOML tables
def write_whenever_config(filename, tasks, conditions, events, globals) -> None:
    doc = document()
    mod_time = strftime("%Y-%m-%d @%H:%M:%S")
    doc.add(comment(f"{UI_APP}: {mod_time}"))
    for k in globals:
        if globals[k] is not None:
            doc.add(k, item(globals[k]))
    t = aot()
    for elem in tasks:
        t.append(elem.as_table())
    doc.append("task", t)
    t = aot()
    for elem in conditions:
        t.append(elem.as_table())
    doc.append("condition", t)
    t = aot()
    for elem in events:
        t.append(elem.as_table())
    doc.append("event", t)
    with open(filename, "w") as f:
        f.write(doc.as_string())


# end.
