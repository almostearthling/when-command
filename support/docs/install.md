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
6. launch the configuration utility, by typing `when config` on the command line: create a task and a condition of your choice, and save the configuration file by clicking the _Save_ button. The [simple trace](tutorial.md#simple-trace) example in the tutorial can be a good choice to verify that everything works as expected.

Once a configuration is available, the resident application can be started from the command line using the `when start` command. A shortcut can be created as described [below](#create-application-icons). On Windows, the `when-bg` command can be used instead of `when` to launch the application _detached_ from a console window.


## Linux

These steps can be followed on recent Linux distributions that derive from Debian such as Ubuntu and Mint, using a terminal:

1. install, as root or via _sudo_, the common requirements:

   ```shell
   sudo apt install build-essential libdbus-1-dev pkg-config \
                    libx11-dev libxss-dev libglib2.0-dev libdbus-1-dev \
                    libcairo2-dev libgirepository-1.0-dev \
                    gir1.2-ayatanaappindicator3-0.1 \
                    python3-tk python3-pip pipx
   ```

   On Debian, specifically, the _introspection_ package is called `libgirepository1.0-dev` instead of `libgirepository-1.0-dev`, and an extra package is needed (the _Gnome shell extension manager_) so use the following command:

   ```shell
   sudo apt install build-essential libdbus-1-dev pkg-config \
                    libx11-dev libxss-dev libglib2.0-dev libdbus-1-dev \
                    libcairo2-dev libgirepository1.0-dev \
                    gir1.2-ayatanaappindicator3-0.1 \
                    gnome-shell-extension-manager \
                    python3-tk python3-pip pipx
   ```

   Then, if you use Debian, launch the _Extension Manager_, choose the _Browse_ tab, scroll down to _AppIndicator and KStatusNotifierItem Support_ (you can use the search bar to find the entry) and install it

   ![GnomeExtensionManager](graphics/install-linux-extmgr.png)

   Make sure that it is enabled in order for **When** to work.

   On other, non-Debian based distributions, there are probably equivalent packages to install for **When** to function properly.

2. launch `pipx ensurepath` from the terminal: it should be done as the current user and **not** as root
3. install the latest release of **When**, using **pipx**:

   ```shell
   pipx install https://github.com/almostearthling/when-command/releases/latest/download/when-command-latest.zip
   ```

4. close the current console window, and open a new one: this is to ensure that the updated `PATH` environemnt variable is active
5. install **whenever** using the **When** installation tool:

   ```shell
   when tool --install-whenever
   ```

6. launch the configuration utility, by typing `when config` on the command line: create a task and a condition of your choice, and save the configuration file by clicking the _Save_ button. The [simple trace](tutorial.md#simple-trace) example in the tutorial can be a good choice to verify that everything works as expected.

Once a configuration is available, the resident application can be started from the command line using the `when start` command. A shortcut can be created as described [below](#create-application-icons). The `when-bg` command also exists on Linux, but its behavior is absolutely identical to `when`.

On non-Debian-based distributions, the package manager and the package names in step 1 will be different, while everything else should work exactly as described above. For instance, on Fedora, **When** runs apparently without major problems by installing the appropriate packages as follows:

```shell
sudo dnf group install c-development development-tools
sudo dnf install libX11-devel libXScrnSaver-devel
sudo dnf install python3-tkinter python3-pip pipx python3-devel
sudo dnf install cairo-devel cairo-gobject-devel
sudo dnf install libglibutil-devel glib2-devel gobject-introspection-devel
sudo dnf install libappindicator-gtk3
sudo dnf install dbus-devel
```

and adding the _Gnome Shell Extension Manager_ using the _Software_ utility, as well as _AppIndicator and KStatusNotifierItem Support_ using the extensions manager. After this, steps 2 to 6 are the same as in Debian based distributions.

```{tip}
In case the appearance of **When** is quirky, for example the text elements in the interface are unreadable, you might need to start the desktop environment in an _X.org_ session instead of _Wayland_ that is the default on many Linux distributions:

![GnomeLogin](graphics/install-gnome-login.png)

Older editions of _Wayland_ have incomplete support for the GUI library used by **When**, which on the other side is the one that ships with Python by default.
```


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


## Installing Directly from the Repository

If you have _git_ installed and in your _PATH_, you can choose to install a version that has not been published yet as a release, using the same _pipx_ based method. Instead of using the URL shown above, pointing to the ZIP file corresponding to the latest release, you can use the URL that points to the repository, or even a branch: launch

```shell
pipx install git+https://github.com/almostearthling/when-command.git
```

to install from the _main_ branch, which is the release candidate and is kept as stable as possible. In order to install from the _development_ branch, the command changes as follows:

```shell
pipx install git+https://github.com/almostearthling/when-command.git@development
```

and can be used on both Linux and Windows. The rest of the installation process does not change in both cases. Please note, however, that subsequent upgrades will use the same upstream source: if you want to change source (be it a different repository branch, or the release ZIP file), **When** has to be uninstalled first by running `pipx uninstall when`.


## Installation Scope

Both the installation of **When** using the **pipx** method, and the installation of **whenever** using the `--install-whenever` tool, are performed at the _user_ level: neither one requires other privileges than write in the home directory. However, this also means that no other user, except the one performing the above described actions, will be able to access either **When** or **whenever**.


## See Also

* [Toolbox](cli.md#toolbox)
* [Configuration Utility](cfgform.md)
* [Resident Wrapper](tray.md)


[`◀ Main`](main.md)

