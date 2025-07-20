# create_shortcuts.py
#
# create desktop or autostart shortcuts: uses either a .ico or a .png icon
# depending on the platform; in order to simplify the shortcut creation
# the icon is kept in the source as a base64 string, and created in the
# APPDATA directory as a graphic file


import sys
import os
import base64


from ..i18n.strings import *
from ..utility import write_error, write_warning, get_rich_console, get_appdata
from .create_shortcuts_icons import ICON_ICO, ICON_PNG
from ..repocfg import AppConfig


# template desktop files for Linux
TEMPLATE_XDG_WHEN = """\
#!/usr/bin/env xdg-open
[Desktop Entry]
Type=Application
Name={app_name}
Version={app_version}
Comment={app_description}
Exec={command_line}
Path={startup_path}
Icon=when-scheduler
Terminal=false
Categories=System
"""


# create the icon in the APPDATA directory
def create_icon(verbose=False) -> None | str:
    if sys.platform.startswith("win"):
        icon_filename = "When.ico"
        icon = ICON_ICO
    else:
        icon_filename = "when.png"
        icon = ICON_PNG
    target_dir = get_appdata()
    if target_dir is None:
        if verbose:
            write_error(CLI_ERR_DATADIR_UNACCESSIBLE)
        return None
    target = os.path.join(target_dir, icon_filename)
    if not os.path.exists(target):
        try:
            with open(target, "wb") as f:
                f.write(base64.b64decode(icon))
        except Exception as e:
            if verbose:
                write_error(CLI_ERR_CANNOT_CREATE_FILE % icon_filename)
            return None
    return target


# shortcut creation for Windows
if sys.platform.startswith("win"):
    import winshell

    def mk_shortcuts(
        target,
        arg_string,
        icon,
        name,
        description=None,
        desktop=True,
        appmenu=True,
        startup=True,
    ):
        locations = []
        if description is None:
            description = name
        if target.endswith(".py") or target.endswith(".pyw"):
            arg_string = '"%s" %s' % (target, arg_string)
            target = os.path.join(sys.exec_prefix, "pythonw.exe")
        if desktop:
            locations.append(winshell.desktop())
        if appmenu:
            d = os.path.join(winshell.start_menu(), "Programs", UI_APP)
            if not os.path.isdir(d):
                os.makedirs(d)
            locations.append(d)
        if startup:
            locations.append(winshell.startup())
        for p in locations:
            linkfile = os.path.join(p, "%s.lnk" % name)
            s = winshell.Shortcut(
                linkfile,
                path=target,
                arguments=arg_string,
                icon_location=(icon, 0),
                description=description,
                show_cmd="min",
                working_directory=os.path.expanduser("~"),
            )
            s.write()


# shortcut creation for Linux
elif sys.platform == "linux":

    def mk_shortcuts(
        target,
        arg_string,
        icon,
        name,
        description=None,
        desktop=True,
        appmenu=True,
        startup=True,
    ):
        if description is None:
            description = name
        if target.endswith(".py"):
            arg_string = f'"{target}" {arg_string}'
            target = sys.executable
        homedir = os.path.expanduser("~")
        # prepare the directories if they do not exist yet
        icondir = os.path.join(homedir, ".local", "share", "icons")
        appsdir = os.path.join(homedir, ".local", "share", "applications")
        autostartdir = os.path.join(homedir, ".config", "autostart")
        desktopdir = os.path.join(homedir, "Desktop")
        for d in [icondir, appsdir, autostartdir, desktopdir]:
            if not os.path.isdir(d):
                os.makedirs(d)
        # create a symlink to the icon in icondir
        icon_path = os.path.join(icondir, "when-scheduler.png")
        if not os.path.exists(icon_path):
            os.symlink(icon, icon_path)
        # prepare variables for .format()
        text = TEMPLATE_XDG_WHEN.format(
            app_name=name,
            app_description=description,
            app_version=UI_APP_VERSION,
            command_line=f"{target} {arg_string}",
            startup_path=homedir,
        )
        if appmenu:
            filename = f"{name}.desktop"
            destdir = appsdir
            with open(os.path.join(destdir, filename), "w") as f:
                f.write(text)
        if desktop:
            filename = f"{name}.desktop"
            destdir = desktopdir
            with open(os.path.join(destdir, filename), "w") as f:
                f.write(text)
        if startup:
            s = name.replace(" ", "_")
            filename = f"{s}-autostart.desktop"
            destdir = autostartdir
            with open(os.path.join(destdir, filename), "w") as f:
                f.write(text)


# no other platforms supported at the moment


# use the utilities defined above to create the requested shortcuts
def create_shortcuts(main_script, desktop=True, autostart=True, verbose=False):
    console = get_rich_console()
    if verbose:
        console.print(CLI_MSG_CREATING_ICON, highlight=False)
    icon_filename = create_icon(verbose)
    if icon_filename is None:
        if verbose:
            write_error(CLI_ERR_CANNOT_CREATE_ICON)
        return False
    # create menu shortcuts for configuration utility and scheduler start
    # first: check whether a `pipx`-style install is available
    if sys.platform.startswith("win"):
        exename = "when-bg.exe"
        interpreter = os.path.join(sys.exec_prefix, "pythonw.exe")
    else:
        exename = "when"
        interpreter = sys.executable
    p = os.path.expanduser(os.path.join("~", ".local", "bin"))
    target = os.path.join(p, exename)
    if not (os.path.isfile(target) and os.access(target, os.X_OK)):
        target = main_script
    args_start = 'start --whenever="%s"' % AppConfig.get("WHENEVER")
    args_config = "config"
    if verbose:
        console.print(CLI_MSG_CREATING_SHORTCUT, highlight=False)
    try:
        # configuration app shortcuts (desktop/appmenu only)
        mk_shortcuts(
            target,
            args_config,
            icon_filename,
            CLI_APPICON_NAME_CONFIG,
            CLI_APPICON_DESC_CONFIG,
            desktop,
            True,
            False,
        )
        # resident app shortcuts (desktop/appmenu/startup)
        mk_shortcuts(
            target,
            args_start,
            icon_filename,
            CLI_APPICON_NAME_START,
            CLI_APPICON_DESC_START,
            desktop,
            True,
            autostart,
        )
    except Exception as e:
        if verbose:
            print(e)
            write_warning(CLI_ERR_CANNOT_CREATE_SHORTCUT)


# end.
