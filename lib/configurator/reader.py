# reader
# read and parse a configuration file

from tomlkit import parse, items

# import item definitions
from ..items.item import ALL_AVAILABLE_ITEMS_D
from ..utility import write_warning


# read the configuration: this reader supports the `tags` entry as table
# so that items different from the standard ones and built on top of them
# can be correctly read and interpreted, and handled by the appropriate
# editor forms; unreadable items are skipped and a warning is printed to
# the standard output
def read_whenever_config(filename):
    with open(filename) as f:
        toml = f.read()
    doc = parse(toml)
    return whenever_config_from_doc(doc)


# this can be used to read the configuration from a document in memory
def whenever_config_from_doc(doc: items.Table):
    res_tasks = []
    res_conditions = []
    res_events = []
    res_globals = {
        'scheduler_tick_seconds': doc.get('scheduler_tick_seconds', 5),
        'randomize_checks_within_ticks': doc.get('randomize_checks_within_ticks', False),
        'tags': doc.get('tags', {}),
    }
    if 'task' in doc:
        for item_table in doc['task']:
            try:
                signature = 'task:%s' % item_table['type']
                tags = item_table.get('tags')
                if tags:
                    signature = '%s:%s' % (signature, tags['subtype'])
                t = ALL_AVAILABLE_ITEMS_D.get(signature)
                if t:
                    factory = t[2]
                    item = factory(item_table)
                    res_tasks.append(item)
                else:
                    write_warning("unknown signature (%s) for task `%s`" % (signature, item_table.get('name', '<unnamed>')))
            except KeyError:
                write_warning("skipping malformed task `%s`" % item_table.get('name', '<unnamed>'))
    if 'condition' in doc:
        for item_table in doc['condition']:
            try:
                signature = 'cond:%s' % item_table['type']
                tags = item_table.get('tags')
                if tags:
                    signature = '%s:%s' % (signature, tags['subtype'])
                t = ALL_AVAILABLE_ITEMS_D.get(signature)
                if t:
                    factory = t[2]
                    item = factory(item_table)
                    res_conditions.append(item)
                else:
                    write_warning("unknown signature (%s) for condition `%s`" % (signature, item_table.get('name', '<unnamed>')))
            except KeyError:
                write_warning("skipping malformed condition `%s`" % item_table.get('name', '<unnamed>'))
    if 'event' in doc:
        for item_table in doc['event']:
            try:
                signature = 'event:%s' % item_table['type']
                tags = item_table.get('tags')
                if tags:
                    signature = '%s:%s' % (signature, tags['subtype'])
                t = ALL_AVAILABLE_ITEMS_D.get(signature)
                if t:
                    factory = t[2]
                    item = factory(item_table)
                    res_events.append(item)
                else:
                    write_warning("unknown signature (%s) for event `%s`" % (signature, item_table.get('name', '<unnamed>')))
            except KeyError:
                write_warning("skipping malformed event `%s`" % item_table.get('name', '<unnamed>'))
    return (res_tasks, res_conditions, res_events, res_globals)


# end.
