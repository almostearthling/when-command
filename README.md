# When (*when-command*)

**When** is a configurable user task scheduler, designed to work in an X/Gnome session. It interacts with the user through a GUI, where the user can define tasks and conditions, as well as relationships of causality that bind conditions to tasks. When a condition is bound to a task, it is said to trigger a task.

![Screenshot](http://almostearthling.github.io/when-command/images/screenshot.png)

The purpose of this small utility is to provide the user, possibly without administrative credentials, the ability to define conditions that do not only depend on time, but also on a particular state of the session (e.g. the result of a command run in a shell). The same result could be achieved with scripts that periodically run commands, check the results and react accordingly, but such a simple task could result in complex sets of scripts and settings that would be harder to maintain. **When** was born out of need: I have been a (happy) Ubuntu user for years now, and couldn't think of having a different desktop environment than the one provided by Ubuntu. In *14.04 LTS* (the release I'm using now) the environment is consistent and pleasant. One thing I've noticed that has evolved in Windows is the *Task Scheduler*: in fact it looks more useful and usable than the usual *cron* daemon, at least because it allows some more options to schedule tasks than just the system time. I needed such an utility to perform some file synchronizations when the workstation is idle, and decided to write my own task scheduler targeted to Ubuntu. The scheduler runs in the background, and it displays an indicator applet icon for user interaction.

It is not generally intended as a replacement to [*cron*](https://en.wikipedia.org/wiki/Cron) and the [Gnome Task Scheduler](http://gnome-schedule.sourceforge.net/), although to some extent these utilities might overlap. **When** is intended to be more flexible, although less precise, and to provide an alternative to more complicated solutions -- such as the implementation of *cron* jobs that check for a particular condition and execute commands when the condition is verified. In such spirit, **When** is not as fine-grained in terms of doing things on a strict time schedule: the **When** approach is that "*when* a certain condition is met, *then* something has to be done". The condition is checked periodically, and the "countermeasure" is taken *subsequently* -- although not *immediately* in most cases. In fact, and with the default configuration, the delay can reach a couple of minutes in the worst case.


## Description

The applet will show up in the indicator tray at startup, which would normally occur at login if the user chose to add **When** to the startup applications, which is the default behavior when using the suggested installation procedure. It will read its configuration and start the scheduler in an unattended fashion. Whenever one of the user defined conditions is met, the associated tasks are executed. A small alarm clock :alarm_clock: icon will display in the indicator tray, to show that the applet is running: by default it turns to an attention sign :warning: when the applet requires attention. Also, the icon changes its shape when the applet is *paused* (the clock is crossed by a slash) and when a configuration dialog is open (the alarm clock shows a plus sign inside the circle).

The icon grants access to the main menu, which allows the following basic operations:

* open the *Task* editing dialog box
* open the *Condition* editing dialog box
* open the *Settings* dialog box
* show the *Task History* window
* *pause* and *resume* the scheduler
* show the *About* box
* quit the applet

Where the *Task* and *Condition* editing boxes, the *Settings* dialog and the *Task History* window might need some further explanation, the other operations should be pretty straightforward.


### Tasks

Tasks are basically commands associated with an environment and checks to determine whether the execution was successful or not. The interface lets the user configure some basic parameters (such as the startup directory and the *environment*) as well as what to test after execution (*exit code*, *stdout* or *stderr*). The user can choose to look for the specified text within the output and error streams (when *Exact Match* is unchecked, otherwise the entire output is matched against the given value) and to perform a case sensitive test, or to match a regular expression. In case a regular expression is chosen, the applet will try to search *stdout* or *stderr* for the given pattern. In case of regular expressions, when *Exact Match* is chosen, a match test is performed at the beginning of the output text. Regular expression tests can be case insensitive as well.

The environment in which the subprocess is run can either import the current one (at **When** startup time), use its own variables or both.

The selected task (if any) can be deleted clicking the *Delete* button in the dialog box. However the application will refuse to delete a task that is used in a condition: remove the task reference from the condition first. Every task must have an *unique name*, if a task is named as an existing task it will replace the existing one. The name *must* begin with an alphanumeric character (letter or digit) followed by alphanumerics, dashes and underscores.

**How to use the "Check for" option:** The applet can either ignore whatever the underlying process returns to the caller by specifying *Nothing* in the *Check for* group, or check

* exit code
* process output (*stdout*)
* process written errors (*stderr*)

to determine whether the process succeeded or failed. When the user chooses to check for *Success*, the operation is considered successful *if and only if* the process result (exit code, output, or error) corresponds to the user provided value. Same yields for *Failure*: if *Failure* is chosen, only the provided result will indicate a failure. For example, in the most common case the user will choose to expect *Success* to correspond to an *Exit Code* of `0` (in fact the default choice), all other exit codes will indicate a failure. And if the user chooses to expect *Failure* to be reported as the word `Error` in the error messages, whatever other error messages will be ignored and the operation will turn out successful. Please note that since all commands are executed in the default shell, expect an exit code different from `0` when the command is not found. With the `/bin/sh` shell used on Linux, the *not found* code is `127`.


### Conditions

There are several types of condition available:

1. **Interval based:** After a certain time interval the associated tasks are executed, if the condition is set to repeat checks, the tasks will be executed again regularly after the same time interval.
2. **Time based:** The tasks are executed when the time specification is matched. Time definitions can be partial, and in that case only the defined parts will be taken into account for checking: for instance, if the user only specifies minutes, the condition is verified at the specified minute for every hour if the *Repeat Checks* option is set.
3. **Command based:** When the execution of a specified command gives the expected result (in terms of **exit code**, **stdout** or **stderr**), the tasks are executed. The way the test command is specified is similar (although simpler) to the specification of a command in the *Task* definition dialog box. The command is run in the same environment (and startup directory) as **When** at the moment it was started.
4. **Idle time based:** When the session has been idle for the specified amount of time the tasks are executed. This actually is implemented as a shortcut to the command based condition built using the `xprintidle` command, which must be installed for the applet to work properly.
5. **Event based:** The tasks are executed when a certain session or system event occurs. The following events are supported:
  - *Startup* and *Shutdown*. These are verified when the applet (or session, if the applet is launched at startup) starts or quits.
  - *Suspend* and *Resume*, respectively match system suspension/hibernation and resume from a suspended state.
  - *Session Lock* and *Unlock*, that occur when the screen is locked or unlocked.
  - *Screensaver*, both entering the screen saver state and exiting from it.
  - *Storage Device Connect* and *Disconnect*, which take place when the user attaches or respectively detaches a removable storage device.
  - *Join* or *Leave a Network*, these are verified whenever a network is joined or lost respectively.
  - *Command Line Trigger* is a special event type, that is triggered invoking the command line. The associated condition can be scheduled to be run at the next clock tick or immediately using the appropriate switch.
6. **Based on filesystem changes:** The tasks are run when a certain file changes, or when the contents of a directory or its subdirectories change, depending on what the user chose to watch -- either a file or a directory. A dialog box can be opened to select what has to be watched. Please note that this is an optional feature, and could lack on some systems: to enable this feature the `pyinotify` library must be installed, please refer to the instructions below.
7. **Based on an user defined event:** The user can define system events by listening to signals emitted on the system bus and the session bus. This is an advanced feature, and the events must be defined using the procedure described below.

**Warning**: because of the way applications are notified that the session is ending (first a TERM signal is sent, then a KILL if the first was unsuccessful), the *Shutdown* event is not suitable for long running tasks, such as file synchronizations, disk cleanup and similar actions. The system usually concedes a "grace time" of about one second before shutting everything down. Longer running tasks will be run if the users quits the applet through the menu, though. Same yields for *Suspend*: by specification, no more than one second is available for tasks to complete.

Also, the condition configuration interface allows to decide:

* whether or not to repeat checks even after a task set has been executed -- that is, make an event *periodic*;
* to run the tasks in a task set concurrently or sequentially: when tasks are set to run sequentially, the user can choose to ignore the outcome of tasks or to break the sequence on the first failure or success, selecting the appropriate entry in the box on the right -- tasks that don't check for success or failure will *never* stop a sequence;
* to *suspend* the condition: it will not be tested, but it's kept in the system, inactive until the *Suspend* box is unchecked.

The selected condition (if any) can be deleted clicking the *Delete* button in the dialog box. Every condition must have an *unique name*, if a condition is named as an existing one it will replace it. The name *must* begin with an alphanumeric character (letter or digit) followed by alphanumerics, dashes and underscores.

**Possibly unsupported events:** some events may not be supported on every platform, even on different Ubuntu implementations. *Screen Lock/Unlock* for instance does not follow very precise specifications, and could be disabled on some desktops. Thus one or more events might appear as *[disabled]* in the list: the user still can choose to create a condition based on a disabled event, but the corresponding tasks will never be run.

*Note:* If a task is triggered by more than one condition almost at the same time, only the first instance of the task will be run. This behavior is intentional, to allow the user to decide to perform a task under more than one cirumstance, and to avoid task repetition in case all triggering circumstances actually occur.


### The history window

Since logs aren't always easy to deal with, **When** provides an easier interface to verify the task results. Tasks failures are also notified graphically via the attention-sign icon and badge notifications, however more precise information can be found in the *History* box. This shows a list of the most recently tasks that where launched by the current applet instance (the list length can be configured), which reports:

* The start time of the task and its duration in seconds
* The task *unique name*
* The *unique name* of the condition that triggered the task
* The process *exit code* (as captured by the shell)
* The result (green &#10004; for success, red &#10008; for failure)
* A short hint on the failure *reason* (only in case of failure)

and when the user clicks a line in the table, the tabbed box below will possibly show the output (*stdout*) and errors (*stderr*) reported by the underlying process. The contents of the list can also be exported to a text file, by invoking the applet with the `--export-history` switch from a console window when an instance is running. The file contains exactly the same values as the history list, with the addition of a row identifier at the beginning of the row. Start time and duration are separate values. The first row of the file consists of column mnemonic titles and the value separator is a semicolon: the file can be safely imported in spreadsheets, but column conversions could be needed depending on your locale settings.


### Settings

The program settings are available through the specific *Settings* dialog box, and can be manually set in the main configuration file, which can be found in `~/.config/when-command/when-command.conf`.

The options are:

1. **General**
  * *Show Icon*: whether or not to show the indicator icon and menu
  * *Autostart*: set up the applet to run automatically at login
  * *Notifications*: whether or not to show notifications upon task failure
  * *Icon Theme*: `Guess` to let the application decide, otherwise one of `Dark` (light icons for dark themes), `Light` (dark icons for light themes), and `Color` for colored icons that should be visible on all themes.
2. **Scheduler**
  * *Application Clock Tick Time*: represents the tick frequency of the application clock, sort of a heartbeat, each tick verifies whether or not a condition has to be checked; this option is called `tick seconds` in the configuration file
  * *Condition Check Skip Time*: conditions that require some "effort" (mainly the ones that depend on an external command) will skip this amount of seconds from previous check to perform an actual test, should be at least the same as *Application Clock Tick Time*; this is named `skip seconds` in the configuration file
  * *Preserve Pause Across Sessions*: if *true* (the default) the scheduler will remain paused upon applet restart if it was paused when the applet (or session) was closed. Please notice that the indicator icon gives feedback anyway about the paused/non-paused state. Use `preserve pause` in the configuration file.
3. **Advanced**
  * *Max Concurrent Tasks*: maximum number of tasks that can be run in a parallel run (`max threads` in the configuration file)
  * *Log Level*: the amount of detail in the log file
  * *Max Log Size*: max size (in bytes) for the log file
  * *Number Of Log Backups*: number of backup log files (older ones are erased)
  * *Instance History Items*: max number of tasks in the event list (*History* window); this option is named `max items` in the configuration file
  * *Enable User Defined Events*: if set, then the user can define events using DBus *(see below)*. Please note that if there are any user defined events already present, this option remains set and will not be modifiable. It corresponds to `user events` in the configuration file. Also, to make this option effective and to enable user defined events in the *Conditions* dialog box, the applet must be restarted
  * *Enable File and Directory Notifications*: if set, **When** is configured to enable conditions based on file and directory changes. The option may result disabled if the required optional libraries are not installed. When the setting changes, the corresponding events and conditions are enabled or disabled at next startup.
  * *Enable Task and Condition Environment Variables*: whether or not to export specific environment variables with task and condition names when spawning subprocesses (either in *Tasks* or in *Command Based Conditions*). The configuration entry is `environment vars`.

The configuration is *immediately stored upon confirmation* to the configuration file, although some settings (such as *Notifications*, *Icon Theme*, and most advanced settings) might require a restart of the applet. The configuration file can be edited with a standard text editor, and it follows some conventions common to most configuration files. The sections in the file might slightly differ from the tabs in the *Settings* dialog, but the entries are easily recognizable.

By default the applet creates a file with the following configuration, which should be suitable for most setups:

```
[Scheduler]
tick seconds = 15
skip seconds = 60
preserve pause = true

[General]
show icon = true
autostart = false
notifications = true
log level = warning
icon theme = guess
user events = false
file notifications = false
environment vars = true

[Concurrency]
max threads = 5

[History]
max items = 100
log size = 1048576
log backups = 4
```

Manual configuration is particularly useful to bring back the program icon once the user decided to hide it (losing access to the menu: I was doubtful about providing the option, then just decided to implement it and provide a safety net anyway), by setting the `show icon` entry to `true`. Another way to force access to the *Settings* dialog box when the icon is hidden is to invoke the applet from the command line using the `--show-settings` (or `-s`) switch when an instance is running.


### Command line options

By default, when the applet is invoked with no arguments, it just starts an instance showing the icon in the top panel (if configured to do so). However there are some command line options that allow for some operations, either on a running instance or on the current configuration. Some are especially useful to recover when something has gone the wrong way -- such as the `--show-settings` switch mentioned above, or the `-I` (or `--show-icon`) switch, to recover from an unwantedly hidden icon. The available options are:

* `-s` or `--show-settings`: show the settings dialog box of an existing instance, it requires a running instance, which may be queried using the `--query` switch explained below
* `-l` or `--show-history`: show the history dialog box of an existing instance
* `-t` or `--show-tasks`: show the task dialog box of an existing instance
* `-c` or `--show-conditions`: show the condition dialog box of an existing instance
* `-d` or `--show-signals`: show the DBus signal handler editor box for an existing instance (*advanced feature not available with the default configuration, see below*)
* `-R` or `--reset-config`: reset applet configuration to default, requires the applet to be shut down with an appropriate switch
* `-I` or `--show-icon`: show applet icon, the icon will be shown at the next startup
* `-T` or `--install`: install or reinstall application icon and autostart icon, requires applet to be shut down with an appropriate switch
* `-C` or `--clear`: clear current tasks, conditions and possibly signal handlers, requires applet to be shut down with an appropriate switch
* `-Q` or `--query`: query for an existing instance (returns a zero exit status if an instance is running, nonzero otherwise, and prints an human-readable message if the `--verbose` switch is also specified)
* `-H` *filename* or `--export-history` *filename*: export the current task history (the ones shown in the history box) to the file specified as argument in a CSV-like format
* `-r` *condition* or `--run-condition` *condition*: trigger a command-line associated condition and immediately run the associated tasks; *condition* must be specified and has to be one of the *Command Line Trigger* conditions, otherwise the command will fail and no task will be run
* `-f` *condition* or `--defer-condition` *condition*: schedule a command-line associated condition to run the associated tasks at the next clock tick; the same as above yields for *condition*
* `--shutdown`: close a running instance performing shutdown tasks first
* `--kill`: close a running instance abruptly, no shutdown tasks are run
* `--export` *[filename]*: save tasks, conditions and other items to a portable format, if *filename* is not specified these items are saved in a default file in the `~/.config/when-command` directory; this will especially be useful in cases where the compatibility of the "running" versions of tasks and conditions (which are a binary format) could be broken across releases
* `--import` *[filename]*: clear tasks, conditions and other items and import them from a previously saved file, if *filename* is not specified the applet tries to import these items from the default file in the `~/.config/when-command` directory; the applet has to be shut down before attempting to import items.

Some trivial switches are also available:

* `-h` or `--help`: show a brief help message and exit
* `-V` or `--version`: show applet version, if `--verbose` is specified it also shows the *About Box* of a running instance, if there is one
* `-v` or `--verbose`: show output for some options; normally the applet would not display any output to the terminal unless `-v` is specified, the only exception being `--version` that prints out the version string anyway.

Please note that whenever a command line option is given, the applet will not "stay resident" if there is no previously running instance. On the other side, if the user invokes the applet when already running, the new instance will bail out with an error.


## Installation and removal

### Requirements

For the applet to function and before unpacking it to the destination directory, make sure that *Python 3.x*,  *PyGObject* for *Python 3.x* and the `xprintidle` utility are installed. Optionally, to enable file and directory monitoring, the `pyinotify` package can be installed. For example, not all of these are installed by default on Ubuntu: in this case the following commands can be used.

```
$ sudo apt-get install python3-gi
$ sudo apt-get install xprintidle
$ sudo apt-get install gir1.2-appindicator3-0.1  # may be required
$ sudo apt-get install python3-pyinotify   # optional (but recommended)
```

After the requirements have been satisfied, there are several options for installation.

### Package based installation

Of course using a package is the quickest and easiest way to have a working installation of **When**. Packages are provided for Ubuntu, although they might work (at least partially) with other Debian based Linux distributions. **When** packages come in two flavors:

1. `when-command`: this is a LSB structured package, especially suitable for Ubuntu and derivatives, that installs the applet in a way similar to other standard Ubuntu packages. The actual file name has the form `when-command_VERSIONSPEC-N_all.deb` where `VERSIONSPEC` is a version specification, and `N` is a number. Pros of this package are mostly that it blends with the rest of the operating environment and that the `when-command` command-line utility is available on the system path by default. Cons are that this setup may conflict with environments that are very different from Ubuntu.
2. `when-command-opt`: this version installs **When** in `/opt/when-command`, and should be suitable for `.deb` based distributions that differ from Ubuntu. The advantage of this method is that the applet is installed separately from the rest of the operating environment and does not clutter the host system. The main drawback is that the `when-command` utility is not in the system path by default and, unless the `PATH` variable is modified, it has to be invoked using the full path, that is `/opt/when-command/when-command`. The package file name has the form `when-command-opt-VERSIONSPEC.deb`.

To install a downloaded package, the command `sudo dpkg --install when-command_VERSIONSPEC-N_all.deb` or `sudo dpkg --install when-command-opt-VERSIONSPEC.deb` for the latter case. After installation, each user who needs to run **When** has to launch `when-command --install` (or `/opt/when-command/when-command --install` if the second method was chosen) in order to find the applet icon in *Dash* and to be able to set it up as a startup application (via the *Settings* dialog box). The first method is the preferred one, and it is referred to throughout the documentation: `when-command` is expected to be in the path and in the examples and instructions is invoked directly, without prefixing the full path.

### Installation from a source archive or a repository clone

To install the package using the source archive in a directory of choice, the required steps are somewhat more difficult. However this can be done almost mechanically. For the example we will supposed that the source has been downloaded from GitHub (but it could have been cloned, and the steps would be similar) in the form of a `when-command-master.zip` archive located in `~/Downloads`, and that the user wants to install **When** in `~/Applications/When`. The required operations are the following:

```
$ cd ~/Applications
$ unzip ~/Downloads/when-command-master.zip
$ mv when-command-master When
$ cd When
$ rm -f when-command
$ rm -Rf po temp scripts .git* setup.* MANIFEST.in share/icons when-command
$ chmod a+x share/when-command/when-command.py
$ ln -s share/when-command/when-command.py when-command
$ $HOME/Applications/When/when-command --install
```

Please note that `rm -f when-command` is *strictly* needed in order to allow creation of the `when-command` symbolic link, whereas the second `rm` is only required to remove files that are not used by the installed applet and to avoid a cluttered setup. Also, with this setup, **When** can only be invoked from the command line using the full path (`$HOME/Applications/When/when-command` in the example): to use the `when-command` shortcut, `$HOME/Applications/When` has to be included in the `PATH` variable in `.bashrc`. This means for instance that a symbolic link in a directory already in the user path can cause malfunctions to **When** upon command line invocation.

This installation method is useful in several cases: it can be used for testing purposes (it can supersede an existing installation), to run the applet directly from a cloned repository or to restrict installation to a single user.

### The --install switch

**When** will try to recognize the way it has been set up the first time it's invoked: the `--install` switch creates the desktop entries and icons for each user that opts in to use the applet, as well as the required directories that **When** needs to run correctly and an active autostart entry, that is:

* `~/.config/when-command` where it will store all configuration
* `~/.local/share/when-command` where it stores resources and logs (in the `log` subdirectory).

Please note that the full path to the command has to be used on the first run if the `/opt` based package or the manual installation were chosen: in this way **When** can recognize the installation type and set up the icons and shortcuts properly.

### Uninstallation

**When** can be uninstalled via `apt-get remove when-command` or `apt-get remove when-command-opt` if a package distribution was used, or by removing the newly created applet directory (`~/Applications/When` in the above example) if the source was unpacked as explained above. Also, user data and the desktop shortcut symbolic links should be removed as follows:

```
$ rm -f ~/.local/share/applications/when-command.desktop
$ rm -f ~/.config/autostart/when-command-startup.desktop
$ rm -f ~/.local/bin/when-command
$ rm -Rf ~/.config/when-command
$ rm -Rf ~/.local/share/when-command
```

Of course it has to be shut down before, for example by killing it via `when-command --kill`.


## Tutorial

There is a tutorial for **When**, which illustrates how to setup the applet to do some simple tasks. The examples are very basic, but cover techniques that can be implemented for useful actions, such as:

* backup files when changes occur
* work on the filesystem when the workstation is idle.

The same combinations can be used to perform more complex tasks, using simple scripts and exploiting the right conditions and monitoring system and session events. With some effort **When** can be used to automate builds, package software, process documents and images, and so on. The tutorial can be found [here](https://github.com/almostearthling/when-command-tutorial): it's a project by itself and should evolve with time.


## Advanced features

### DBus signal handlers

Recent versions of the applet support the possibility to define system and session events using [DBus](http://dbus.freedesktop.org/). Such events can activate conditions which in turn trigger task sequences, just like any other condition. However, since this is not a common use for the **When** scheduler as it assumes a good knowledge of the DBus interprocess communication system and the related tools, this feature is intentionally inaccessible from the applet menu and disabled by default in the configuration. To access the *DBus Signal Handler Editor* dialog, the user must invoke the applet from the command line with the appropriate switch, while an instance is running in the same session:

```
$ when-command --show-signals
```

This is actually the only way to expose this dialog box. Unless the user defines one or more signal handlers, there will be no *User Defined Events* in the corresponding box and pane in the *Conditions* dialog box, and **When** will not listen to any other system and session events than the ones available in the *Events* list that can be found in the *Conditions* dialog box. The possibility to define such events must be enabled in the *Settings* dialog box, and **When** has to be restarted to make the option effective: before restart the user events are not available in the *Conditions* box, although it becomes possible to show the *DBus Signal Handler Editor* using the command shown above. If the appropriate setting is disabled, the above command exits without showing the editor dialog.

To define a signal to listen to, the following values must be specified in the *DBus Signal Handler Editor* box:

* the handler name, free for the user to define as long as it begins with an alphanumeric character (letter or digit) followed by alphanumerics, dashes and underscores
* the bus type (either *Session* or *System* bus)
* the unique bus name in dotted form (e.g. `org.freedesktop.DBus`)
* the path of the object that emits the signal (e.g. `/org/freedesktop/FileManager1`)
* the interface name in dotted form (e.g. `org.freedesktop.FileManager1`)
* the signal name
* whether the scheduler must wait until the next clock tick to process the signal (checking *Activate on next clock tick*)

All these values follow a precise syntax, which can be found in the DBus documentation. Moreover, if the signal has any parameters, constraints on the parameters can be specified for the condition to be verified: given a list of constraints, the user can choose whether to require all of them or just any to evaluate to true. The tests against signal parameters require the following data:

* *Value #* is the parameter index
* *Sub #* (optional) is the index within the returned parameter, when it is either a list or a dictionary: in the latter case, the index is read as a string and must match a dictionary key
* *comparison* (consisting of an operator, possibly negated) specifies how the value is compared to a test value: the supported operators are
  1. `=` (equality): the operands are converted to the same type, and the test is successful when they are identical; please notice that, in case of boolean parameters, the only possible comparison is equality (and the related *not* equality): all other comparisons, if used, will evaluate to false and prevent condition activation, and the comparison value should be either `true` or `false`
  2. `CONTAINS`: the test evaluates to true when either the test string is a substring of the selected value, or the parameter is a list (or struct, or dictionary: for dictionaries it only searches for values and not for keys though), no *Sub #* has been specified, and the test value is in the compound value
  3. `MATCHES`: the test value is treated as a *regular expression* and the selected value, which must be a string, matches it
  4. `<`: the selected value is less than the test value (converted to the parameter selected value type)
  5. `>`: the selected value is greater than the test value (converted to the parameter selected value type)
* *Test Value* is the user provided value to compare the parameter value to: in most cases it is treated as being of the same type as the selected parameter value.

When all the needed fields for a tests are given, the test can be accepted by clicking the *Update* button. To remove a test line, either specify *Value #* and *Sub #* or select the line to delete, then click the *Remove* button. Tests are optional: if no test is provided, the condition will be enqueued as soon as the signal is emitted. If a test is specified in the wrong way, or a comparison is impossible (e.g. comparing a returned list against a string), or any error arises within a test, the test will evaluate to *false* and the signal will not activate any associated condition. For now the tests are pretty basic: for instance nested compound values (e.g. lists of lists) are not treated by the testing algorithm. The supported parameter types are booleans, strings, numerals, simple arrays, simple structures, and simple dictionaries. Supporting more complex tests is beyond the scope of a limited scheduler: the most common expected case for the DBus signal handler is to catch events that either do not carry parameters or carry minimal information anyway.

**Warning:** when the system or session do not support a bus, path, interface, or signal, the signal handler registration fails: in this case the associated event never takes place and it is impossible for any associated condition to be ever verified.

### File and directory notifications

Monitoring file and directory changes can be enabled in the *Settings* dialog box. This is particularly useful to perform tasks such as file synchronizations and backups, but since file monitoring can be resource consuming, the option is disabled by default. File and directory monitoring is quite basic in **When**: a condition can be triggered by changes either on a file or on a directory, no filter can be specified for the change type -- that is, all change types are monitored (creations, writes and deeletions), and in case of directory monitoring all files in the directory are recursively monitored. These limitations are intentional, at least for the moment, in order to keep the applet as simple as possible. Also, no more than either a file or a directory can be monitored by a condition: in order to monitor more items, multiple conditions must be specified.

As said above, this feature is optional, and in order to make it available the `pyinotify` library has to be installed. On Ubuntu this can be achieved via the package manager (`sudo apt-get install python3-pyinotify`); alternatively `pip` can be used to let Python directly handle the installation: `sudo pip3 install pyinotify` (this will ensure that the latest release is installed, but package updates are left to the user).

There are also some configuration steps at system level that might have to be performed if filesystem monitoring does not work properly: when a monitored directory is big enough, the default *inotify watches* may fall short so that not all file changes can be notified. When a directory is under control, all its subdirectories need to be watched as well recursively, and this implies that several watches are consumed. There are many sources of information on how to increase the amount of *inotify watches*, and as usual StackExchange is one of the most valuables: see [Kernel inotify watch limit reached](http://unix.stackexchange.com/a/13757/125979) for a detailed description. Consider that other applications and utilities, especially the ones that synchronize files across the network -- such as the cloud backup and synchronization clients -- use watches intensively. In fact **When** monitoring activity should not be too different from other cases.

**Warning:** Conditions depending on file and directory monitoring are not synchronous, and checks occur on the next tick of the applet clock. Depending tasks should be aware that the triggering event might have occurred some time before the notified file or directory change.

### Environment variables

By default **When** defines one or two environment variables when it spawns subprocesses, respectively in *command based conditions* and in *tasks*. These variables are:

* `WHEN_COMMAND_TASK` containing the task name
* `WHEN_COMMAND_CONDITION` containing the name of the triggering or current condition

When the test subprocess of a command based condition is run, only `WHEN_COMMAND_CONDITION` is defined, on the other hand when a task is run both are available. This feature can be disabled in the configuration file or in the *Settings* dialog box if the user doesn't want to clutter the environment or the variable names conflict with other ones. Please note that in a *task* these variables are defined *only* if the task is set to import the environment (which is true by default): if not, it will only know the variables defined in the appropriate list. This behavior is intentional, since if the user chose not to import the surrounding environment, it means that it's expected to be as clean as possible.


## Developer notes and resources

### Why a single source file?

The applet is in fact a small utility, and I thought it also would have less features. It grew a little just because some of the features could be added almost for free, so the "*Why Not?*" part of the development process has been quite consistent for a while. The first usable version of the applet has been developed in about two weeks, most of which spent learning how to use *PyGObject* and friends, and not on a full time basis: by the 5th day I had to freeze the features (the result is the `ROADMAP.md` file) and focus on the ones I wrote down. So, being small and mostly not reusable, the single-source option seemed the most obvious, also to keep the package as self-contained as possible. However, the way the applet starts and defines its own system-wide and user directories allows for the development of modules that can be imported without cluttering and polluting the system: the `APP_DATA_FOLDER` variable defines a dedicated directory for the application where modules can be installed, and normally it points to `<install-base>/when-command/share` or `/usr/[local/]share/when-command` or something similar.

### Developer dependencies

Being an applet oriented mostly towards users of recent Ubuntu editions, it is developed in *Python 3.x* and uses the latest supported edition of *PyGObject* at the time. It shouldn't rely on other packages than `python3-gi` on the Python side. The *Glade* user interface designer is almost mandatory to edit the dialog boxes.

To implement the "*Idle Session*" based condition (i.e. the one that lets a task run when the session has been idle for a while), however, the external `xprintidle` command is used that is not installed by default on Ubuntu: at this time the DBus idle time detection function is still imperfect and crashes the applet, so it still relies on the external command. Also, by doing this, the "*Idle Session*" based condition is not much more than a *Command* based condition, and this simplified the development a lot.

### Contributing

**When** is open source software, this means that contributions are welcome. To contribute with code, please consider following the minimal recommendations that usually apply to the software published on GitHub:

1. Fork the [When repository](https://github.com/almostearthling/when-command) and pull it to your working directory
2. Create a branch for the new feature or fix: `git checkout -b new-branch`
3. Edit the code and commit: `git commit -am "Add this feature to When"`
4. Push your changes to the new branch: `git push origin new-branch`
5. Compare and submit a [Pull Request](https://github.com/almostearthling/when-command/compare)

A more general discussion about contribution can be found [here](https://help.github.com/articles/using-pull-requests/). Otherwise, just submit an issue to notify a bug, a mistake or something that could just have been implemented better. Just consider that the applet is intended to be and remain minimal in terms of code and features, so that it can stay in the background of an user session without disturbing it too much.

There is additional documentation that might be useful for contributions:

* [TRANSLATE.md](share/doc/when-command/TRANSLATE.md) contains some hints on how to use the tools described below for localization
* [PACKAGE.md](share/doc/when-command/PACKAGE.md) describes how to package **When** for Debian and Ubuntu.

### Localization

As of version *0.9.1-beta.2* **When** supports the standard localization paradigm for Linux software, via `gettext` and companion functions. This means that all translation work can be done with the usual tools available on Linux, that is:

* `xgettext` (for the Python source) and `intltool-extract` (for the *Glade* UI files)
* `msginit`, `msgmerge` and `msgfmt`

This should allow for easier translation of the software. In fact I provide the Italian localization (it's the easiest one for me): help is obviously welcome and really appreciated for other ones.

### Breaking the compatibility

As long as the software can be considered in its *pre-release* state, breaking the backwards-compatibility is allowed although undesirable. **When** has actually been released as *beta* software, since it has been tested for a while and with a suite that covered all the cases it can handle. Surely there are still bugs and they will have to be corrected. Unfortunately these bugs could also pop up in the main classes that build the core of the applet, and the "form" of these classes could affect the way the stateful part of the program data (*Tasks* and *Conditions* and possibly other items) is stored permanently: when it comes to bugs, until **When** enters a *production* state (which will be the 1.0.0 release, as per the [Semantic Versioning](https://github.com/mojombo/semver/blob/master/semver.md) specification), compatibility break will be preferred to bug persistence or bad design. Also considering that starting with release *0.5.0-beta.1* a mechanism is provided to save persistent data to a portable format that would remain valid across releases (via the `--import` and `--export` command line switches); it's advisable, while **When** is still in its early development stage, to perform an export whenever the configuration changes, in order to be able to recover if the applet is unable to start due to compatibility mismatch. All users that access **When** on the host system should take care to export their data periodically, so that when the administrator updates the package they could recover in the same way.

There have been some early changes that actually broke the backwards compatibility, without the possibility to recover: explicit variables are now used instead of properties and setters/getters in the main classes, to improve readability and clarity of code. *Tasks* and *Conditions* (and other configuration parts) created with the 0.1.x releases are not compatible with the ones that are created with version 0.2.x (and further). Releases *0.2.0* through *0.5.0-beta.1* are compatible with each other.

### Test suite

As of version *0.7.0-beta.1* **When** has an automated test suite. The test suite does not come packaged with the applet, since it wouldn't be useful to install the test scripts on the user machine: instead, it's stored in its dedicated [repository](https://github.com/almostearthling/when-command-testsuite.git), see the specific `README.md` for more details. The test suite is kept as a separate entity from the project: future releases of the test suite could be moved to a dedicated GitHub repository.

Whenever a new feature is added, that affects the *background* part of **When** (i.e. the loop that checks conditions and possibly runs tasks), specific tests should be added using the test suite "tools", that is:

* the configurable *items* export file
* the *ad hoc* configuration file
* the test functions in `run.sh`.

It has to be noted that, at least for now, the test suite is only concerned about *function* and not *performance*: since **When** is a rather lazy applet, performance in terms of speed is not a top requirement.

### Credits

Open Source Software relies on collaboration, and more than I'm happy to receive help from other developers. Here I'll list the main contributions.

* Adolfo Jayme-Barrientos, aka [fitojb](https://github.com/fitojb), for the Spanish translation

Also, I'd like to thank everyone who contributes to the development of **When** by commenting, filing bugs, suggesting features and testing. Every kind of help is welcome.

### Resources

As said above, this software is designed to run mainly on Ubuntu, so the chosen framework is *Python 3.x* with *PyGObject* (*GTK 3.0*); the interface is developed using the *Glade* interface designer. The used resources are:

* [Python 3.x Documentation](https://docs.python.org/3/)
* [PyGTK 3.x Tutorial](http://python-gtk-3-tutorial.readthedocs.org/en/latest/index.html)
* [PyGTK 2.x Documentation](https://developer.gnome.org/pygtk/stable/)
* [PyGObject Documentation](https://developer.gnome.org/pygobject/stable/)
* [GTK 3.0 Documentation](http://lazka.github.io/pgi-docs/Gtk-3.0/index.html)
* [DBus Documentation](http://www.freedesktop.org/wiki/Software/dbus/)
* [pyinotify Documentation](https://github.com/seb-m/pyinotify/wiki)

The top panel icons and the emblems used in the application were selected within Google's [Material Design](https://materialdesignicons.com/) icon collection.

Application [icon](http://www.graphicsfuel.com/2012/08/alarm-clock-icon-psd/) by Rafi at [GraphicsFuel](http://www.graphicsfuel.com/).

The guidelines specified in [UnityLaunchersAndDesktopFiles](https://help.ubuntu.com/community/UnityLaunchersAndDesktopFiles) have been roughly followed to create the launcher from within the application.

Many hints taken on [StackOverflow](http://stackoverflow.com/) and the like.
