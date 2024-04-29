# extra items module
#
# dynamically load all items in this directory

import os


# export two dictionaries, one for successfully loaded items/forms and the
# other for items that could not be loaded and thus will not be enabled
factories = {}
not_loaded = {}


# load all Python modules in the directory, except the ones whose filename
# begins with an underscore: in this way a `_template.py` module can be put
# in the directory to actually serve as a template; note that, since all
# modules should export the `factories()` function, the names of the item
# and form classes is ininfluent -- if not for default item names in the
# editor forms
_basepath = os.path.dirname(__file__)
for elem in [x[:-3] for x in os.listdir(_basepath) if x.lower().endswith('.py') and not x.startswith('_')]:
    try:
        exec("from lib.extra import %s" % elem)
        factories[elem] = eval("%s.factories()" % elem)
    except Exception as e:
        not_loaded[elem] = e


# only export the useful objects, that is, the two dictionaries
__all__ = ['factories', 'not_loaded']


# end
