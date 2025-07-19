# configuration application: implements the `config` command


from lib.forms.cfgform import form_Config


# entry point for the configuration application, which is also reachable
# using the system tray menu when using the tray resident application
def main(root) -> None:
    # not setting the root of form_Config() informs that this is the
    # configuration app, thus no `Reload` button should be displayed
    form = form_Config()
    form.run()
    root.send_exit()


# end.
