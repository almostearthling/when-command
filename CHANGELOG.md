# Changelog

## Version 0.5.0 (beta)
* More consistent dialog boxes
* Task and condition naming rules


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
