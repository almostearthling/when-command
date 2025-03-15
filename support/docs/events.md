# Native Events Editors

The only type of event editable in **When** that is natively supported by the scheduler is the one that depends on changes in files and directories that are monitored by the operating system.


## File System Monitoring

This type of event fires whenever one of the monitored files or directories undergoes a modification: for files it means that its contents or metadata are altered, for directories it also occurs when there is a change in any of the files that they contain. In the latter case, subdirectories are also monitored if the _Recursive_ flag is set.

![WhenEventFSChange](graphics/when-event-fschange.png)

The event _Name_ is mandatory and must be an alphanumeric string beginning with a letter or an underscore. The associated _Condition_ is also mandatory, and must be selected among the appropriate ones using the drop down list.

The items (files and directories) to be monitored can be provided by entering their path in the _Item_ fiels below the list, and then checking the _Add_ button to populate the list: the button with three dots on the right provides a convenient way to browse the filesystem and select objects. By checking the _Use button to select directories_ option, the dialog box associated with the three-dotted button will allow to choose directories, otherwise to choose files.

To remove an item, double click it on the list and then click the _Remove_ button.


## Other Event Types

Items that handle particular events, which may in many cases available for a specific host platform, are described in this [section](events_extra01.md).


## See Also

* [Event Based Conditions](cond_eventrelated.md)
* [Events](events.md)
* [Conditions](conditions.md)
* [Tasks](tasks.md)


[`◀ Main`](main.md)
