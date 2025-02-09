# check for presence of a removable drive


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
from ..items.cond_dbus import DBusCondition


# imports specific to this module
import sys
import shutil


# resource strings (not internationalized for the moment)
ITEM_HR_NAME = "Removable Drive Available Condition"

_UI_FORM_TITLE = "%s: Removable Drive Condition Editor" % UI_APP

_UI_FORM_REMOVABLEDRIVE_DEVICE_SC = "Device:"


# default values
_DEFAULT_DRIVE_DEVICE = "DRIVE"


# the DBus query template (as JSON, see whenever documentation): here we
# rely on the MediaAvailable flag, which can be found directly by querying
# the GetManagedObjects() method of the UDisks2 Object Manager; the property
# is at a quite nested point, in a structure made up of three levels of
# dictionaries (see how the index is nested) and luckily JSON allows for a
# more readable construction of the query
_DBUS_QUERY = """
{
    "index": [
        "/org/freedesktop/UDisks2/drives/%s",
        "org.freedesktop.UDisks2.Drive",
        "MediaAvailable"
    ],
    "operator": "eq",
    "value": true
}
""".strip()



# check for availability
def _available():
    if sys.platform == 'linux':
        try:
            import dbus
        except:
            return False
        return True
    else:
        return False



# the specific item is derived from the actual parent item
class RemovableDrivePresent(DBusCondition):

    # availability at class level: these variables *MUST* be set for all items
    item_type = 'command'
    item_subtype = 'removabledrive_linux'
    item_hrtype = ITEM_HR_NAME
    available = _available()

    def __init__(self, t: items.Table=None) -> None:
        # first initialize the base class (mandatory)
        DBusCondition.__init__(self, t)

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
            self.tags.append('drive_name', _DEFAULT_DRIVE_DEVICE)

        self.updateitem()

    def updateitem(self):
        # set base item properties according to specific parameters in `tags`

        # the check is performed a DBus query
        query = _DBUS_QUERY % self.tags.get('drive_name', _DEFAULT_DRIVE_DEVICE)
        self.bus = ":system"
        self.service = "org.freedesktop.UDisks2"
        self.object_path = "/org/freedesktop/UDisks2"
        self.interface = "org.freedesktop.DBus.ObjectManager"
        self.method = "GetManagedObjects"
        self.parameter_check = query
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
        super().__init__(_UI_FORM_TITLE, tasks_available, item)

        # this will work here since the module is available
        import dbus

        # now find drive names
        prefix = "/org/freedesktop/UDisks2/drives/"
        bus = dbus.SystemBus()
        o = bus.get_object(
            "org.freedesktop.UDisks2",
            "/org/freedesktop/UDisks2",
            )
        o_iface = dbus.Interface(o, "org.freedesktop.DBus.ObjectManager")
        mgobjs = o_iface.GetManagedObjects()
        drive_names = []
        for k in mgobjs.keys().filter(lambda s: s.startswith(prefix)):
            if mgobjs[k]['org.freedesktop.UDisks2.Drive']['Removable']:
                drive_names.append(str(mgobjs[k])[len(prefix):])

        # create a specific frame for the contents
        area = ttk.Frame(super().contents)
        area.grid(row=0, column=0, sticky=tk.NSEW)
        PAD = WIDGET_PADDING_PIXELS

        # build the UI elements as needed and configure the layout
        l_deviceName = ttk.Label(area, text=_UI_FORM_REMOVABLEDRIVE_DEVICE_SC)
        cb_deviceName = ttk.Combobox(area, values=drive_names)
        self.data_bind('drive_name', cb_deviceName, TYPE_STRING)

        l_deviceName.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)
        cb_deviceName.grid(row=0, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)

        area.columnconfigure(1, weight=1)

        # always update the form at the end of initialization
        self._updateform()

    # update the form with the specific parameters (usually in the `tags`)
    def _updateform(self):
        self.data_set('drive_name', self._item.tags.get('drive_name'))

    # update the item from the form elements (usually update `tags`)
    def _updatedata(self):
        self._item.tags['drive_name'] = self.data_get('drive_name')
        self._item.updateitem()
        return super()._updatedata()



# function common to all extra modules to declare class items as factories
def factories():
    return (RemovableDrivePresent, form_RemovableDrivePresent)


# end.
