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
import sys
import shutil



# resource strings (not internationalized for the moment)
ITEM_COND_REMOVABLEDRIVE = "Removable Drive Available Condition"

_UI_TITLE_REMOVABLEDRIVE = "%s: Removable Drive Condition Editor" % UI_APP
_UI_FORM_REMOVABLEDRIVE_LABEL_SC = "Expected label:"

_UI_FORM_SPECIFY_DRIVE_LETTER = "Specify drive letter"
_UI_FORM_EXPECTED_LETTER_SC = "Expected drive letter:"


# default values
_DEFAULT_DRIVE_LABEL = "DRIVE"
_DEFAULT_DRIVE_LETTER = ""


# check for availability: include all needed checks in this function, may
# or may not include actually checking the hosting platform
def _available():
    if sys.platform == 'win32':
        if shutil.which("pwsh.exe"):
            return True
        return False
    else:
        return False



# the specific item is derived from the actual parent item
class RemovableDrivePresent(CommandCondition):

    # availability at class level: these variables *MUST* be set for all items
    item_type = 'command'
    item_subtype = 'removabledrive_win'
    item_hrtype = ITEM_COND_REMOVABLEDRIVE
    available = _available()

    def __init__(self, t: items.Table=None) -> None:
        # first initialize the base class (mandatory)
        CommandCondition.__init__(self, t)

        # then set type (same as base), subtype and human readable name: this
        # is mandatory in order to correctly display the item in all forms
        self.type = self.item_type
        self.subtype = self.item_subtype
        self.hrtype = self.item_hrtype

        # initializing from a table should always have this form:
        if t:
            assert(t.get('type') == self.type)
            self.tags = t.get('tags')
            assert(isinstance(self.tags, items.Table))
            assert(self.tags.get('subtype') == self.subtype)

        # while creating a new item must always initialize specific parameters
        else:
            self.tags = table()
            self.tags.append('subtype', self.subtype)
            self.tags.append('drive_label', _DEFAULT_DRIVE_LABEL)
            self.tags.append('drive_letter', _DEFAULT_DRIVE_LETTER)

        self.updateitem()

    def updateitem(self):
        # set base item properties according to specific parameters in `tags`

        # the check is performed using WMI objects: [System.IO.DriveType] is
        # a system enum, and ::Removable is the fixed value 2; 
        label = self.tags.get('drive_label', _DEFAULT_DRIVE_LABEL)
        letter = self.tags.get('drive_letter', _DEFAULT_DRIVE_LETTER)
        cmdline = (
            "Get-WmiObject Win32_Volume -Filter (\"" +
            "DriveType={0}" +
            " and Label='%s'" % label +
            ((" and DriveLetter='%s'" % letter) if letter else "") +
            "\" -f [int][System.IO.DriveType]::Removable)"
        )
        self.command = 'pwsh.exe'
        self.command_arguments = [
            '-Command',
            cmdline,
        ]
        self.startup_path = "."
        self.success_stdout = label
        self.case_sensitive = False
        self.check_after = 60
        self.recur_after_failed_check = True


# dedicated form definition derived directly from one of the base forms
class form_RemovableDrivePresent(form_Condition):

    def __init__(self, tasks_available, item=None):

        # check that item is the expected one for safety, build one by default
        if item:
            assert(isinstance(item, RemovableDrivePresent))
        else:
            item = RemovableDrivePresent()
        super().__init__(_UI_TITLE_REMOVABLEDRIVE, tasks_available, item)

        # list the drive letters to create a combo box
        drive_letters = list("%s:" % x for x in "DEFGHIJKLMNOPQRSTUVWXYZ")

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # build the UI elements as needed and configure the layout
        l_driveLabel = ttk.Label(area, text=_UI_FORM_REMOVABLEDRIVE_LABEL_SC)
        e_driveLabel = ttk.Entry(area)
        self.data_bind('drive_label', e_driveLabel, TYPE_STRING)
        sep1 = ttk.Separator(area)

        ck_specifyLetter = ttk.Checkbutton(area, text=_UI_FORM_SPECIFY_DRIVE_LETTER)
        l_driveLetter = ttk.Label(area, text=_UI_FORM_EXPECTED_LETTER_SC)
        cb_driveLetter = ttk.Combobox(area, values=drive_letters, state='readonly')

        l_driveLabel.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        e_driveLabel.grid(row=0, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)
        sep1.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=PAD)
        ck_specifyLetter.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=PAD, pady=PAD)
        l_driveLetter.grid(row=3, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cb_driveLetter.grid(row=3, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.data_bind('specify_letter', ck_specifyLetter)
        self.data_bind('drive_letter', cb_driveLetter, TYPE_STRING)

        ck_specifyLetter.bind('<ButtonPress-1>', lambda _: self._check_specify_letter())
        ck_specifyLetter.bind('<KeyPress-space>', lambda _: self._check_specify_letter())

        area.columnconfigure(1, weight=1)

        # propagate widget that have to be accessible
        self._cb_driveLetter = cb_driveLetter

        # always update the form at the end of initialization
        self._updateform()

    def _check_specify_letter(self):
        # we use the opposite of the value because of <ButtonPress-1>: anyway
        # the <ButtonRelease-1> counterpart does not work so well (same thing
        # for <KeyPress-space>, while <KeyRelease-space> does better)
        not_spec = self.data_get('specify_letter')
        if not_spec:
            self._cb_driveLetter.config(state=tk.DISABLED)
            self._item.tags['drive_letter'] = ""
        else:
            self._cb_driveLetter.config(state='readonly')
            sel = self.data_get('drive_letter') or "D:"
            self._item.tags['drive_letter'] = sel

    # update the form with the specific parameters (usually in the `tags`)
    def _updateform(self):
        self.data_set('drive_label', self._item.tags.get('drive_label'))
        if not self._item.tags.get('drive_letter'):
            self.data_set('specify_letter', False)
            self._cb_driveLetter.config(state=tk.DISABLED)
        else:
            self.data_set('specify_letter', True)
            self._cb_driveLetter.config(state='readonly')
        return super()._updateform()

    # update the item from the form elements (usually update `tags`)
    def _updatedata(self):
        self._item.tags['drive_label'] = self.data_get('drive_label')
        self._item.tags['drive_letter'] = self.data_get('drive_letter') if self.data_get('specify_letter') else ""
        self._item.updateitem()
        return super()._updatedata()



# function common to all extra modules to declare class items as factories
def factories():
    return (RemovableDrivePresent, form_RemovableDrivePresent)


# end.
