# Native Tasks Editors

There are two types of base task implemented in **When** which correspond to tasks natively supported by the underlying scheduler:

* [Command](#command) based
* [Lua Script](#lua-script) based

Other, specific tasks may be added - which actually are specialized versions of the above mentioned ones.

In all editors, the task _Name_ is mandatory and must be an alphanumeric string beginning with a letter or an underscore.[^1]


## Command

Command tasks execute a command at the OS level which can be any kind of executable, that is, both scripts and binaries are accepted commands. The command, along with its arguments and startup folder, must be provided by the user.

![WhenTaskCommand](graphics/when-task-command.png)

The definition of the related command and of the tests that are performed to determine its outcome is very similar to the corresponding [condition](cond_actionrelated.md#command) definition.

Apart from the mandatory name, the following entries must be specified:

* _Command_: must either be the full path to an executable, or a command that can be found in the current execution _PATH_
* _Arguments_: the arguments, if any, to be passed to the command
* _Working Folder_: the directory where the command is started by the OS.

If the working folder is not important for command execution, a simple dot (`.`) can be entered to specify the "current folder": the field can not be empty.

The _environment variables_ deserve special consideration:

* by checking _Preserve Existing Environment_ (default, recommended) the command starts with all the already defined variables, otherwise a fresh, empty environment is created
* the _Set..._ flag, if checked, _adds_ two more variables: _WHENEVER_TASK_ holding the current task name, and _WHENEVER_CONDITION_ containing the name of the condition that triggered the task itself
* more environment variables can be defined for the specific command: for this, it is sufficient to enter the variable name and the value in the respective fields, and click the _Update_ button; to remove a variable it is sufficient to enter its name in the _Variable Name_ field (or double click the entry in the list) and then click the _Remove_ button. Clicking _Update_ by providing a new value for an existing variable will update its value in the list.

Variables provided in the list will add up to the existing ones, or _overwrite_ the ones that share the same name.

The _Checks_ section allows to test the outcome of commands by examining their output (either _stdout_ or _stderr_) or the exit code. When selecting _Success_ in the _Check for_ drop down list, meeting the criteria provided on the right will be considered a success. Selecting _Failure_ will cause the same event to be considered a failure. This especially counts when instructing conditions to stop task execution after either success or failure (see [here](conditions.md)). When _Nothing_ is selected, the outcome of the task will always be undetermined. In the same section, the flags below change the way the provided result is compared against the selected output (_stdout_ or _stderr_ only: ignored when the exit code is considered): _Exact Match_ indicates that the output is matched against the provided string in its entirety (by default it is sufficient to find the provided string as a substring), _Case Sensitive_ obviously considers uppercase and lowercase letters differently, while _Regular Expression_ considers the provided string as a regular expression to match against the command output, either in its entirety or just partially depending on whether _Exact Match_ is respectively checked or unchecked.

The _Timeout_ parameter can be set to a specified number of seconds in order to force a command which can hang or take a long time to complete to stop after the provided time. In terms of outcome, a timeout terminated command is always considered as failed. The provided value must be a positive integer, to avoid timeout checking field must be left empty.


## Lua Script

As a lightweight alternative to OS level commands, it is possible to run _Lua_ scripts: since the _Lua_ interpreter is embedded in the scheduler executable, execution of simple _Lua_ scripts may have less impact on computational resources than equivalent tasks that require commands. The interpreter is provided with its full library, and although the script has to be specified in the scheduler configuration, it is possible to use the `require()` and `dofile()` functions to call external scripts.

![WhenTaskLua](graphics/when-task-lua.png)

Success and failure of _Lua_ based tasks are determined by the correspondence of the values held by some variables after the script execution. The variables to be checked are provided by the user by entering the variable name and the expected value respectively in the _Variable Name_ and _New Value_ fields, and clicking the _Update_ button: the behavior of the list, the aforementioned fields and the _Update_ and _Remove_ buttons are similar to the ones seen for the _environment variables_ in [command based tasks](#command). Checking the _Match ALL Results_ box will cause the task to be successful only when **all** listed variables hold the expected values, while by default just one match among the listed ones is sufficient for success.

> **Note**: _Lua_ script based tasks will always _fail_ if there is an error in the provided script.


## Session Related Tasks

There are a bunch of simple session related tasks, useful for such things as turning off the computer or just locking the session under certain circumstances, that can be used with the application: more details can be found [here](tasks_extra_session.md).


## See also

* [Command Based Conditions](cond_actionrelated.md#command)
* [Lua Script Based Conditions](cond_actionrelated.md#lua-script)
* [Conditions](conditions.md)
* [Events](events.md)


[`◀ Main`](main.md)


[^1]: Names beginning with the prefix `__When__private__` are reserved, and are not allowed when creating items.
