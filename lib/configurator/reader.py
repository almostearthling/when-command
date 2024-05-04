# reader
# read and parse a configuration file

from tomlkit import parse

# import item definitions
from lib.items.item import ALL_AVAILABLE_ITEMS_D


# read the configuration: this reader supports the `tags` entry as table
# so that items different from the standard ones and built on top of them
# can be correctly read and interpreted, and handled by the appropriate
# editor forms
def read_whenever_config(filename):
    with open(filename) as f:
        toml = f.read()
    doc = parse(toml)
    res_tasks = []
    res_conditions = []
    res_events = []
    res_globals = {
        'scheduler_tick_seconds': doc.get('scheduler_tick_seconds', 5),
        'randomize_checks_within_ticks': doc.get('randomize_checks_within_ticks', False),
    }
    if 'task' in doc:
        for item_table in doc['task']:
            signature = 'task:%s' % item_table['type']
            tags = item_table.get('tags')
            if tags:
                signature = '%s:%s' % (signature, tags['subtype'])
            t = ALL_AVAILABLE_ITEMS_D.get(signature)
            if t:
                factory = t[2]
                item = factory(item_table)
            else:
                item = None
            if item:
                res_tasks.append(item)
    if 'condition' in doc:
        for item_table in doc['condition']:
            signature = 'cond:%s' % item_table['type']
            tags = item_table.get('tags')
            if tags:
                signature = '%s:%s' % (signature, tags['subtype'])
            t = ALL_AVAILABLE_ITEMS_D.get(signature)
            if t:
                factory = t[2]
                item = factory(item_table)
            else:
                item = None
            if item:
                res_conditions.append(item)
    if 'event' in doc:
        for item_table in doc['event']:
            signature = 'event:%s' % item_table['type']
            tags = item_table.get('tags')
            if tags:
                signature = '%s:%s' % (signature, tags['subtype'])
            t = ALL_AVAILABLE_ITEMS_D.get(signature)
            if t:
                factory = t[2]
                item = factory(item_table)
            else:
                item = None
            if item:
                res_events.append(item)
    return (res_tasks, res_conditions, res_events, res_globals)


# end.
