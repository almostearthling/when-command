# When

![HeaderImage](support/docs/graphics/when_banner.png)

This repository hosts the development of **When**, a Python based graphical frontend for [**whenever**](https://github.com/almostearthling/whenever): although sometimes referred to as a scheduler, **whenever** is actually an automation tool, capable of executing _tasks_ when specific _conditions_ are met.

![MainWindow](support/docs/graphics/when-application.png)

**When** aims at providing a simple interface to configure **whenever**, and an easy way to monitor and control the scheduler through an icon sitting in the _tray area_ of your desktop. This utility works on both Linux and Windows, and gives access to the features of **whenever** that are supported on the host environment.


## :sparkles: Purpose

The **When** application can be used to install, configure, and run **whenever** in a desktop environment:

* the installation procedure takes care of downloading the latest available version of **whenever**, installing it to a suitable location, creating the program icons in the host environment, and setting it up to start automatically when the user session begins;
* the configuration utility is a GUI application that allows to define
  * the _tasks_ that the automation tool should activate
  * the _conditions_ that should be verified to activate the _tasks_
  * the _events_ that, in some cases, will trigger _conditions_
  * the global scheduler parameters;
* the resident application takes care of starting **whenever** in a separate process with the current configuration, and provides a basic interface to interact with it through a menu that can be reached from the icon sitting in the desktop _tray area_.

**When** offers a selection of common configuration items (_conditions_, _events_, and _tasks_) which would be difficult to define manually in the scheduler configuration file. Such items include (but are not limited to):

* session related _tasks_ such as shutdown and sleep;
* _conditions_ based on
  * time intervals or instants, and
  * duration of an idle session
  * system load or battery status
  * session being locked or unlocked;
* _events_ triggered by the system or by changes in files and directories.

The documentation is more exhaustive than the above list, and describes in detail all the currently supported items.


## :book: Documentation

The [documentation](https://almostearthling.github.io/when-command/) almost covers all aspects of **When**, and a simple [tutorial](https://almostearthling.github.io/when-command/tutorial.html) is available to see some quick examples of common use cases.


## :floppy_disk: Installation

**When** has requirements that vary according to the platform that should host it, and that on Linux may also depend on the distribution: the standard [installation procedure](https://almostearthling.github.io/when-command/install.html) attempts at describing these requirements, and providing a streamlined way to install, configure, and launch both **When** and **whenever**.

> :bell: **Note**
> Neither **When** nor **whenever** require administrative rights for the suggested setup: the instructions lead to an installation that is limited to the user that performs it. Following these instructions, both the scheduler and the application will be executed in the user environment, inheriting the user specific permissions: considering that they run as a background application, this type of setup can be considered safer than a system wide one.


## :hammer_and_wrench: Compatibility

**When** is usually tested on Windows (10 and 11) and some Debian based Linux distributions: Debian, Ubuntu, and Mint. Some packages are required to run on these Linux distros, that are not installed by default. The same yields for distributions that derive from other bases: probably it will not be difficult to find equivalent packages to those specified for a successful installation in the tested environments. The [installation procedure](https://almostearthling.github.io/when-command/install.html), for instance, lists the packages needed to install **When** on Fedora.

In some cases (that is, in _Wayland_ based environments that do not fully support the _X.org_ protocol) the _X.org_ backend may have to be used in order to successfully run **When**.


## :radioactive: Issues and Breaking Changes

As of version 1.10 the configuration file format specific to **When** has changed; while it is safe to use an old configuration file with the resident [tray application](https://almostearthling.github.io/when-command/tray.html), some of the items will not be recognized or edited by the configuration utility. Please use the `--fix-config` [tool](https://almostearthling.github.io/when-command/cli.html#toolbox) to safely convert an old configuration file to the new format, which by the way implements specific items in a more efficient way. The `--fix-config` tool also removes JSON strings from the configuration, which are not supported anymore in recent versions of **whenever**.


## :lady_beetle: Bug Reporting

If there is a bug in the **When** application, please use the project [issue tracker](https://github.com/almostearthling/when-command/issues) to report it.


## :balance_scale: License

**When** is released under the terms of the [BSD 3-Clause "New" or "Revised" License](LICENSE).
