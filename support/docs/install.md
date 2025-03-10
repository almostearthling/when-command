# Installation

The easiest way to install _When_ is using [pipx](https://pipx.pypa.io/): this works both on [Windows](#windows) and [Linux](#linux), at least in the tested distributions. Installation on Linux is somewhat more complicated due to the need of fulfilling the requirements before successfully running the application. On Windows the requirements are easier to deal with, in the sense that only [Python](https://www.python.org/) and [pipx](https://pipx.pypa.io/) need to be installed.

_Requirements_:

* [Python](https://www.python.org/) in a recent release (at least version 3.11)
* [pipx](https://pipx.pypa.io/)
* [whenever](https://github.com/almostearthling/whenever), possibly the latest binary [release](https://github.com/almostearthling/whenever/releases)

Note that even though a [recent release](https://github.com/almostearthling/whenever/releases/latest) of **whenever** is required for **When** to work as intended, **When** itself can be used to properly install and configure the core scheduler as described below.


## Windows

The following steps can be followed on both Windows 10 and Windows 11:

1. install **Python** using one of the official installation methods
2. install pipx by issuing the command `py -m pip install --user pipx` in a console window: after installation launch `pipx ensurepath` from the command prompt
3. install the latest release of **When**, using **pipx**: `pipx install https://github.com/almostearthling/when-command/releases/latest/download/when-command-latest.zip`
4. close the current console window, and open a new one: this is to ensure that the updated `PATH` environemnt variable is active
5. install **whenever** using the **When** installation tool: `when --install-whenever`
6. launch the configuration utility, by typing `when config` on the command line: create a task and a condition of your choice, and save the configuration file by clicking the _Save_ button.

Once a configuration is available, the resident application can be started from the command line using the `when start` command. A shortcut can be created as described [below](#create-application-icons). On Windows, the `when-bg` command can be used instead of `when` to launch the application _detached_ from a console window.


## Linux

The following steps can be followed on an updated version of Debian Linux 12:

1. start a Gnome session using **Xorg** as a backend

   ![GnomeLogin](graphics/install-gnome-login.png)

2. as root, install the development toolchain: `su - root -c "apt install build-essential"` (enter the root password when prompted)
3. as root, install the necessary libraries for **whenever**: `su - root -c "apt install pkg-config libx11-dev libdbus-1-dev libxss-dev"` (see above)
4. as root, install the dependencies for DBus in **When**: `su - root -c "apt install libglib2.0-dev libdbus-1-dev"` (see above)
5. as root, install the _Gnome shell extension manager_: `su - root -c "apt install gnome-shell-extension-manager"` (see above)
6. as root, install the **pip** and **pipx** Python modules: `su - root -c "apt install python3-tk python3-pip pipx"` (see above)
7. in a different terminal window, _not_ as root, launch `pipx ensurepath` from the terminal
8. start the _Gnome shell extension manager_, named simply _Extension Manager_ in the activities dashboard
9. choose the _Browse_ tab and scroll down to find _AppIndicator and KStatusNotifierItem Support_ and install it

   ![GnomeExtensionManager](graphics/install-linux-extmgr.png)

10. install the latest release of **When**, using **pipx**: `pipx install https://github.com/almostearthling/when-command/releases/latest/download/when-command-latest.zip`
11. close the current console window, and open a new one: this is to ensure that the updated `PATH` environemnt variable is active
12. install **whenever** using the **When** installation tool: `when --install-whenever`
13. launch the configuration utility, by typing `when config` on the command line: create a task and a condition of your choice, and save the configuration file by clicking the _Save_ button.

Once a configuration is available, the resident application can be started from the command line using the `when start` command. A shortcut can be created as described [below](#create-application-icons). The `when-bg` command also exists on Linux, but its behaviour is absolutely identical to `when`.


## Create Application Icons

The `--create-icons` subcommand can be used to create icons in the _Start_ or _Applications_ menu, and on the user desktop. In particular, the following _subcommand_:

```shell
when tool --create-icons --autostart
```

will create the appropriate icons in the menu _and_ create a shortcut that launches **When** and activates the **whenever** scheduler each time the desktop session is started.


## Upgrade

The upgrade process is quite easy with this type of setup, and it just consists in the following command, issued from a terminal or command window (depending on the host operating system):

```shell
pipx upgrade when
```

and there is no need to recreate the program icons, as the existing ones will continue to work. It might be necessary to stop **When** during the upgrade process. To upgrade **whenever** it is sufficient to repeat its installation step, that is:

```shell
when tool --install-whenever
```

which will always download and install the most recent binary release.


## Installation Scope

Both the installation of **When** using the **pipx** method and the installation of **whenever** using the `--install-whenever` tool are performed at the _user_ level: neither one requires other privileges than write in the home directory. However, this also means that no other user, except the one performing the above defined actions, will be able to access either **When** or **whenever**.


## See Also

* [Toolbox](cli.md#toolbox)
* [Configuration Utility](cfgform.md)
* [Resident Wrapper](tray.md)


[`◀ Main`](main.md)
