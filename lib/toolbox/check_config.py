# check_config.py
#
# check the configuration by loading it and forcing the checking function
# for each loaded element; also check the global parameters (both the native
# ones and the ones in `tags`) for correctness.


from tomlkit import table, items, TOMLDocument
from tomlkit_extras import (
    TOMLDocumentDescriptor,
    AoTDescriptor,
    TableDescriptor,
    Hierarchy,
)

from ..items.itemhelp import ConfigurationError
from ..items.item import ALL_AVAILABLE_ITEMS_D


def check_globals(doc: TOMLDocument) -> bool:
    # TODO: perform actual checks
    if doc is None:
        raise ConfigurationError(message="invalid configuration file")
    return True


def check_items(doc: TOMLDocument) -> list[ConfigurationError]:
    tasks = []
    event_conds = []
    errors = []
    # first retrieve tasks, and store their names to test concitions
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
                        err = ConfigurationError(
                            name,
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
                        err = ConfigurationError(
                            name,
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
                        err = ConfigurationError(
                            name,
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


# end.
