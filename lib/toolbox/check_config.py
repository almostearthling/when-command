# check_config.py
#
# check the configuration by loading it and forcing the checking function
# for each loaded element; also check the global parameters (both the native
# ones and the ones in `tags`) for correctness.


from lib.i18n.strings import *

from tomlkit import parse, TOMLDocument
from tomlkit.exceptions import ParseError

from ..items.itemhelp import ConfigurationError
from ..items.item import ALL_AVAILABLE_ITEMS_D

from ..utility import get_rich_console, write_error


def check_globals(doc: TOMLDocument) -> list[ConfigurationError]:
    errors = []
    # TODO: perform actual checks
    if doc is None:
        errors.append(ConfigurationError(message="invalid configuration file"))
    return errors


def check_items(doc: TOMLDocument) -> list[ConfigurationError]:
    tasks = []
    event_conds = []
    errors = []
    # first retrieve tasks, and store their names to test concitions
    print("#################### TASKS ########################")
    if (elems := doc.get("task")) is not None:
        for item_table in elems:
            err = None
            if (name := item_table.get("name")) is not None:
                name = item_table.get("name")
                try:
                    signature = "task:%s" % item_table["type"]
                    tags = item_table.get("tags")
                    if tags:
                        signature = "%s:%s" % (signature, tags["subtype"])
                    t = ALL_AVAILABLE_ITEMS_D.get(signature)
                    if t and name is not None:
                        factory = t[2]
                        try:
                            factory.check_in_document(name, doc)
                        except ConfigurationError as e:
                            err = e
                    else:
                        # TODO: report item line in TOML document
                        err = ConfigurationError(
                            name if name is not None else "<unnamed>",
                            message=f"unknown signature ({signature}) for task `{name}`",
                        )
                except KeyError:
                    err = ConfigurationError(name, message=f"malformed task `{name}`")
            else:
                # TODO: report item line in TOML document
                err = ConfigurationError("<unnamed>", message=f"unnamed task found")
            if err is not None:
                errors.append(err)
    # retrieve conditions and store names of event based ones
    print("#################### CONDITIONS ########################")
    if (elems := doc.get("condition")) is not None:
        for item_table in elems:
            err = None
            if (name := item_table.get("name")) is not None:
                cond_type = item_table.get("type")
                try:
                    signature = "cond:%s" % cond_type
                    tags = item_table.get("tags")
                    if tags:
                        signature = "%s:%s" % (signature, tags["subtype"])
                    t = ALL_AVAILABLE_ITEMS_D.get(signature)
                    if t and name is not None:
                        factory = t[2]
                        try:
                            factory.check_in_document(name, doc, tasks)
                        except ConfigurationError as e:
                            err = e
                    else:
                        # TODO: report item line in TOML document
                        err = ConfigurationError(
                            name if name is not None else "<unnamed>",
                            message=f"unknown signature ({signature}) for condition `{name}`",
                        )
                except KeyError:
                    err = ConfigurationError(
                        name, message=f"malformed condition `{name}`"
                    )
            else:
                # TODO: report item line in TOML document
                err = ConfigurationError(
                    "<unnamed>", message=f"unnamed condition found"
                )
            if err is not None:
                errors.append(err)
    # retrieve events
    print("#################### EVENTS ########################")
    if (elems := doc.get("event")) is not None:
        for item_table in elems:
            err = None
            if (name := item_table.get("name")) is not None:
                try:
                    signature = "event:%s" % item_table["type"]
                    tags = item_table.get("tags")
                    if tags:
                        signature = "%s:%s" % (signature, tags["subtype"])
                    t = ALL_AVAILABLE_ITEMS_D.get(signature)
                    if t:
                        factory = t[2]
                        try:
                            factory.check_in_document(name, doc, event_conds)
                        except ConfigurationError as e:
                            err = e
                    else:
                        # TODO: report item line in TOML document
                        err = ConfigurationError(
                            name if name is not None else "<unnamed>",
                            message=f"unknown signature ({signature}) for event `{name}`",
                        )
                except KeyError:
                    err = ConfigurationError(name, message=f"malformed event `{name}`")
            else:
                # TODO: report item line in TOML document
                err = ConfigurationError("<unnamed>", message=f"unnamed event found")
            if err is not None:
                errors.append(err)
    return errors


# this is the main tool function
def check_config_file(filename, verbose=True) -> bool:
    if verbose:
        console = get_rich_console()
    else:
        console = None
    try:
        with open(filename) as f:
            toml = f.read()
        doc = parse(toml)
        errors = []
        errors += check_globals(doc)
        errors += check_items(doc)
        if len(errors) > 0:
            if verbose:
                write_error(CLI_ERR_CONFIG_ERRORS_FOUND % f)
                for e in errors:
                    write_error("* %s" % str(e))
        else:
            # the only case that results in a successful outcome
            if verbose:
                console.print(CLI_MSG_NO_ERRORS_FOUND)  # type: ignore
            return True
    except FileNotFoundError:
        if verbose:
            write_error(CLI_ERR_FILE_NOT_FOUND % f)
    except ParseError as err:
        if verbose:
            write_error(CLI_ERR_CONFIG_INVALID % (f, str(err)))
    except Exception as err:
        if verbose:
            import traceback
            print(err)
            print(traceback.format_exc())
            write_error(CLI_ERR_ERROR_GENERIC)
    # if we are here the check was not positive
    return False


# end.
