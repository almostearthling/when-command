# configuration application: implements the `config` command


from lib.forms.cfgform import form_Config


# entry point for the configuration application, which is also reachable
# using the system tray menu when using the tray resident application
def main(root):
    form = form_Config()
    form.run()
    root.send_exit()


# end.
