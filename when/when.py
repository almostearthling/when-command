#!/usr/bin/env python
# application launcher and command line interpreter

from lib.i18n.strings import *

import sys
import os.path
import argparse
import shutil

BASEDIR = os.path.dirname(os.path.dirname(sys.argv[0]))
if not BASEDIR:
    BASEDIR = '.'
sys.path.append(BASEDIR)

from lib.utility import get_default_configdir, get_configfile, set_UI_theme
from lib.repocfg import AppConfig


# this is used to enable exception handling too
DEBUG = AppConfig.get('DEBUG')


# utility to bail out with a consistent error message
def exiterror(s, code=2):
    sys.stderr.write("%s error: %s\n" % (UI_APP, s))
    sys.exit(code)


# main program: it actually perform CLI parsing
def main():

    default_appdata = get_default_configdir()
    default_whenever = shutil.which('whenever')

    parser = argparse.ArgumentParser(
        description=CLI_APP_DESCRIPTION,
        epilog=CLI_APP_HELP_EPILOG,
        )
    parser.add_argument(
        "command",
        help=CLI_ARG_HELP_COMMAND,
        choices=['start', 'config', 'version'],
        )
    parser.add_argument(
        "-D", "--dir-appdata",
        help=CLI_ARG_HELP_DIR_APPDATA,
        type=str,
        default=default_appdata,
    )
    parser.add_argument(
        "-W", "--whenever",
        help=CLI_ARG_HELP_WHENEVER,
        type=str,
        default=default_whenever,
    )
    parser.add_argument(
        "-L", "--log-level",
        help=CLI_ARG_HELP_LOGLEVEL,
        type=str,
        choices=['trace', 'debug', 'info', 'warn', 'error'],
        default='info',
    )

    args = parser.parse_args()

    # set some global configuration values according to CLI options
    AppConfig.set('APPDATA', args.dir_appdata)
    AppConfig.set('LOGLEVEL', args.log_level)
    AppConfig.set('WHENEVER', args.whenever)

    # create the application data directory if it does not exist
    datadir = AppConfig.get('APPDATA')
    if not os.path.exists(datadir):
        try:
            os.makedirs(datadir)
        except Exception as e:
            exiterror(CLI_ERR_DATADIR_UNACCESSIBLE)

    # run the selected action
    command = args.command

    # display the version and exit
    if command == 'version':
        print("%s: v%s" % (UI_APP, UI_APP_VERSION))

    # open the configuration utility and exit after its use
    elif command == 'config':
        if DEBUG:
            set_UI_theme()
            configfile = get_configfile()
            if not os.path.exists(configfile):
                try:
                    with open(configfile, 'w') as f:
                        f.write("# Created by: %s v%s" % (UI_APP, UI_APP_VERSION))
                except Exception as e:
                    exiterror(CLI_ERR_CONFIG_UNACCESSIBLE)
            from lib.cfgapp import main
            main()
        else:
            try:
                set_UI_theme()
                configfile = get_configfile()
                if not os.path.exists(configfile):
                    try:
                        with open(configfile, 'w') as f:
                            f.write("# Created by: %s v%s" % (UI_APP, UI_APP_VERSION))
                    except Exception as e:
                        exiterror(CLI_ERR_CONFIG_UNACCESSIBLE)
                from lib.cfgapp import main
                main()
            except Exception as e:
                exiterror("unexpected exception '%s'" % e)

    # start the resident application and display an icon on the tray area
    elif command == 'start':
        if DEBUG:
            set_UI_theme()
            whenever = AppConfig.get('WHENEVER')
            if whenever is None or not os.path.exists(whenever) or not os.access(whenever, os.X_OK):
                exiterror(CLI_ERR_WHENEVER_NOT_FOUND)
            from lib.trayapp import main
            main()
        else:
            try:
                set_UI_theme()
                whenever = AppConfig.get('WHENEVER')
                if whenever is None or not os.path.exists(whenever) or not os.access(whenever, os.X_OK):
                    exiterror(CLI_ERR_WHENEVER_NOT_FOUND)
                from lib.trayapp import main
                main()
            except Exception as e:
                exiterror("unexpected exception '%s'" % e)

    else:
        exiterror("unknown command: %s" % command)


# standard startup
if __name__ == '__main__':
    main()


# end