# template for extra modules

# this header is common to all extra modules
from tomlkit import items, table

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from ..i18n.strings import *
from ..utility import check_not_none, append_not_none

from ..forms.ui import *


# since a condition is defined, the base form is the one for conditions
from ..forms.cond import form_Condition

# import item to derive from
from ..items.cond_command import CommandCondition


# imports specific to this module
import shutil



# resource strings (not internationalized for the moment)
ITEM_COND_TEMPLATE = "Template Condition"

_UI_TITLE_TEMPLATE = "%s: Template Condition Editor" % UI_APP
_UI_FORM_TEMPLATE_PARAM_SC = "Parameter is:"


# default values
_DEFAULT_PARAM_VALUE = "somestring"


# check for availability: include all needed checks in this function, may
# or may not include actually checking the hosting platform
def _available():
    if shutil.which('ls'):
        return True
    return False



# the specific item is derived from the actual parent item
class TemplateCondition(CommandCondition):

    # availability at class level: these variables *MUST* be set for all items
    item_type = 'command'
    item_subtype = 'template'
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
            self.tags.append('parameter1', _DEFAULT_PARAM_VALUE)
        
        self.updateitem()

    def updateitem(self):
        # set base item properties according to specific parameters in `tags`
        self.command = 'ls'
        self.command_arguments = ['-l', self.tags.get('parameter1', _DEFAULT_PARAM_VALUE)]
        self.startup_path = "."
        self.success_status = 0


# dedicated form definition derived directly from one of the base forms
class form_TemplateCondition(form_Condition):

    def __init__(self, tasks_available, item=None):

        # check that item is the expected one for safety, build one by default
        if item:
            assert(isinstance(item, TemplateCondition))
        else:
            item = TemplateCondition()
        super().__init__(_UI_TITLE_TEMPLATE, tasks_available, item)

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # build the UI elements as needed and configure the layout
        l_parameter1 = ttk.Label(area, text=_UI_FORM_TEMPLATE_PARAM_SC)
        e_parameter1 = ttk.Entry(area)
        self.data_bind('parameter1', e_parameter1, TYPE_STRING)

        l_parameter1.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_parameter1.grid(row=0, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)

        area.columnconfigure(1, weight=1)

        # always update the form at the end of initialization
        self._updateform()

    # update the form with the specific parameters (usually in the `tags`)
    def _updateform(self):
        self.data_set('parameter1', self._item.tags.get('parameter1'))
        return super()._updateform()
    
    # update the item from the form elements (usually update `tags`)
    def _updatedata(self):
        self._item.tags['parameter1'] = self.data_get('parameter1')
        return super()._updatedata()



# function common to all extra modules to declare class items as factories
def factories():
    return (TemplateCondition, form_TemplateCondition)


# end.
