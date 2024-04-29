# template for extra modules

# this header is common to all extra modules:
from lib.i18n.strings import *
from lib.utility import sg, check_not_none, append_not_none

import os
import sys
from tomlkit import items, table


# since a condition is defined, the base form is `form_Condition`; when
# deriving a task `form_Task` should be imported and `form_Event` for a
# derived event: the specialized forms for 
from lib.forms.cond import form_Condition

# here the actual item to derive from has to be imported
from lib.items.cond_command import CommandCondition


# imports specific to this module
import re
import shutil


# resource strings (not internationalized)
ITEM_COND_TEMPLATE = "Template Condition"

_UI_TITLE_TEMPLATE = "%s: Template Condition Editor" % UI_APP
_UI_FORM_TEMPLATE = "Template"
_UI_FORM_TEMPLATE_PARAM_SC = "Parameter is:"


# default values
_DEFAULT_PARAM_VALUE = "somestring"


# check for availability: include all needed checks in this function, may
# or may not include actually checking the hosting platform
def _available():
    if shutil.which('ls'):
        return True



# the specific item is derived from the actual parent item
class TemplateCondition(CommandCondition):

    # availability at class level: these variables *MUST* be set for all items
    item_type = 'command'
    item_subtype = 'sysload'
    item_hrtype = ITEM_COND_TEMPLATE
    available = _available()

    def __init__(self, t: items.Table=None) -> None:
        # first initialize the base class (mandatory)
        CommandCondition.__init__(self, t)

        # then set type (same as base), subtype and human readable name: this
        # is mandatory in order to correctly display the item in all forms
        self.type = self.item_type
        self.subtype = self.item_subtype
        self.hrtype = self.item_hrtype

        # initializin from a table should always have this form:
        if t:
            assert(t.get('type') == self.type)
            self.tags = t.get('tags')
            assert(isinstance(self.tags, items.Table))
            assert(self.tags.get('subtype') == self.subtype)
        
        # while creating a new item must always initialize specific parameters
        else:
            self.tags = table()
            self.tags.append('subtype', self.subtype)
            self.tags.append('parameter', _DEFAULT_PARAM_VALUE)
        
        self.updateitem()

    def updateitem(self):
        # set base item properties according to specific parameters in `tags`
        self.command = 'ls'
        self.command_arguments = ['-l', self.tags.get('parameter', _DEFAULT_PARAM_VALUE)]
        self.startup_path = "."
        self.success_status = 0


# the specialized form is directly derived from the generic item form: the
# following snippet is the layout that will be inserted in the variable part
def _form_layout():
    return [
        [ sg.Frame(_UI_FORM_TEMPLATE, [[
            sg.T(_UI_FORM_TEMPLATE_PARAM_SC),
            sg.I(key='-PARAMETER-', expand_x=True),
            sg.T("%"),
        ]], expand_x=True, expand_y=True) ]
    ]

class form_TemplateCondition(form_Condition):

    # initialization always follows this pattern, the only thing that has to
    # be fine tuned is the list of checks, if needed, that must be performed
    # on form fields to test the validity of entered values
    def __init__(self, tasks_available, item=None):
        if item:
            assert(isinstance(item, TemplateCondition))
        else:
            item = TemplateCondition()
        extra_layout = _form_layout()
        form_Condition.__init__(self, _UI_TITLE_TEMPLATE, tasks_available, extra_layout, item)
        self.add_checks(
            ('-PARAMETER-', _UI_FORM_TEMPLATE_PARAM_SC, lambda x: re.match(r"[a-zA-Z0-9_]+")),
        )

    # data to be sent to the form, usually corresponding to specific params
    def _updatedata(self):
        form_Condition._updatedata(self)
        if self._item:
            self._data['-PARAMETER-'] = self._item.tags.get('parameter')
        else:
            self._data['-PARAMETER-'] = str(_DEFAULT_PARAM_VALUE)

    # here the data is retrieved from the form fields and sent to the
    # specific `tags` table corresponding to the item
    def _updateitem(self):
        form_Condition._updateitem(self)
        if self._data['-PARAMETER-']:
            self._item.tags['parameter'] = int(self._data['-PARAMETER-'])
        else:
            self._item.tags['parameter'] = None

    # this utility might have to be defined (and in this case the super()
    # version must *always* be called), but in many cases it can just be
    # omitted - which has the same effect as defining it as below
    def process_event(self, event, values):
        return super().process_event(event, values)



# function common to all extra modules to declare class items as factories:
# this is mandatory and must return the item and the form in this order
def factories():
    return (TemplateCondition, form_TemplateCondition)


# end.
