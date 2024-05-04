# SimpleGUI modifications
#
# here are all the modifications to the SimpleGUI widgets so that they can
# be easily found and possibly tweaked in one single place

from lib.i18n.strings import *

# use the still-FOSS fork of PySimpleGUI
import FreeSimpleGUI as sg


# import required icons
from lib.icons import (
    APP_ICON32 as APP_ICON,
    OK_B_ICON112x24 as BTN_ICON_OK,
    CANCEL_B_ICON112x24 as BTN_ICON_CANCEL,
    EXIT_B_ICON112x24 as BTN_ICON_EXIT,
    ENTER_B_ICON112x24 as BTN_ICON_LOAD,
    SAVE_B_ICON112x24 as BTN_ICON_SAVE,
    ADD_B_ICON112x24 as BTN_ICON_ADD,
    DELETE_B_ICON112x24 as BTN_ICON_REMOVE,
    NEW_DOCUMENT_B_ICON112x24 as BTN_ICON_NEW,
    PENCIL_DRAWING_B_ICON112x24 as BTN_ICON_EDIT,
    FILE_B_ICON112x24 as BTN_ICON_FILE,
)


# local constants to modify the GUI library
_BUTTON_WIDTH = 12


# actual modifications to the GUI library

# 0. save current button constructor for use in modified buttons
sg._B = sg.B

sg.B()

# 1. make all buttons of the same width
sg.B = lambda *args, **kwargs: sg._B(
    *args, size=_BUTTON_WIDTH,
    **{k: v for k, v in kwargs.items() if k != 'size'}
    )

# 2. create some stock buttons
sg.B_OK = lambda *args, **kwargs: sg._B(
    *args, image_source=BTN_ICON_OK,
    **{k: v for k, v in kwargs.items() if k != 'image_source'}
    )

sg.B_CANCEL = lambda *args, **kwargs: sg._B(
    *args, image_source=BTN_ICON_CANCEL,
    **{k: v for k, v in kwargs.items() if k != 'image_source'}
    )

sg.B_EXIT = lambda *args, **kwargs: sg._B(
    *args, image_source=BTN_ICON_EXIT,
    **{k: v for k, v in kwargs.items() if k != 'image_source'}
    )

sg.B_LOAD = lambda *args, **kwargs: sg._B(
    *args, image_source=BTN_ICON_LOAD,
    **{k: v for k, v in kwargs.items() if k != 'image_source'}
    )

sg.B_SAVE = lambda *args, **kwargs: sg._B(
    *args, image_source=BTN_ICON_SAVE,
    **{k: v for k, v in kwargs.items() if k != 'image_source'}
    )

sg.B_ADD = lambda *args, **kwargs: sg._B(
    *args, image_source=BTN_ICON_ADD,
    **{k: v for k, v in kwargs.items() if k != 'image_source'}
    )

sg.B_DEL = lambda *args, **kwargs: sg._B(
    *args, image_source=BTN_ICON_REMOVE,
    **{k: v for k, v in kwargs.items() if k != 'image_source'}
    )

sg.B_NEW = lambda *args, **kwargs: sg._B(
    *args, image_source=BTN_ICON_NEW,
    **{k: v for k, v in kwargs.items() if k != 'image_source'}
    )

sg.B_BLANK = lambda *args, **kwargs: sg._B(
    *args, image_source=BTN_ICON_FILE,
    **{k: v for k, v in kwargs.items() if k != 'image_source'}
    )

sg.B_EDIT = lambda *args, **kwargs: sg._B(
    *args, image_source=BTN_ICON_EDIT,
    **{k: v for k, v in kwargs.items() if k != 'image_source'}
    )

# ...


# useful UI non-string constants such as themes
sg.DEFAULT_THEME_DARK = 'DarkGray4'
sg.DEFAULT_THEME_LIGHT = 'Default1'
sg.DEFAULT_THEME_DEBUG = 'DarkGreen5'


# end.
