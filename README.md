# When (*when-command*)

**When** is a configurable user space scheduler, designed to work during an X/Gnome session. It interacts with the user through a GUI, where the user can define tasks and conditions, as well as relations of causality that bind conditions to task. The purpose is to define conditions that do not only depend on time, but also on a particular state of the session (e.g. the result of a command run in a shell). The same result could have been achieved writing scripts that periodically issued commands, checked the results and reacted accordingly, but such a simple task could result in complex sets of scripts and settings that would be harder to maintain.

It is not generally intended as a replacement to [*cron*](https://en.wikipedia.org/wiki/Cron) and the [Gnome Task Scheduler](http://gnome-schedule.sourceforge.net/), although to some extent these utilities might overlap. **When** is intended to be more flexible, although less precise, and to provide a user interface to more complicated solutions -- such as the implementation of *cron* jobs that check for a particular condition and execute commands when the condition is verified.

When a condition is bound to a task, it is said to trigger a task.

The scheduler runs in the background, although it displays an indicator applet icon. How the scheduler checks the task result is flexibly defined by the user.


## Program description

The applet will show up in the indicator tray at startup, which would normally occur at login if the user chose to add it to the startup programs. It will read its configuration and start the scheduler without user interaction. Whenever one of the user defined conditions is met, the associated tasks are executed. A small alarm clock :alarm_clock: icon will display in the indicator tray, to show that the applet is running: it changes to an attention sign :warning: when something went wrong or the applet requires attention anyway.

Clicking the icon gives access to the main menu: it allows basic interaction (such as *pause*/*resume*), to quit the applet and stop the scheduler, and to configure tasks, conditions and the applet itself. The configuration is *immediately stored upon confirmation*, as well as task and condition definitions.


### Installation Requirements

For the applet to function and before unpacking it to the destination directory, make sure that *Python 3.x*,  *PyGObject* for *Python 3.x* and the *xprintidle* utility are installed. For example, not all of these are installed by default on Ubuntu: in this case use the following commands.

```
~$ sudo apt-get install python3-gi
~$ sudo apt-get install xprintidle
~$ cd /opt
~$ sudo tar xzf /path/to/when-command.tar.gz
```

The instructions given in the following section will complete the installation for the current user. For now the applet has to be manually added to the *Startup Applications*: for Ubuntu the instructions are in [Startup Applications](https://help.ubuntu.com/stable/ubuntu-help/startup-applications.html), and the command to specify in the *Command* entry is `python3 /opt/when-command/when-command.py` (or whatever is the path to `when-command.py`). The applet icon will display at every login.


### Directory structure

The When utility will try to recognize the way it has been set up the first time it's invoked. Since there is no application icon, it has to be invoked from the command line. Assuming that it has been unarchived in `/opt` (thus creating the `/opt/when-command` directory), it's advisable to run it for the first time using the command

```
~$ python3 /opt/when-command/when-command.py
```

and it will create all the needed directory structure in the user folder, and notably:

* `~/.config/when-command` where it will store all configuration
* `~/.local/share/when-command` where it stores resources and logs (in the `log` subdirectory)

In the first run the utility also installs icons for the user, so that it can be launched using the Gnome launcher (e.g. *Dash*).


### Tasks

Tasks are basically commands associated with an environment and checks to determine whether the execution was successful or not. The interface lets the user configure some basic parameters (such as the startup directory and the environment) as well as what to test after execution (*exit code*, *stdout* or *stderr*). The user can choose to look for the specified text within the output and error streams (when *Exact Match* is unchecked) and to perform a case sensitive test.

The selected task (if any) can be deleted though, clicking the *Delete* button in the dialog box. However the application will refuse to delete a task that is used in a condition: remove the task reference from the condition first.

Every task must have an *unique name*, if a task is named as an existing task it will replace the existing one.


### Conditions

There are several types of condition available:

1. **Interval based**: After a certain time interval the associated tasks are executed, if the condition is set to repeat checks, the tasks will be executed again regularly after the same time interval.
2. **Time based**: The tasks are executed when the time specification is matched.
3. **Command based**: When the execution of a specified command gives the expected result (in terms of **exit code**, **stdout** or **stderr**), the tasks are executed.
4. **Idle time based**: When the session has been idle for the specified amount of time the tasks are executed. This actually is implemented as a shortcut to the command based condition based upon the *xprintidle* command, which must be installed for the applet to work properly.
5. **System event based**: The tasks are executed when a certain system event occurs. Currently only *startup* and *shutdown* are the implemented system events.

Also, the condition configuration interface allows to decide:

* whether or not to repeat checks even after a task set has been executed -- that is, make an event cyclical;
* to execute the tasks in a task set concurrently or sequentially: please note that in the latter case no test is performed for a task to have exited successfully or not, the tasks in a set are executed one after the other anyway;
* the tasks in the task set are executed in the given order, although this makes a difference only when sequential execution is chosen.
* a condition can be suspended: it will not be checked, but it's retained in the system

The selected condition (if any) can be deleted though, clicking the *Delete* button in the dialog box.

Every condition must have an *unique name*, if a condition is named as an existing one it will replace it.


### Settings

The program settings are available through the specific *Settings* dialog box, and can be manually set in the main configuration file, which can be found in `~/.config/when-command/when-command.conf`. By defaults the settings are as follows:

The options are:

1. General
  * *Show Icon*: whether or not to show the indicator icon and menu
  * *Autostart*: set up the applet to run on login
  * *Notifications*: whether or not to show notifications upon task failure
  * *Log Level*: the amount of detail in the log file
  * *Icon Theme*: `guess` to let the application decide, otherwise one of `dark` (light icons for dark themes), `light` (dark icons for light themes), `color` for colored icons that should be visible on all themes
2. Scheduler
  * *Tick Seconds*: represents the tick frequency of the application scheduler, each tick verifies whether or not a condition has to be checked
  * *Skip Seconds*: (by default) all conditions will skip this amount of seconds from previous test to perform an actual test, should be at least the same as *Tick Seconds*
3. Concurrency
  * *Max Threads*: the maximum number of parallel tasks that can be run in a parallel run, and the maximum number of conditions that can be checked at once
4. History and log management
  * *Max Items*: max number of tasks in the event list (history window)
  * *Log Size*: max size (in bytes) for the log file
  * *Log Backups*: number of backup log files (older ones are erased)

All these options have default values in the configuration file that is created by default with the following content:

```
[Scheduler]
tick seconds = 15
skip seconds = 60

[General]
show icon = true
autostart = true
notifications = true
log level = debug
icon theme = guess

[Concurrency]
max threads = 5

[History]
max items = 100
log size = 1048576
log backups = 4
```

These options can also be set manually: it is particularly useful in case the user chooses not to show the applet icon and wants to have the icon (and menu) back on the top panel. This can be achieved by setting the `show icon` option to `true`. Also, in case the icon is lost, the user can manually start the applet even if there is a hidden instance running: this will recall the settings dialog box, where the user can set whatever oprion graphically. *After the dialog box is closed, the running instance will shut down and will have to be restarted.*

The default settings should be suitable for most setups.


## Developer notes and resources

### Why a single source file?

The applet is in fact a small utility, and I thought it also would have less features. It grew a little (but not that much in fact) just because some of the features could be added almost for free, so the "*Why Not?*" part of the development process has been quite consistent for a while. The applet has been developed in about two weeks, most of which spent learning how to use *PyGObject* and friends, and not on a full time basis: by the 5th day I had to freeze the features (the result is the `ROADMAP.md` file) and focus on the ones I wrote down. So, being small and mostly not reusable, the single-source option seemed the most obvious, also to keep the package as self-contained as possible. However, the way the applet starts and defines its own system-wide and user directories allows for the development of modules that can be imported without cluttering and polluting the system: the `APP_DATA_FOLDER` variable defines a dedicated directory for the application where modules can be installed, and normally it points to `/opt/when-command/share` or `/usr/[local/]share/when-command` or something similar. For example, in a future version that supports translations, a translation can be implemented as a Python file that exports a `resource` class and resides in the `APP_DATA_FOLDER` directory.


### Dependencies

*When* was born out of need: I have been a (happy) Ubuntu user for years now, and couldn't think of having a different desktop environment than the one provided by Ubuntu. In *14.04 LTS* (the release I'm using now) the environment is consistent and pleasant. One thing I've noticed that Windows has evolved is the *Task Scheduler*: in fact it looks more useful and usable than the usual *cron* daemon, at least because it allows some more options to schedule tasks than the time based ones. I needed such an applet to perform some file synchronizations when the workstation is idle, and decided to write my own task scheduler targeted to Ubuntu.

Being an applet oriented mostly towards users of recent Ubuntu editions, it is developed in *Python 3.x* and uses the latest supported edition of *GTK 3.0* (and related *PyGObject*). It shouldn't rely on other packages than `python3-gi` on the Python side.

To implement the "*Idle Session*" based condition (i.e. the one that lets a task run when the session has been idle for a while), however, the external `xprintidle` command is used that is not installed by default on Ubuntu: this seemed easier than to implement an idle time detection function from scratch, which could possibly be even more resource hungry than the available small external utility. Also, by doing this, the "*Idle Session*" based condition is not much more than a *Command* based condition, and this simplified the development a lot.


### Resources

The program is designed to run mainly on Ubuntu, so the chosen framework is *Python 3.x* with *PyGObject 3.x* (*GTK 3.0*); the interface is developed using the official Glade interface designer. The used resources are:

* [Python 3.x Documentation](https://docs.python.org/3/)
* [PyGTK 3.x Tutorial](http://python-gtk-3-tutorial.readthedocs.org/en/latest/index.html)
* [PyGTK 2.x Documentation](https://developer.gnome.org/pygtk/stable/)
* [PyGObject Documentation](https://developer.gnome.org/pygobject/stable/)
* [GTK 3.0 Documentation](http://lazka.github.io/pgi-docs/Gtk-3.0/index.html)

The top panel icons and the emblems used in the application were selected within Googles [Material Design](https://materialdesignicons.com/) icon collection.

Application icon by Rafi at [GraphicsFuel](http://www.graphicsfuel.com/).

The guidelines specified in [UnityLaunchersAndDesktopFiles](https://help.ubuntu.com/community/UnityLaunchersAndDesktopFiles) have been roughly followed to create the launcher from within the application.

Many hints taken on [StackOverflow](http://stackoverflow.com/) and the like.
