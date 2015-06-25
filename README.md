# When (*when-command*)

**When** is a configurable user task scheduler, designed to work during an X/Gnome session. It interacts with the user through a GUI, where the user can define tasks and conditions, as well as relations of causality that bind conditions to task. When a condition is bound to a task, it is said to trigger a task.

The purpose of this small utility is to provide an user, possibly without administrative credentials, the ability to define conditions that do not only depend on time, but also on a particular state of the session (e.g. the result of a command run in a shell). The same result could have been achieved writing scripts that periodically issued commands, checked the results and reacted accordingly, but such a simple task could result in complex sets of scripts and settings that would be harder to maintain. *When* was born out of need: I have been a (happy) Ubuntu user for years now, and couldn't think of having a different desktop environment than the one provided by Ubuntu. In *14.04 LTS* (the release I'm using now) the environment is consistent and pleasant. One thing I've noticed that Windows has evolved is the *Task Scheduler*: in fact it looks more useful and usable than the usual *cron* daemon, at least because it allows some more options to schedule tasks than the time based ones. I needed such an applet to perform some file synchronizations when the workstation is idle, and decided to write my own task scheduler targeted to Ubuntu. The scheduler runs in the background, and it displays an indicator applet icon for user interaction.

It is not generally intended as a replacement to [*cron*](https://en.wikipedia.org/wiki/Cron) and the [Gnome Task Scheduler](http://gnome-schedule.sourceforge.net/), although to some extent these utilities might overlap. **When** is intended to be more flexible, although less precise, and to provide an alternative to more complicated solutions -- such as the implementation of *cron* jobs that check for a particular condition and execute commands when the condition is verified. In such spirit, **When** is not as fine-grained in terms of doing things on a strict time schedule: the **When** approach is that "*when* a certain condition is met, *then* something has to be done". The condition is checked periodically, and the "countermeasure" is taken *subsequently* - although not *immediately*. In fact, and with the default configuration, the delay can reach two minutes in the worst case.


## Description

The applet will show up in the indicator tray at startup, which would normally occur at login if the user chose to add **When** it to the startup programs. It will read its configuration and start the scheduler in an unattended fashion. Whenever one of the user defined conditions is met, the associated tasks are executed. A small alarm clock :alarm_clock: icon will display in the indicator tray, to show that the applet is running: by default it turns to an attention sign :warning: when the applet requires attention. Also, the icon changes its shape when the applet is *paused* (the clock is crossed by a slash) and when a configuration dialog is open (the alarm clock shows a plus sign inside the circle).

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

Tasks are basically commands associated with an environment and checks to determine whether the execution was successful or not. The interface lets the user configure some basic parameters (such as the startup directory and the *environment*) as well as what to test after execution (*exit code*, *stdout* or *stderr*). The user can choose to look for the specified text within the output and error streams (when *Exact Match* is unchecked) and to perform a case sensitive test.

The environment in which the subprocess is run can either import the current one (at **When** startup time), use its own variables or both.

The selected task (if any) can be deleted clicking the *Delete* button in the dialog box. However the application will refuse to delete a task that is used in a condition: remove the task reference from the condition first. Every task must have an *unique name*, if a task is named as an existing task it will replace the existing one.

**A note on the "Check for" option:** The applet can either ignore whatever the underlying process returns to the caller by specifying *Nothing* in the *Check for* group, or check

* exit code
* process output (*stdout*)
* process written errors (*stderr*)

to determine whether the process succeeded or failed. When choosing to check for  *Success*, the operation is considered successful *if and only if* the process result (exit code, output, or error) corresponds to the user provided value. Same yields for *Failure*: if *Failure* is chosen, only the provided result will indicate a failure. For example, in the most common case the user will choose to expect *Success* to correspond to an *Exit Code* of `0` (in fact the default choice), all other exit codes will indicate a failure. And if the user chooses to expect *Failure* to be reported as the word `Error` in the error messages, whatever other error messages will be ignored and the operation will turn out successful.


### Conditions

There are several types of condition available:

1. **Interval based**: After a certain time interval the associated tasks are executed, if the condition is set to repeat checks, the tasks will be executed again regularly after the same time interval.
2. **Time based**: The tasks are executed when the time specification is matched.
3. **Command based**: When the execution of a specified command gives the expected result (in terms of **exit code**, **stdout** or **stderr**), the tasks are executed.
4. **Idle time based**: When the session has been idle for the specified amount of time the tasks are executed. This actually is implemented as a shortcut to the command based condition based upon the `xprintidle` command, which must be installed for the applet to work properly.
5. **System event based**: The tasks are executed when a certain system event occurs. Currently only *startup* and *shutdown* are the implemented system events.

Also, the condition configuration interface allows to decide:

* whether or not to repeat checks even after a task set has been executed -- that is, make an event *periodic*;
* to execute the tasks in a task set concurrently or sequentially: please note that in the latter case no test is performed for a task to have exited successfully or not, the tasks in a set are executed one after the other anyway;
* the tasks in the task set are executed in the given order, although this makes a difference only when sequential execution is chosen;
* a condition can be suspended: it will not be checked, but it's retained in the system

The selected condition (if any) can be deleted clicking the *Delete* button in the dialog box. Every condition must have an *unique name*, if a condition is named as an existing one it will replace it.


### The History window

Since logs aren't always easy to deal with, **When** provides an easier interface to verify the task results. Tasks failures are also notified graphically via the attention-sign icon and badge notifications, however more precise information can be found in the *History* box. This shows a list of the most recently tasks that where launched by the current applet instance (the list length can be configured), which reports:

* The start time of the task and its duration in seconds
* The task *unique name*
* The *unique name* of the condition that triggered the task
* The process *exit code* (as captured by the shell)
* The result (green :heavy_check_mark: for success, red :x: for failure)
* A short hint on the failure *reason* (only in case of failure, obviously)

and when the user clicks a line in the table, the tabbed box below will possibly show the output (*stdout*) and errors (*stderr*) reported by the underlying process.


### Settings

The program settings are available through the specific *Settings* dialog box, and can be manually set in the main configuration file, which can be found in `~/.config/when-command/when-command.conf`. By defaults the settings are as follows:

The options are:

1. **General**
  * *Show Icon*: whether or not to show the indicator icon and menu
  * *Autostart*: set up the applet to run on login
  * *Notifications*: whether or not to show notifications upon task failure
  * *Icon Theme*: `Guess` to let the application decide, otherwise one of `Dark` (light icons for dark themes), `Light` (dark icons for light themes), and `Color` for colored icons that should be visible on all themes.
2. **Scheduler**
  * *Application Clock Tick Time*: represents the tick frequency of the application clock, sort of a heartbeat, each tick verifies whether or not a condition has to be checked; this option is called `tick seconds` in the configuration file
  * *Condition Check Skip Time*: all conditions will skip this amount of seconds from previous test to perform an actual test, should be at least the same as *Application Clock Tick Time*; this is named `skip seconds` in the configuration file.
3. **Advanced**
  * *Max Concurrent Tasks*: maximum number of tasks that can be run in a parallel run (`max threads` in the configuration file)
  * *Debug Level*: the amount of detail in the log file
  * *Max Log Size*: max size (in bytes) for the log file
  * *Number Of Log Backups*: number of backup log files (older ones are erased)
  * *Instance History Items*: max number of tasks in the event list (*History* window); this option is named `max items` in the configuration file.

The configuration is *immediately stored upon confirmation* to the configuration file, although some settings (such as *Notifications*, *Icon Theme*) might require a restart of the applet. The configuration file can be edited with a standard text editor, and it follows some conventions common to most configuration files. The sections in the file might slightly differ from the tabs in the *Settings* dialog, but the entries are easily recognizable.

By default the applet creates a file with the following configuration, which should be suitable for most setups:

```
[Scheduler]
tick seconds = 15
skip seconds = 60

[General]
show icon = true
autostart = true
notifications = true
log level = warning
icon theme = guess

[Concurrency]
max threads = 5

[History]
max items = 100
log size = 1048576
log backups = 4
```

Manual configuration is particularly useful to bring back the program icon once the user decided to hide it (losing access to the menu: I was doubtful about providing the option, then just decided to implement it and provide a safety net anyway), by setting the `show icon` entry to `true`. Another way to force access to the *Settings* dialog box when the icon is hidden is to explicitly invoke the applet (either from the command line, or the Gnome shell, or *Dash* on Ubuntu) when an instance is already running. However, in this case, *after the dialog box is closed, the running instance will shut down and will have to be restarted*.


### Installation requirements and Directory structure

For the applet to function and before unpacking it to the destination directory, make sure that *Python 3.x*,  *PyGObject* for *Python 3.x* and the `xprintidle` utility are installed. For example, not all of these are installed by default on Ubuntu: in this case use the following commands.

```
~$ sudo apt-get install python3-gi
~$ sudo apt-get install xprintidle
~$ cd /opt
~$ sudo tar xzf /path/to/when-command.tar.gz
```

The instructions given in the following section will complete the installation for the current user. For now the applet has to be manually added to the *Startup Applications*: for Ubuntu the instructions are in [Startup Applications](https://help.ubuntu.com/stable/ubuntu-help/startup-applications.html), and the command to specify in the *Command* entry is `python3 /opt/when-command/when-command.py` (or whatever is the path to `when-command.py`). The applet icon will display at every login.

The **When** utility will try to recognize the way it has been set up the first time it's invoked. Since there is no application icon, it has to be invoked from the command line. Assuming that it has been unarchived in `/opt` (possibly in the `/opt/when-command` directory), it's advisable to run it for the first time using the command

 ```
 ~$ python3 /opt/when-command/when-command.py
 ```

and it will create all the needed directory structure in the user folder, and notably:

* `~/.config/when-command` where it will store all configuration
* `~/.local/share/when-command` where it stores resources and logs (in the `log` subdirectory)

In the first run the utility also installs launchers and icons for the user, so that it can be launched using the Gnome shell or Ubuntu *Dash*.


## Developer notes and resources

### Why a single source file?

The applet is in fact a small utility, and I thought it also would have less features. It grew a little (but not that much in fact) just because some of the features could be added almost for free, so the "*Why Not?*" part of the development process has been quite consistent for a while. The applet has been developed in about two weeks, most of which spent learning how to use *PyGObject* and friends, and not on a full time basis: by the 5th day I had to freeze the features (the result is the `ROADMAP.md` file) and focus on the ones I wrote down. So, being small and mostly not reusable, the single-source option seemed the most obvious, also to keep the package as self-contained as possible. However, the way the applet starts and defines its own system-wide and user directories allows for the development of modules that can be imported without cluttering and polluting the system: the `APP_DATA_FOLDER` variable defines a dedicated directory for the application where modules can be installed, and normally it points to `/opt/when-command/share` or `/usr/[local/]share/when-command` or something similar. For example, in a future version that supports translations, a translation can be implemented as a Python file that exports a `resource` class and resides in the `APP_DATA_FOLDER` directory.


### Developer Dependencies

Being an applet oriented mostly towards users of recent Ubuntu editions, it is developed in *Python 3.x* and uses the latest supported edition of *GTK 3.0* (and related *PyGObject*). It shouldn't rely on other packages than `python3-gi` on the Python side. However the *Glade* user interface designer is almost mandatory to edit the dialog boxes.

To implement the "*Idle Session*" based condition (i.e. the one that lets a task run when the session has been idle for a while), however, the external `xprintidle` command is used that is not installed by default on Ubuntu: this seemed easier than to implement an idle time detection function from scratch, which could possibly be even more resource hungry than the available small external utility. Also, by doing this, the "*Idle Session*" based condition is not much more than a *Command* based condition, and this simplified the development a lot.


### Resources

The program is designed to run mainly on Ubuntu, so the chosen framework is *Python 3.x* with *PyGObject 3.x* (*GTK 3.0*); the interface is developed using the *Glade* interface designer. The used resources are:

* [Python 3.x Documentation](https://docs.python.org/3/)
* [PyGTK 3.x Tutorial](http://python-gtk-3-tutorial.readthedocs.org/en/latest/index.html)
* [PyGTK 2.x Documentation](https://developer.gnome.org/pygtk/stable/)
* [PyGObject Documentation](https://developer.gnome.org/pygobject/stable/)
* [GTK 3.0 Documentation](http://lazka.github.io/pgi-docs/Gtk-3.0/index.html)

The top panel icons and the emblems used in the application were selected within Google's [Material Design](https://materialdesignicons.com/) icon collection.

Application icon by Rafi at [GraphicsFuel](http://www.graphicsfuel.com/).

The guidelines specified in [UnityLaunchersAndDesktopFiles](https://help.ubuntu.com/community/UnityLaunchersAndDesktopFiles) have been roughly followed to create the launcher from within the application.

Many hints taken on [StackOverflow](http://stackoverflow.com/) and the like.
