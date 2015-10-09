# Changelog

## Version 0.7.0 (beta)
* Implement generic DBus signal handler and related toolbox
* Some conditions can be activated from the command line
* File and directory change notifications
* Bug fixes

### Compatibility break

This release breaks compatibility with previous version regarding the binary format of static data (conditions), as it introduces a new condition type for file notifications. The problem only affects *downgrading* from this to previous releases, upgrades are safe and all static data is correctly loaded. Unless file notification conditions are enabled and defined, a downgrade should be safe as well.


## Version 0.6.0 (beta)
* Match regular expressions in command output for tasks and command based conditions
* Stop task sequence on task outcome
* Major bug fixes
* Refactoring for better integration with host environment

### Compatibility break

This release breaks compatibility with previous version regarding the binary format of static data (tasks and conditions), as it introduces new parameters in both tasks and command based conditions. **A dump and restore of static data is required for *When* to work correctly.**

* Before upgrade: `/opt/when-command/when-command --export --shutdown`
* Upgrade: `sudo dpkg --install when-command-0.6.0-beta.1.deb` (or your preferred upgrade method)
* After upgrade: `/opt/when-command/when-command --import`

Then you can start the applet from *Dash* or at the next login. This should be done for all accounts that use *When* on the system.


## Version 0.5.0 (beta)
* More consistent dialog boxes
* Task and condition naming rules
* Command line options for
  - configuration management
  - accessing dialog boxes
  - applet information
  - applet control
* Import and export static data across incompatible versions

### Note about compatibility breaks

This release introduces a way to save static data (tasks and conditions) in a portable format that is not subject to significant changes across versions: this should solve the concern about compatibility breaks when the core structures of the program are modified in an incompatible way.


## Version 0.3.0 (beta)
* Perform shutdown tasks on logout, shutdown and reboot (Issue #8)
* Create autostart directory when not present (Issue #15)
* Keep pause state across sessions (configurable, default: on, Issue #11)


## Version 0.2.0 (beta)
* Code refactoring and cleanup
* Some GTK warnings were addressed

### Warning: compatibility break

This release is not compatible with previous ones, both *Tasks* and *Conditions* must be redefined from scratch. Hopefully this will be the one and only compatibility break. To clean up tasks and conditions, please do the following in a terminal window (on Ubuntu):

```
~$ rm ~/.config/when-command/*.list
~$ rm ~/.config/when-command/*.task
~$ rm ~/.config/when-command/*.cond
```

This preserves at least global configuration.


## Version 0.1.1 (beta)
All known issues closed
* Dialog boxes jump to top level
* Exit codes are forced to integers


## Version 0.1.0 (beta)
First usable public beta release:
* Tasks
* Conditions (time and interval based, command based, idle time, and event)
* History
* Pause/Resume
* Global settings
* Auto configuration at first use
