# When

This document describes the new version of **When**, a Python-based automation tool for the desktop. This version, instead of incorporating the scheduler, relies on the [**whenever**](https://github.com/almostearthling/whenever) automation tool, which focuses on reliability and lightweightness, while trying to achieve a good performance even when running at low priority. In this sense, **When** acts as a _wrapper_ for **whenever**, both providing a simple interface for configuration and an easy way to control the scheduler via an icon sitting in the tray area of your desktop. This version of **When** aims at being cross-platform, dynamically providing access to the features of **whenever** that are supported on the host environment.

This is still in its early development stage and still contains a lot of bugs and errors, yet it is capable of running **whenever** in the background and to control it via an icon in the system tray, create and edit the configuration file, capture the log and display a history window. All of this trying to mimic the behaviour of the old **When** tool, only available on Ubuntu distributions and restricted to the 16.XX and 18.XX editions, which is entirely Python based and is now abandoned because of the difficulty of adapting all needed DBus signals and checks to the ever-changing interface of the various Linux distributions.

![MainWindow](support/docs/graphics/when-application.png)

Most of the interface of this release of **When** tries to be similar to the old version, although the need for cross-platform components pushes towards the adoption of the most widespread GUI library for Python, that is [_tkinter_](https://docs.python.org/3/library/tkinter.html). Also, some of the extra features that are built into **whenever** call for a somewhat less-streamlined interface especially in terms of form layout.

The [documentation](support/docs/main.md) is still underway, and the features are reduced compared to recent releases of the old version of **When**. However the structure of this new version is modular, and the design of **whenever** allows for the maximum flexibility in term of definitions of tasks, conditions, and events, so that new types of _usable_ events can be defined along with the forms to edit them easily and write a well-formed configuration file.

For the moment this version of **When** is mostly intended as a proof-of-concept, even though it has reached a status in which all the basic features are implemented. The application may show problems due to lack of targeted exception handling, and genericity of checks on correctness of values provided via the UI. The UI itself still might have some quirks: the semantic of common gestures such as double clicks is not always respected, and some usual interface elements (pop-up boxes, buttons, and so on) might still result incomplete and not entirely consistent.


## Usage

This version of **When** uses [poetry](https://python-poetry.org/): after running `poetry install` in the project directory to install all necessary Python dependencies, **When** can be launched as follows:

```shell
poetry run when COMMAND [OPTIONS]
```

where `COMMAND` is one of the following:

- `config` to launch the configuration utility, without staying resident (i.e. no system tray icon)
- `start` to launch the resident **whenever** wrapper displaying the control icon on the system tray area (non working on Linux: see [#113](https://github.com/almostearthling/when-command/issues/113))
- `version` to display version information.

More commands might be supported in the future. `OPTIONS` are the possible options, some of which are command specific.

- `-D`/`--dir-appdata` _PATH_: specify the application data and configuration directory (default: _%APPDATA%\Whenever_ on Windows, _~/.whenever_ on Linux)
- `-W`/`--whenever` _PATH_: specify the path to the whenever executable (defaults to the one found in the PATH if any, otherwise exit with error)
- `-L`/`--log-level` _LEVEL_: specify the log level, all **whenever** levels are supported (default: _info_, specific to `start`)
- `-h`/`--help`: print help for the specific command

For the moment, due to the lack of access to some of the Python modules necessary for [pystray](https://github.com/moses-palmer/pystray) to work correctly, running the resident **whenever** wrapper is not possible on Linux. However `poetry run when config` can be used to create and edit a **whenever** configuration file, and **whenever_tray** is available as a consistent wrapper.

**NOTE**: **When** can be run in _debug mode_, that is, it will not catch exceptions, and will use a _DEBUG_ suffix for the application data directory: it also displays a color scheme that is neither dark nor light to underline its particular state. This behaviour can be enabled by setting `'DEBUG': True` in the instantiation of `AppConfig` in _lib/repocfg.py_, instead of the current `True` value. This is useful when testing the application when an existing instance of **whenever** is running in production mode, possibly using the **whenever_tray** utility that normally shares the application data directory with **When** (starting with release 0.1.6). Note that a debug version of **whenever** should be used when a release version is running, because a debug version will not complain and refuse to start in case a non-debug version of the scheduler is already running. The full path to the desired **whenever** executable can be provided on the command line using the `-W` option.

**When** will be able to act as a wrapper only if a working and recent (not below [0.1.23](https://github.com/almostearthling/whenever/releases/tag/v0.1.23%2Btray0.1.6)) version of **whenever** is available, either in the system _PATH_ or specified via the command line interface by using the `-W` switch.


## Roadmap

The first goal is to obtain a fully functional version of this **When** edition, although supporting a minimal set of configuration items -- the ones that were supported at the time of the first launch of the old application. In this first stage of development, the effort will be devoted to amend bugs, enforce checks, handle possible exceptions that might occur in secondary threads and which may cause the application to become unstable, and more in general to make the application consistent in terms of both the user interface and the handling of the **whenever** subprocess, _without_ adding new features. Once the minimal **When** application has reached an almost stable condition, new features (such as specific items and the _tool box_ mentioned below) will be added.

Expectations and fulfillments for this version of **When** follow:

### Editors

Editor forms for the items supported by **whenever**: should behave in a way similar to how the original _When_ used to handle these items. Moreover, a main form is provided to access global configuration parameters and to create new items and edit or delete existing ones.

- [x] Main Form
- [x] Task: Command
- [x] Task: _Lua_ Script
- [x] Condition: Interval
- [x] Condition: Idle Session
- [x] Condition: Time
- [x] Condition: Command
- [x] Condition: _Lua_ Script
- [x] Condition: Event (aka Bucket)
- [ ] ~~Condition: DBus Method call~~ (was not available in the original edition: form implemented but not made available)
- [x] Event: Filesystem Monitoring
- [ ] ~~Event: Command Line~~ (not useful from a user POV: form implemented but not made available)
- [ ] ~~Event: DBus Signal~~ (was barely usable and restricted in the original edition: form implemented but not made available)

Specific command/_Lua_ based tasks, command/_Lua_/DBus based conditions, DBus based events should be supported to mimic the old **When** behaviour:

- [ ] Task: Shut down the system
- [ ] Task: Lock the system
- [ ] Condition: Startup and Shutdown
- [ ] Condition: Suspend and Resume
- [ ] Condition: Session Lock and Unlock
- [ ] Condition: Screensaver
- [ ] Condition: Storage Device Connect and Disconnect
- [ ] Condition: Join or Leave a Network
- [ ] Condition: Battery is Charging, Discharging or Low
- [x] Condition: System Load is Below a Certain Treshold

### Other forms

The following forms, not related to the configuration application, are or should be only available from menus on the system tray:

- [x] History Box
- [ ] Tool Box: configure/unconfigure startup link (also for **whenever_tray**), config file conversion tool (old **When** --> new **When**)

### UI wrapper for the **whenever** scheduler

The following actions should be supported by a resident part of the application that only shows an icon in the tray area, and allows to choose entries from a popup menu.

- [x] Show an About Box (to be improved)
- [x] Show the task history, including execution time and outcome
- [ ] Suspend and resume conditions
- [x] Reset conditions
- [x] Pause and resume the scheduler
- [ ] Restart the scheduler
- [x] Load the configuration utility (to be improved)

Other features that might be useful:

- [ ] Preserve paused state
- [ ] Log rotation and max number of old logs
- [ ] Reset conditions on wakeups from suspension or hibernation

The resident part of the application should **not** load the configuration utility at startup: it should only be loaded when the appropriate menu entry is selected, and all the modules should be removed from memory after the configuration utility has been left by the user.


## Compatibility

**When** has been successfully tested on Windows (10 and 11) and Linux (Debian 12). On Debian 12, however, it does not run OOTB: some additional packages are needed, as it does not ship with _tkinter_ support by default, nor it supports the _AppIndicator_ protocol in a Gnome session. Thus both `python3-tk` and `gir1.2-ayatanaappindicator3` need to be installed using the _apt_ package manager. Moreover, on _Wayland_ sessions the UI appears mangled and the graphic elements are actually unusable: it looks like _tkinter_ only works well in _Xorg_ sessions. Since Gnome does not support indicator icons direcltly, a Gnome shell extension capable of implementing this protocol has to be installed, such as [AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/).

Before starting **When** on Debian 12, and before the `poetry install` step described [above](#usage), the following option needs to be set in order to let the Python virtual environment access all the needed system modules:

```shell
poetry config virtualenvs.options.system-site-packages false
```

otherwise Python would not reach the modules needed to display the system tray icon and menu.

Research is underway on the possibility to provide **When** in "binary-ish" form too: there are some available tools that use the dependency management features in **poetry** to build packages suitable for various operating systems and their distributions.


## Credits

The clock [icon](http://www.graphicsfuel.com/2012/08/alarm-clock-icon-psd/) used for the application logo has been created by Rafi and is available at [GraphicsFuel](http://www.graphicsfuel.com/). All other icons have been found on [Icons8](https://icons8.com/):

* [Alarm Clock](https://icons8.com/icon/13026/alarm-clock)
* [Exclamation Mark](https://icons8.com/icon/j1rPetruM5Fl/exclamation-mark)
* [Question Mark](https://icons8.com/icon/cjUb4tRvBCNt/question-mark)
* [Settings Gear](https://icons8.com/icon/12784/settings)
* [OK (Check Mark) Button](https://icons8.com/icon/70yRC8npwT3d/check-mark)
* [Cancel Button](https://icons8.com/icon/fYgQxDaH069W/cancel)
* [Close Window](https://icons8.com/icon/rmf1Fvj5nBib/close-window)
* [Save](https://icons8.com/icon/yFBJCjFJpLXw/save)
* [Enter](https://icons8.com/icon/U5AcCk9kUWMk/enter)
* [Add](https://icons8.com/icon/IA4hgI5aWiHD/add)
* [Remove](https://icons8.com/icon/9lB4p3bBjCNX/remove)
* [Error](https://icons8.com/icon/hP6pCUyT8QGk/error)
* [New Document](https://icons8.com/icon/8tcDgihugAYf/new-document)
* [Pencil Drawing](https://icons8.com/icon/FnCPHMRRKpyL/pencil-drawing)
* [Delete](https://icons8.com/icon/pre7LivdxKxJ/delete)
* [File](https://icons8.com/icon/XWoSyGbnshH2/file)
* [Folder](https://icons8.com/icon/dINnkNb1FBl4/folder)

This utility uses the beautiful [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) theme extension for _tkinter_, which provides a modern look consistent on all supported platform (and which is probably more clean and clear than it used to be in the GTK days). Also, [chlorophyll](https://github.com/rdbende/chlorophyll) is used to display and edit code and structured text, providing a more pleasant and up to date UI, and [pystray](https://github.com/moses-palmer/pystray) to implement the system tray interface.
