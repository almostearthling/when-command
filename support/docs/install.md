# Installation

The easiest way to install _When_ is using [pipx](https://pipx.pypa.io/): this works both on [Windows](#windows) and [Linux](#linux), at least in the tested distributions. Installation on Linux is somewhat more complicated due to the need of fulfilling the requirements before successfully running the application. On Windows the requirements are easier to deal with, in the sense that only [Python](https://www.python.org/) and [pipx](https://pipx.pypa.io/) need to be installed.

_Requirements_:

* [Python](https://www.python.org/) in a recent release (at least version 3.11)
* [pipx](https://pipx.pypa.io/)
* [whenever](https://github.com/almostearthling/whenever), possibly the latest binary [release](https://github.com/almostearthling/whenever/releases)

Note that even though a [recent release](https://github.com/almostearthling/whenever/releases/latest) of **whenever** is required for **When** to work as intended, **When** itself can be used to properly install and configure the core scheduler as described below.


## Windows

These steps can be followed on both Windows 10 and Windows 11:

1. install **Python** using one of the official installation methods
2. install pipx by issuing the command `py -m pip install --user pipx` in a console window: after installation launch `pipx ensurepath` from the command prompt
3. install the latest release of **When**, using **pipx**:

   ```batch
   pipx install https://github.com/almostearthling/when-command/releases/latest/download/when-command-latest.zip
   ```

4. close the current console window, and open a new one: this is to ensure that the updated `PATH` environemnt variable is active
5. install **whenever** using the **When** installation tool: `when tool --install-whenever`
6. launch the configuration utility, by typing `when config` on the command line: create a task and a condition of your choice, and save the configuration file by clicking the _Save_ button.

Once a configuration is available, the resident application can be started from the command line using the `when start` command. A shortcut can be created as described [below](#create-application-icons). On Windows, the `when-bg` command can be used instead of `when` to launch the application _detached_ from a console window.


## Linux

These steps can be followed on an updated version of Debian Linux 12, and should work on debian derivative with few changes:

1. start a Gnome session using **Xorg** as a backend

   ![GnomeLogin](graphics/install-gnome-login.png)

2. as root, install the development toolchain: `su - root -c "apt install build-essential"` (enter the root password when prompted: if _sudo_ is available, it can be used, of course, instead of becoming root)
3. as root, install the necessary libraries for **whenever**: `su - root -c "apt install pkg-config libx11-dev libdbus-1-dev libxss-dev"` (see above)
4. as root, install the dependencies for DBus in **When**: `su - root -c "apt install libglib2.0-dev libdbus-1-dev"` (see above)
5. as root, install the python bindings for Gnome _GObject_ (optional[^2]): `su - root -c "apt install libcairo2-dev libgirepository-2.0-dev"` (see above)
6. as root, install the _Gnome shell extension manager_[^1]: `su - root -c "apt install gnome-shell-extension-manager"` (see above)
7. as root, install the **pip** and **pipx** Python modules: `su - root -c "apt install python3-tk python3-pip pipx"` (see above)
8. in a different terminal window, _not_ as root, launch `pipx ensurepath` from the terminal
9. start the _Gnome shell extension manager_, named simply _Extension Manager_ in the activities dashboard[^1]
10. choose the _Browse_ tab and scroll down to find _AppIndicator and KStatusNotifierItem Support_ and install it[^1]

    ![GnomeExtensionManager](graphics/install-linux-extmgr.png)

11. install the latest release of **When**, using **pipx**:

    ```shell
    pipx install https://github.com/almostearthling/when-command/releases/latest/download/when-command-latest.zip
    ```

12. close the current console window, and open a new one: this is to ensure that the updated `PATH` environemnt variable is active
13. install **whenever** using the **When** installation tool: `when tool --install-whenever`
14. launch the configuration utility, by typing `when config` on the command line: create a task and a condition of your choice, and save the configuration file by clicking the _Save_ button.

> **Note**: the steps from 1 to 7 can be condensed in a single command:
>
> ```shell
> su - root -c "apt install build-essential pkg-config libx11-dev \
>               libdbus-1-dev libxss-dev libglib2.0-dev libdbus-1-dev \
>               libcairo2-dev libgirepository-2.0-dev \
>               gnome-shell-extension-manager python3-tk \
>               python3-pip pipx"
> ```
>
> or, if _sudo_ is available for the user:
>
> ```shell
> sudo apt install build-essential pkg-config libx11-dev \
>                  libdbus-1-dev libxss-dev libglib2.0-dev libdbus-1-dev \
>                  libcairo2-dev libgirepository-2.0-dev \
>                  gnome-shell-extension-manager python3-tk \
>                  python3-pip pipx"
> ```
>

Once a configuration is available, the resident application can be started from the command line using the `when start` command. A shortcut can be created as described [below](#create-application-icons). The `when-bg` command also exists on Linux, but its behavior is absolutely identical to `when`.


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


[^1]: these steps might not be required on some distributions, like _Linux Mint_, that natively support system tray icons.
[^2]: optional, but in fact allow the application to show the tray menu and the tray icon to be rendered in a nice way.
