# Extra Conditions

The condition items described here cover various different aspects of a session, and their availability may vary depending on the hosting platform and the presence of certain features.


## System Load

This test verifies whether or not the system load is below a certain percentage and, if so, runs the related tasks. The only available specific parameter is the percentage treshold below which the test is considered successful.

![WhenCondExtraSysload](graphics/when-cond-extra-sysload.png)

The item can be used on Windows and Linux systems, and depends on the availability of the _PowerShell_ in the first case, and the presence of the `vmstat` and `bc` OS commands in the latter, which may need to be installed on some distributions. The checks for this condition are performed about every minute.
