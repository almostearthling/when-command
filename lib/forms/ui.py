# UI single file

import tkinter as tk

# from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap import dialogs
import ttkbootstrap.constants as ttkc
from ttkbootstrap.icons import Icon
from ttkbootstrap_icons_mat import MatIcon as Icons

from typing import Callable, Any

from ..utility import get_icon, get_appicon, get_tkroot
from .colors import *


# default strings for UI (overwritten by `i18n.strings`)
BTN_OK = "OK"
BTN_CANCEL = "Cancel"
BTN_YES = "Yes"
BTN_NO = "No"
BTN_CLOSE = "Close"
BTN_EXIT = "Exit"
BTN_QUIT = "Quit"
BTN_ADD = "Add"
BTN_REMOVE = "Remove"
BTN_DELETE = "Delete"
BTN_SAVE = "Save"
BTN_LOAD = "Load"
BTN_NEW = "New"
BTN_EDIT = "Edit"
BTN_MODIFY = "Modify"
BTN_RELOAD = "Reload"
BTN_RESET = "Reset"

BTN_FILE_D = "File..."
BTN_FOLDER_D = "Folder..."

try:
    from ..i18n.strings import *
except ImportError:
    pass




# default UI values
DIALOG_PADDING_MAIN = (8, 10)
DIALOG_PADDING_INNER = (4, 6)
WIDGET_PADDING_PIXELS = 5
BUTTON_STANDARD_WIDTH = 12
BUTTON_STANDARD_WIDTH_SMALL = 8
BUTTON_STANDARD_WIDTH_LARGE = 31


# common settings for all standard buttons
class _btn_Base(ttk.Button):
    def __init__(self, master, text, icon, command, enabled):
        if isinstance(icon, bytes):
            self._image = get_icon(icon)
        else:
            self._image = icon
        self._style = ttk.Style()
        self._style.configure(
            style="stdbutton.TButton", anchor=tk.EW, width=BUTTON_STANDARD_WIDTH
        )
        if command is None:
            command = ""
        super().__init__(
            master,
            text=text,
            image=self._image,
            compound=tk.LEFT,
            command=command,
            style="stdbutton.TButton",
        )
        self.enable(enabled)

    def enable(self, enabled=True):
        if enabled:
            active = ["!disabled"]
        else:
            active = ["disabled"]
        self.state(active)


class _btn_MenuEntry(ttk.Button):
    def __init__(self, master, text, icon, command, enabled):
        if isinstance(icon, bytes):
            self._image = get_icon(icon)
        else:
            self._image = icon
        self._style = ttk.Style()
        self._style.configure(
            style="stdbutton.TButton", anchor=tk.W, width=BUTTON_STANDARD_WIDTH_LARGE
        )
        if command is None:
            command = ""
        super().__init__(
            master,
            text=text,
            image=self._image,
            compound=tk.LEFT,
            command=command,
            style="stdbutton.TButton",
        )
        self.enable(enabled)

    def enable(self, enabled=True):
        if enabled:
            active = ["!disabled"]
        else:
            active = ["disabled"]
        self.state(active)


# standard buttons
class BtnOK(_btn_Base):
    def __init__(self, master, text=BTN_OK, command=None, enabled=True):
        icon = Icons("check", color=GREEN).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnCancel(_btn_Base):
    def __init__(self, master, text=BTN_CANCEL, command=None, enabled=True):
        icon = Icons("cancel", color=RED).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnClose(_btn_Base):
    def __init__(self, master, text=BTN_CLOSE, command=None, enabled=True):
        icon = Icons("stop-circle", color=ORANGE).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnExit(_btn_Base):
    def __init__(self, master, text=BTN_EXIT, command=None, enabled=True):
        icon = Icons("exit-run", color=RED).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnAdd(_btn_Base):
    def __init__(self, master, text=BTN_ADD, command=None, enabled=True):
        icon = Icons("plus-box", color=YELLOW).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnRemove(_btn_Base):
    def __init__(self, master, text=BTN_REMOVE, command=None, enabled=True):
        icon = Icons("minus-box", color=RED).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnDelete(_btn_Base):
    def __init__(self, master, text=BTN_DELETE, command=None, enabled=True):
        icon = Icons("trash-can", color=LTGRAY).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnLoad(_btn_Base):
    def __init__(self, master, text=BTN_LOAD, command=None, enabled=True):
        icon = Icons("folder", color=GREEN).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnSave(_btn_Base):
    def __init__(self, master, text=BTN_SAVE, command=None, enabled=True):
        icon = Icons("floppy", color=CYAN).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnNew(_btn_Base):
    def __init__(self, master, text=BTN_NEW, command=None, enabled=True):
        icon = Icons("file", color=WHITE).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnEdit(_btn_Base):
    def __init__(self, master, text=BTN_EDIT, command=None, enabled=True):
        icon = Icons("file-edit", color=YELLOW).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnModify(_btn_Base):
    def __init__(self, master, text=BTN_MODIFY, command=None, enabled=True):
        icon = Icons("pencil", color=YELLOW).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnReset(_btn_Base):
    def __init__(self, master, text=BTN_RESET, command=None, enabled=True):
        icon = Icons("power-cycle", color=RED).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


class BtnReload(_btn_Base):
    def __init__(self, master, text=BTN_RELOAD, command=None, enabled=True):
        icon = Icons("reload", color=GREEN).image
        super().__init__(
            master,
            text=text,
            icon=icon,
            command=command,
            enabled=enabled,
        )


# ...


# button box constants
BBOX_OK = "ok"
BBOX_CANCEL = "cancel"
BBOX_ADD = "add"
BBOX_REMOVE = "remove"
BBOX_DELETE = "delete"
BBOX_EDIT = "edit"
BBOX_MODIFY = "modify"
BBOX_LOAD = "load"
BBOX_SAVE = "save"
BBOX_NEW = "new"
BBOX_CLOSE = "close"
BBOX_EXIT = "exit"
BBOX_QUIT = "quit"
BBOX_RESET = "reset"
BBOX_RELOAD = "reload"
BBOX_SEPARATOR = "*"


# type constants
TYPE_BOOL = "bool"
TYPE_INT = "int"
TYPE_FLOAT = "float"
TYPE_STRING = "str"


# Message box derived from ttkbootstrap message dialogs: offers static methods
# that map the ones provided by Tkinter standard messagebox entity
class MessageBox(object):
    def __init__(self, parent=None):
        self._parent = parent

    def showerror(self, title, message):
        dialogs.Messagebox.show_error(message, title, parent=self._parent)

    def showinfo(self, title, message):
        dialogs.Messagebox.show_info(message, title, parent=self._parent)

    def showwarning(self, title, message):
        dialogs.Messagebox.show_warning(message, title, parent=self._parent)

    def askyesno(self, title, message):
        buttons = [BTN_YES, BTN_NO]
        dialog = dialogs.MessageDialog(
            message,
            title,
            buttons=buttons,
            icon=Icon.question,
            parent=self._parent,
        )
        dialog.show()
        return True if dialog.result == BTN_YES else False

    def askokcancel(self, title, message):
        buttons = [BTN_OK, BTN_CANCEL]
        dialog = dialogs.MessageDialog(
            message,
            title,
            buttons=buttons,
            icon=Icon.question,
            parent=self._parent,
        )
        dialog.show()
        return True if dialog.result == BTN_OK else False


# base dialog box class: provide a button strip at the bottom and a contents
# area that can be used to display the needed widgets; also provides utilities
# to bind widgets to retrievable values
class ApplicationForm(object):

    # the initialization sets the form dimensions and prepares the default
    # button box, binding the displayed buttons to default actions: buttons
    # in the button box are chosen by specifying one of the above constants
    # and one instance of BBOX_SEPARATOR: not specifying the position of the
    # separator is equivalent to assigning it the first position, specifying
    # it more than one time can lead to unexpected layouts.
    def __init__(
        self,
        title: str,
        size: tuple[int, int],
        icon: bytes | None,
        buttons: tuple[str, ...] = (BBOX_OK, BBOX_CANCEL),
        main: bool = False,
    ):
        self._main = main
        if main:
            self._dialog = tk.Tk()
        else:
            self._dialog = tk.Toplevel()
        self._icon = None
        if icon is not None:
            self._icon = get_appicon(icon)
            self._dialog.iconphoto(main, self._icon)  # type: ignore

        # position the form at the center of the screen
        sw = self._dialog.winfo_screenwidth()
        sh = self._dialog.winfo_screenheight()
        geometry = "%sx%s+%s+%s" % (
            size[0],
            size[1],
            int(sw / 2 - size[0] / 2),
            int(sh / 2 - size[1] / 2),
        )
        self._root = get_tkroot()
        self._dialog.title(title)
        self._dialog.geometry(geometry)
        self._dialog.resizable(False, False)
        self._area = ttk.Frame(self._dialog, padding=DIALOG_PADDING_MAIN)
        self._area.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.S, tk.E))  # type: ignore
        self._contents = ttk.Frame(self._area, padding=DIALOG_PADDING_INNER)
        self._contents.grid(row=0, sticky=(tk.N, tk.W, tk.S, tk.E))  # type: ignore
        self._contents.columnconfigure(0, weight=1)
        self._contents.rowconfigure(0, weight=1)
        sep = ttk.Separator(self._area)
        sep.grid(row=1, sticky=(tk.N, tk.W, tk.S, tk.E))  # type: ignore
        sep.rowconfigure(0, weight=1)
        bbox = ttk.Frame(self._area, padding=DIALOG_PADDING_INNER)
        pos = 0
        fill_idx = 0
        self._std_buttons = {}
        form_buttons = list(buttons)
        if "*" not in form_buttons:
            form_buttons.insert(0, "*")
        for btn_name in form_buttons:
            btn = None
            match btn_name:
                case "*":
                    fill_idx = pos
                    pos += 1
                case "ok":
                    btn = BtnOK(bbox, command=self.exit_ok)
                case "cancel":
                    btn = BtnCancel(bbox, command=self.exit_cancel)
                case "add":
                    btn = BtnAdd(bbox, command=self.add)
                case "remove":
                    btn = BtnRemove(bbox, command=self.remove)
                case "delete":
                    btn = BtnDelete(bbox, command=self.delete)
                case "edit":
                    btn = BtnEdit(bbox, command=self.edit)
                case "modify":
                    btn = BtnEdit(bbox, command=self.edit)
                case "load":
                    btn = BtnLoad(bbox, command=self.load)
                case "reset":
                    btn = BtnReset(bbox, command=self.reset)
                case "reload":
                    btn = BtnReload(bbox, command=self.reload)
                case "save":
                    btn = BtnSave(bbox, command=self.save)
                case "new":
                    btn = BtnNew(bbox, command=self.new)
                case "close":
                    btn = BtnClose(bbox, command=self.exit_close)
                case "exit":
                    btn = BtnExit(bbox, command=self.exit_close)
                case "quit":
                    btn = BtnClose(bbox, command=self.exit_close, text=BTN_QUIT)
            if btn is not None:
                btn.grid(row=0, column=pos, padx=DIALOG_PADDING_INNER[0])
                self._std_buttons[btn_name] = btn
                pos += 1
        fill = ttk.Frame(bbox)
        fill.grid(row=0, column=fill_idx, sticky=(tk.W, tk.E))  # type: ignore
        bbox.grid(row=2, sticky=(tk.N, tk.W, tk.S, tk.E))  # type: ignore
        bbox.columnconfigure(fill_idx, weight=1)
        bbox.rowconfigure(0, weight=1)
        self._area.rowconfigure(0, weight=1)
        self._area.columnconfigure(0, weight=1)
        self._dialog.columnconfigure(0, weight=1)
        self._dialog.rowconfigure(0, weight=1)
        self._widgets = {}
        self._data = {}
        self._checks = {}
        self._autocheck = True
        self._messagebox = MessageBox(self._dialog)

        # bind common shortcut keys
        self._dialog.bind("<FocusIn>", lambda _: self.focus_in())

    # support the context manager protocol
    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback) -> None:
        del self._dialog

    # contents is the root for slave widgets
    @property
    def contents(self) -> ttk.Frame:
        return self._contents

    # form to use as parent when needed
    @property
    def dialog(self) -> tk.Tk | tk.Toplevel:
        return self._dialog

    @property
    def messagebox(self) -> MessageBox:
        return self._messagebox

    # internals
    # force a variable value (and mimic ttk *Var retrieval method used below)
    def _force_set_data(self, name: str, value: Any) -> None:
        class _Elem(object):
            def __init__(self, v):
                self._v = v

            def get(self):
                return self._v

        data = _Elem(value)
        self._data[name] = data

    # bind a ttk.Treeview to a variable: it involves defining a new
    # function and reacting to a (virtual) event
    def _bind_ttk_treeview(self, name: str, treeview: ttk.Treeview) -> None:
        def _store_data(event):
            iid = treeview.focus()
            data = treeview.item(iid)["values"]
            self._force_set_data(name, data)

        self._force_set_data(name, None)
        treeview.bind("<<TreeviewSelect>>", _store_data)

    # bind an event to this form
    def event_bind(self, event, reaction) -> None:
        self._dialog.bind(event, reaction)

    # bind <Return> and <Escape> when gaining focus and unbind when n is lost
    def _key_exit_close(self, event) -> None:
        if event.widget == self._dialog:
            self.exit_close()

    def _key_exit_ok(self, event) -> None:
        if event.widget == self._dialog:
            self.exit_ok()

    def focus_in(self) -> None:
        self.event_bind("<Escape>", self._key_exit_close)
        self.event_bind("<Return>", self._key_exit_ok)

    # bind widgets to data: the parameters are the following
    # - name: the name under which the data is bound to a value
    # - widget: the widget that holds the data value, or a tuple of radio
    #           buttons to be bound to a single variable
    # - dtype: type of data in the widget: 'bool', 'int', 'float', 'str',
    #          or None for some widget types
    # - check: a function that returns True if data is valid, False otherwise
    #
    # Ok, the following is quite complicated - maybe overly complicated at
    # first sight. But I actually prefer to make this one somehow convoluted
    # in order to let the consumers be more streamlined.
    def data_bind(
        self,
        name: str,
        widget: tk.Widget | tuple[ttk.Radiobutton, ...],
        dtype: str | None = None,
        check: Callable[..., bool] | None = None,
    ) -> None:
        # as per documentation, the configure() method is not the preferred
        # method to configure a widget in tkinter, and direct access to the
        # widget keys (as if it were a dict) is used in the examples
        # see: https://docs.python.org/3/library/tkinter.html#setting-options
        if isinstance(widget, tk.Widget):
            opts = widget.keys()
        else:
            opts = []
        # store a reference to the widget
        self._widgets[name] = widget
        # special and non-bindable widget cases are treated one by one
        # TODO: hunt for possible special cases such as bool only widgets
        if isinstance(widget, ttk.Treeview):
            if dtype is not None:
                raise ValueError("cannot specify type for Treeview")
            self._bind_ttk_treeview(name, widget)
        # one-type widgets
        elif isinstance(widget, (tk.Checkbutton, ttk.Checkbutton)):
            if dtype is not None and dtype != "bool":
                raise ValueError("Checkbutton only provides boolean values")
            var = tk.BooleanVar()
            widget["variable"] = var
            self._data[name] = var
        # spin buttons?
        # scales?
        # special case: radio buttons (to be passed in groups)
        elif isinstance(widget, tuple):
            match dtype:
                case "str":
                    var = tk.StringVar()
                case "int":
                    var = tk.IntVar()
                case "float":
                    var = tk.DoubleVar()
                case None:
                    raise ValueError("type must be specified")
                case _:
                    raise ValueError("unsupported type: %s" % dtype)
            for w in widget:
                if not isinstance(w, (tk.Radiobutton, ttk.Radiobutton)):
                    raise TypeError("Only Radiobuttons are passed in groups")
                w.configure(variable=var)
                # w['variable'] = var
            self._data[name] = var
        # the following is a hack: we create the variable and handle it in a
        # specific way just when setting or getting, leaving it unbound
        elif isinstance(widget, tk.Text):
            if dtype is not None and dtype != "str":
                raise ValueError("Text only provides string values")
            var = tk.StringVar()
            self._data[name] = var
        # only strings and numbers for text elements (TODO: verify)
        elif "textvariable" in opts:
            match dtype:
                case "str":
                    var = tk.StringVar()
                case "int":
                    var = tk.IntVar()
                case "float":
                    var = tk.DoubleVar()
                case None:
                    raise ValueError("type must be specified")
                case _:
                    raise ValueError("unsupported type: %s" % dtype)
            widget["textvariable"] = var
            self._data[name] = var
        # for bindable non-text widgets strings are not supported
        elif "variable" in opts:
            match dtype:
                case "bool":
                    var = tk.BooleanVar()
                case "int":
                    var = tk.IntVar()
                case "float":
                    var = tk.DoubleVar()
                # case 'str':
                #     var = tk.StringVar()
                case None:
                    raise ValueError("type must be specified")
                case _:
                    raise ValueError("unsupported type: %s" % dtype)
            widget["variable"] = var
            self._data[name] = var
        else:
            pass
        # if validation is allowed use the provided validator (if any)
        if (
            check is not None
            and "validatecommand" in opts
            and isinstance(widget, tk.Widget)
        ):
            widget["validatecommand"] = check
        # final check is always set, possibly to an always pass test
        self._checks[name] = check or (lambda _: True)

    # retrieve a data item
    def data_get(self, dataname: str, default: Any | None = None):
        if dataname in self._data:
            widget = self._widgets[dataname]
            if isinstance(widget, tk.Text):
                s = widget.get(1.0, tk.END)
                self._data[dataname].set(s)
            try:
                rv = self._data[dataname].get()
                if self._checks[dataname](rv):
                    return rv
                else:
                    return None
            except Exception as _:
                return None
        else:
            return default

    # set the value of a widget: None is used to clear the widget
    def data_set(self, dataname: str, value: Any | None = None) -> None:
        if dataname in self._data:
            try:
                if value is None:
                    self._data[dataname].set("")
                elif self._checks[dataname](value):
                    self._data[dataname].set(value)
                else:
                    raise ValueError(
                        "invalid value %s for entry `%s`" % (repr(value), dataname)
                    )
                widget = self._widgets[dataname]
                if isinstance(widget, tk.Text):
                    widget.delete(1.0, tk.END)
                    widget.insert(tk.END, "" if value is None else value)
            except (TypeError, ValueError):
                if self._autocheck:
                    raise ValueError(
                        "invalid value %s for entry `%s`" % (repr(value), dataname)
                    )
        else:
            raise IndexError("entry `%s` not found" % dataname)

    # verify that a data item exists and that it passes the provided checks
    def data_exists(self, dataname: str) -> bool:
        return dataname in self._data

    def data_valid(self, dataname: str) -> bool:
        if dataname in self._data:
            try:
                rv = self._data[dataname].get()
                return bool(self._checks[dataname](rv))
            except (ValueError, TypeError, tk.TclError):
                return False
        else:
            return False

    # set autocheck feature on or off
    def set_autocheck(self, c: bool) -> None:
        self._autocheck = bool(c)

    # return a list of the widget-bound variables
    @property
    def data_vars(self):
        return list(self._data.keys())

    # exit functions are predefined and may be overridden or not: the
    # default implementation destroys the window and: if OK leave form
    # data accessible, otherwise clear form data
    def exit_ok(self) -> None:
        self._dialog.destroy()

    def exit_cancel(self) -> None:
        self._data = {}
        self._dialog.destroy()

    def exit_close(self) -> None:
        self._dialog.destroy()

    def exit_quit(self) -> None:
        self._dialog.destroy()

    # other button reactions have to be overridden because the default
    # implementation just does nothing
    def load(self) -> None:
        pass

    def save(self) -> None:
        pass

    def new(self) -> None:
        pass

    def add(self) -> None:
        pass

    def delete(self) -> None:
        pass

    def edit(self) -> None:
        pass

    def modify(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def reload(self) -> None:
        pass

    def remove(self) -> None:
        pass

    # the following utilities allow to enable or disable the default buttons
    def enable_buttons(self, *names: str) -> None:
        for name in map(str.lower, names):
            if name in self._std_buttons:
                self._std_buttons[name].enable(True)

    def disable_buttons(self, *names: str) -> None:
        for name in map(str.lower, names):
            if name in self._std_buttons:
                self._std_buttons[name].enable(False)

    # main dialog loop: the initial dialog will actually have a main loop
    # while the following ones will just be spawned and then waited for
    def run(self) -> None:
        if self._main:
            self._dialog.mainloop()
        else:
            self._dialog.wait_window()


# only export interesting stuff
__all__ = [
    "ApplicationForm",
    "MessageBox",
    "BBOX_OK",
    "BBOX_CANCEL",
    "BBOX_ADD",
    "BBOX_REMOVE",
    "BBOX_DELETE",
    "BBOX_EDIT",
    "BBOX_MODIFY",
    "BBOX_LOAD",
    "BBOX_SAVE",
    "BBOX_NEW",
    "BBOX_CLOSE",
    "BBOX_EXIT",
    "BBOX_QUIT",
    "BBOX_RESET",
    "BBOX_RELOAD",
    "BBOX_SEPARATOR",
    "DIALOG_PADDING_MAIN",
    "DIALOG_PADDING_INNER",
    "WIDGET_PADDING_PIXELS",
    "BUTTON_STANDARD_WIDTH",
    "BUTTON_STANDARD_WIDTH_SMALL",
    "TYPE_BOOL",
    "TYPE_INT",
    "TYPE_FLOAT",
    "TYPE_STRING",
    "BtnOK",
    "BtnCancel",
    "BtnClose",
    "BtnExit",
    "BtnAdd",
    "BtnRemove",
    "BtnDelete",
    "BtnLoad",
    "BtnSave",
    "BtnNew",
    "BtnEdit",
    "BtnModify",
    "BtnReset",
    "BtnReload",
]


# end.
