# When

This document describes the new version of **When**, a Python-based automation tool for the desktop. This version, instead of incorporating the scheduler, relies on the [**whenever**](https://github.com/almostearthling/whenever) automation tool, which focuses on reliability and lightweightness, while trying to achieve a good performance even when running at low priority. In this sense, **When** acts as a _wrapper_ for **whenever**, both providing a simple interface for configuration and an easy way to control the scheduler via an icon sitting in the tray area of your desktop. This version of **When** aims at being cross-platform, dynamically providing access to the features of **whenever** that are supported on the host environment.

This is still in its early development stage and still contains a lot of bugs and errors, yet it is capable of running **whenever** in the background and to control it via an icon in the system tray, create and edit a simple configuration file, capture the log and display a history window. All of this trying to mimic the behaviour of the old, _Ubuntu 16-to-18_ based **When** tool, which is entirely Python based and is now not actively developed anymore because of the difficulty of adapting all needed DBus signals and checks to the ever-changing interface of the various Linux distributions.

![MainWindow](support/docs/graphics/when-config-main.png)

Most of the interface of this release of **When** tries to be similar to the old version, although the need for cross-platform components pushes towards the adoption of the most diffused GUI library for Python, that is [tkinter](https://docs.python.org/3/library/tkinter.html).

![EditCmdCond](support/docs/graphics/when-config-cmdcond.png)

The documenttion is still underway, and the features are reduced compared to the old version of **When**. However the design of this new version is modular, and the design of **whenever** allows for the maximum flexibility in term of definitions of tasks, conditions, and events, so that new types of _usable_ events can be defined along with the forms to edit them easily and write a well-formed configuration file.

For the moment this version of **When** is not much more than a proof-of-concept. Still, the application may show a lot of problems due to lack of exception handling, absence of checks on correctness of values entered via the UI or interdependency of items (that is, tasks referenced in conditions and conditions referenced in events). The UI itself is far from being really usable: reactions to common gestures such as double clicks are not respected and sometimes inconsistently handled, and some usual graphic elements (pop-up boxes, buttons, and so on) are still incomplete and not consistent with the rest of the application. Graphic widgets, which are sometimes helpful within the forms, are for now either primitive or absent.


## Usage

This version of **When** uses [poetry](https://python-poetry.org/): after running `poetry install` in the project directory to install all necessary Python dependencies, **When** can be launched as follows:

```shell
when COMMAND [OPTIONS]
```

where `COMMAND` is one of the following:

- `config` to launch the configuration utility, without staying resident (i.e. no system tray icon)
- `start` to launch the resident **whenever** wrapper displaying the control icon on the system tray area
- `version` to display version information.

More commands might be supported in the future. `OPTIONS` are the possible options, some of which are command specific.

- `-D`/`--dir-appdata` _PATH_: specify the application data and configuration directory (default: _%APPDATA%\Whenever_ on Windows, _~/.whenever_ on Linux)
- `-W`/`--whenever` _PATH_: specify the path to the whenever executable (defaults to the one found in the PATH if any, otherwise exit with error)
- `-L`/`--log-level` _LEVEL_: specify the log level, all **whenever** levels are supported (default: _info_, specific to `start`)
- `-h`/`--help`: print help for the specific command

**NOTE**: For now **When** runs in _debug mode_, this means that it will sport a green-ish window style, will not catch exceptions, and will use a _DEBUG_ suffix for the application data directory. This behaviour can be modified by setting `'DEBUG': False` in the instantiation of `AppConfig` in _lib/repocfg.py_, instead of the current `True` value. This is useful when testing the application when an existing instance of **whenever** is running in production mode, possibly using the **whenever_tray** utility that normally shares the application dataa directory with **When** (starting with release 0.1.6). Note that a debug version of **whenever** should be used when a release version is running, because a debug version will not refuse to start sensing that the scheduler is already running. The full ppath to the desired **whenever** executable can be provided on the command line using the `-W` option.

**When** will only work if a working version of **whenever** is available, either in the system _PATH_ or specified via the command line interface by using the `-W` switch.


## Roadmap

The first goal is to obtain a fully functional version of this **When** edition, although supporting a minimal set of configuration items -- the ones that were supported at the time of the first launch of the old application. In this first stage of development, the effort will be devoted to amend bugs, enforce checks, handle possible exceptions that might occur in secondary threads and which may cause the application to become unstable, and overall to make the application consistent in terms of both the user interface and the handling of the **whenever** subprocess, _without_ adding new features. Once the minimal **When** application has reached an almost stable condition, new features (such as specific items and the _tool box_ mentioned below) will be added.

All in all, expectations and fulfillments for this version of **When** follow:

### Editors

Editor forms for the items supported by **whenever**: should behave in a way similar to how the original _When_ used to handle these items. Moreover, a main form is provided to access global configuration parameters and to create new items and edit or delete existing ones. Caveats: items that are referenced in other configuration items (eg. tasks in conditions, conditions in events) should not be deleteable.

- [x] Main Form (_to be completed_)
- [x] Task: Command
- [x] Task: Lua Script
- [x] Condition: Interval
- [x] Condition: Idle Session
- [x] Condition: Time
- [x] Condition: Command
- [x] Condition: Lua Script
- [x] Condition: Event (aka Bucket)
- [x] Event: Filesystem Monitoring
- [x] Event: Command Line (direct command sent to _stdin_, implemented for now, however this should be used for events handled by the wrapper itself, thus not directly accessed by the user)

Specific command/Lua based tasks, command/Lua/DBus based conditions, DBus based events should be supported to mimic the old **When** behaviour:

- [ ] Task: Shut down the system
- [ ] Task: Lock the system
- [ ] Condition: Startup and Shutdown
- [ ] Condition: Suspend and Resume
- [ ] Condition: Session Lock and Unlock
- [ ] Condition: Screensaver
- [ ] Condition: Storage Device Connect and Disconnect
- [ ] Condition: Join or Leave a Network
- [ ] Condition: Battery is Charging, Discharging or Low

### Other forms

The following forms, not related to the configuration application, are or should be only available from menus on the system tray:

- [x] History Box
- [ ] Tool Box: configure/unconfigure startup link (also for **whenever_tray**), config file conversion tool (old **When** --> new **When**)

### UI wrapper for the **whenever** scheduler

The following action should be supported by a resident part of the application that only shows an icon in the tray area, and allows to select entries from a popup menu.

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

This program uses a fork of [PySimpleGUI](https://www.pysimplegui.com/), namely [FreeSimpleGUI](https://github.com/spyoungtech/FreeSimpleGUI) which is on PyPI. The latest version of _PySimpleGUI_ is not open source anymore, and I'm fine with it: it is a useful package and deserves all possible support. However, **When** is an OSS project, and for the moment being I prefer to rely on libraries that do not require the end user to accept non-OSS license terms or to install third party license keys.
