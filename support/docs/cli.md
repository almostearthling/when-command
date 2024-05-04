# Command Line Interface (CLI)

This version of **When** uses [poetry](https://python-poetry.org/) to manage dependencies and to provide a suitable environment for a source distribution: after running `poetry install` in the project directory to install all necessary Python dependencies, **When** can be launched as follows:

```shell
poetry run when COMMAND [OPTIONS]
```

where `COMMAND` is one of the following:

- `config` to launch the [configuration utility](cfgform.md), without staying resident (i.e. no system tray icon)
- `start` to launch the resident **whenever** [wrapper](tray.md) displaying a control icon on the system tray area
- `version` to display version information.

More commands might be supported in the future. `OPTIONS` are the possible options, some of which have effect specific on specific commands:

- `-D`/`--dir-appdata` _PATH_: specify the application data and configuration directory (default: _%APPDATA%\Whenever_ on Windows, _~/.whenever_ on Linux)
- `-W`/`--whenever` _PATH_: specify the path to the whenever executable (defaults to the one found in the PATH if any, otherwise exit with error, specific to `start`)
- `-L`/`--log-level` _LEVEL_: specify the log level, all **whenever** levels are supported (default: _info_, specific to `start`)
- `-h`/`--help`: print a brief help message about commands and options.

> **Note**: In order to simplify the usage of **When**, many values that could have been implemented as parameters are instead left as defaults that cannot be chenged, at least for now, if not via direct intervention on the code.


[`◀ Main`](main.md)
