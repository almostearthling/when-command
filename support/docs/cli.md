# Command Line Interface (CLI)

The documentation assumes that **When** has been installed using the instructions provided in the installation [guide](install.md). In this case the `when` command should be available from the command line, and could be invoked as follows:

```shell
when COMMAND [OPTIONS]
```

where `COMMAND` is one of the following:

- `config` to launch the [configuration utility](cfgform.md), without staying resident (i.e. no system tray icon)
- `start` to launch the resident **whenever** [wrapper](tray.md) displaying a control icon on the system tray area
- `tool` to launch one of the utilities that can help in the setup of a working environment
- `version` to display version information.

More commands might be supported in the future. `OPTIONS` are the possible options, which have effect on specific commands:

- `-D`/`--dir-appdata` _PATH_: specify the application data and configuration directory (default: _%APPDATA%\Whenever_ on Windows, _~/.whenever_ on Linux)
- `-W`/`--whenever` _PATH_: specify the path to the whenever executable (defaults to the one found in the PATH if any, otherwise exit with error, specific to `start`)
- `-L`/`--log-level` _LEVEL_: specify the log level, all **whenever** levels are supported (default: _info_, specific to `start`)
- `-h`/`--help`: print a brief help message about commands and options.

In order to know which options can be used for each command, `when COMMAND --help` can be invoked from the command line, where `COMMAND` is one of the commands described above.

> [!NOTE] In order to simplify the usage of **When**, many values that could have been implemented as parameters are instead left as defaults that cannot be changed, at least for now, if not via direct intervention on the code.

This version of **When** uses [poetry](https://python-poetry.org/) to manage dependencies and to provide a suitable environment for a source distribution, therefore after running `poetry install` in the project directory to install all necessary Python dependencies, **When** can also be launched as `poetry run when COMMAND [OPTIONS]`.


## Toolbox

The `tool` command provides various utilities that can help in the setup of **When** for a desktop environment. Each utility is invoked by means of a subcommand, which might possibly have variants. The following list explains the available subcommands and their options:

* `--install-whenever`: downloads and installs the latest version of **whenever** for the current user
* `--create-icons`: create the **When** desktop shortcuts (for both the configuration utility and for the resident application) for the current user in the _Start_ or _Applications_ menu -- depending on the host platform; accepts the following modifiers
  * `--autostart`: (option) creates a shortcut that launches the resident version of **When** when the user logs in
  * `--desktop`: (option) also creates icons on the desktop[^1]
* `--fix-config`: fix legacy configuration files converting [old item definitions](configfile.md#legacy-configuration-files) to new ones
* `--install-lua`: install a _Lua_ script or library in the _Lua_ specific subtree within the [_APPDATA_](appdata.md) directory
* `--upgrade-lua`: upgrade a _Lua_ script or library in the _Lua_ specific subtree within the [_APPDATA_](appdata.md) directory: similar to `--install-lua`, but only works when a module _already exists_
* ...
* `--quiet`: (option) applies to all the operations described above, and inhibits printing messages to the console.

The subcommands cannot be combined. The **whenever** installation step should be performed first if there is no working copy of the core scheduler on the system.


## See Also

* [Installation](install.md)
* [Configuration Utility](cfgform.md)
* [Resident Wrapper](tray.md)


[`◀ Main`](main.md)


[^1]: on some Linux desktop (for example, the most recent versions of Gnome) the deployment of launcher files in the `~/Desktop` subfolder is not honored as a way to create desktop icons, thus the `--desktop` option is actually executed, but has no effect.
