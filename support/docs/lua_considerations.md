# Some Considerations on Lua

The embedded _Lua_ interpreter in **whenever** is surely a powerful feature, that can efficiently replace OS commands and scripts for many purposes, sometimes also in a way that is

* more portable across systems, as the _Lua_ interpreter is the same on all systems, as well as its standard library that provides many actions usually available via different commands on different operating systems,
* significantly faster, because the interpreter is already in memory when it is instantiated by **whenever** and there are no shells and no external commands to be launched.

The version of _Lua_ embedded in **whenever** is quite recent,[^1] and in the provided binaries it is compiled for 64 bit architectures on both Linux and Windows. This actually poses a problem on Windows, where the "traditional" _Lua_ installers only come in 32 bit flavors. As long as there is no need to extend _Lua_ with extra functionalities provided by binary libraries, the supported architecture does not really impact on the embedded interpreter. However, in order to use any popular _C libraries_ in _Lua_ from the **whenever** automation tool, they would probably have to be recompiled from scratch for 64 bit Windows, because the internal interpreter would not be able to link he ones provided in common distributions.

The current version of **When** supports a [_tool_](cli.md#toolbox) to install a script or a binary library, so that it can be `require`d from the embedded interpreter in **whenever**: the `--install-lua` command, followed by a file name can be used and, if the file type is supported, it will be copied to an appropriate directory in [_APPDATA_](appdata.md) which is in the searched _paths_. The supported file types are:

* _.lua_ (_Lua_ scripts): obviously _Lua_ source files that can define functions, initialize or update tables, and so on,
* _.zip_ (ZIP archives): the zip contents, which are expected to be a tree of _Lua_ source files and possibly binary modules, are extracted in a directory with the same name of the ZIP file in the _Lua_ subdirectory of _APPDATA_.

There is no support for _Lua C (binary) modules_: the reason is that the interpreter embedded in **whenever** only operates in _safe_ mode, which in turn disables dynamic loading of extenal binary libraries, which in fact _Lua C modules_ are. Attempts to `require` a binary module, even if available in the correct directory, will result in a _module not found_ runtime error for the embedded interpreter.

At the moment no real _package management_ is available, mainly because the most popular _Lua_ package managers rely on development tools which are not always expected to be available on the host platform.

> **Note**: the _Lua_ library installation tool is in its very early development stage, and for the moment does not support either removal or upgrade for installed modules. To remove a module, it has to be manually deleted from the _Lua_ subdirectory in _APPDATA_; this is also needed for upgrades, because the `--install-lua` command will refuse, at least for now, to overwrite something that already exists. The output of the command, however, will show what has to be manually removed in order to perform an upgrade.

If a _pure Lua_ module is available as a directory structure, it is easy to produce a ZIP file that can be used with the `--install-lua` tool: most modern file managers offer a _"Archive/Compress to ZIP"_ option using a mouse click on a folder, which can be used with the folder containing the desired module. The resulting ZIP file is suitable for installation using the tool.


## See Also

* [Lua Based Tasks](tasks.md#lua-script)
* [Lua Based Conditions](cond_actionrelated.md#lua-script)
* [Toolbox](cli.md#toolbox)


[`◀ Main`](main.md)


[^1]: at the moment is in the _Lua 5.4_ series.

