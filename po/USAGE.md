# Usage

This text is here to just remind how to use the files in the `po` directory, until a proper MAKEFILE is created.


## Extract translatables

The following commands are needed for the program and the UI files:

```
$ for x in share/*.glade ; do intltool-extract --type=gettext/glade $x ; done
$ xgettext -k_ -kN_ -o po/messages.pot -D . -D share -f po/translate.list
```


## Create and update translations

To create a translation, one should be in a localized environment:

```
$ export LANG=it_IT
$ msginit --locale=it_IT
```

where `it_IT` should be changed for other locales. For all `.po` in the `po` directory (in this case `it.po` is created), the following command can be used to create an updated file without losing previous work:

```
$ msgmerge -U po/it.po po/messages.pot
```

where `it.po` should be changed according to locale to translate.


## Create object file

After editing the `.po` file, the following commands create a localization file in a subtree of `share/locale` that is ready for packaging and distribution:

```
$ mkdir -p share/locale/it/LC_MESSAGES
$ msgfmt po/it.po -o share/locale/it/LC_MESSAGES/when-command.mo
```

Also here, `it.po` and the `/it/` part in the folder has to be changed according to the translated locale. In the `/opt/when-command/` based setup , the `share` directory will be copied as it is, in standard setups the package will take care to copy the appropriate files to the standard localization directory.
