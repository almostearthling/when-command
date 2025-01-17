# strings for internationalization

# app name
UI_APP = "When"
UI_APP_LABEL = "When Automation Tool"
UI_APP_COPYRIGHT = "© 2023-2025 Francesco Garosi"
UI_APP_VERSION = "1.9.0-beta"


# item types
ITEM_TASK = "Task"
ITEM_TASK_COMMAND = "Command Based Task"
ITEM_TASK_LUA = "Lua Script Based Task"

ITEM_COND = "Condition"
ITEM_COND_COMMAND = "Command Based Condition"
ITEM_COND_LUA = "Lua Script Based Condition"
ITEM_COND_INTERVAL = "Interval Based Condition"
ITEM_COND_IDLE = "Idle Session Based Condition"
ITEM_COND_TIME = "Time Based Condition"
ITEM_COND_DBUS = "DBus Inspection Based Condition"
ITEM_COND_EVENT = "Event Based Condition"

ITEM_EVENT = "Event"
ITEM_EVENT_FSCHANGE = "Filesystem Monitoring Based Event"
ITEM_EVENT_DBUS = "DBus Subscription Based Event"
ITEM_EVENT_CLI = "Command Based Event"


# time specifications
UI_TIME_YEARS = "years"
UI_TIME_MONTHS = "months"
UI_TIME_WEEKS = "weeks"
UI_TIME_DAYS = "days"
UI_TIME_HOURS = "hours"
UI_TIME_MINUTES = "minutes"
UI_TIME_SECONDS = "seconds"

UI_TIME_YEAR = "year"
UI_TIME_MONTH = "month"
UI_TIME_WEEK = "week"
UI_TIME_DAY = "day"
UI_TIME_DOW = "weekday"
UI_TIME_HOUR = "hour"
UI_TIME_MINUTE = "minute"
UI_TIME_SECOND = "second"

UI_TIME_YEAR_SC = "Year:"
UI_TIME_MONTH_SC = "Month:"
UI_TIME_WEEK_SC = "Week:"
UI_TIME_DAY_SC = "Day:"
UI_TIME_DOW_SC = "Weekday:"
UI_TIME_HOUR_SC = "Hour:"
UI_TIME_MINUTE_SC = "Minute:"
UI_TIME_SECOND_SC = "Second:"

UI_DOW_MON = "Monday"
UI_DOW_TUE = "Tuesday"
UI_DOW_WED = "Wednesday"
UI_DOW_THU = "Thursday"
UI_DOW_FRI = "Friday"
UI_DOW_SAT = "Saturday"
UI_DOW_SUN = "Sunday"

UI_MON_JAN = "January"
UI_MON_FEB = "February"
UI_MON_MAR = "March"
UI_MON_APR = "April"
UI_MON_MAY = "May"
UI_MON_JUN = "June"
UI_MON_JUL = "July"
UI_MON_AUG = "August"
UI_MON_SEP = "September"
UI_MON_OCT = "October"
UI_MON_NOV = "November"
UI_MON_DEC = "December"

UI_STR_UNKNOWN = "<unknown>"

UI_TIMESPEC_MIDNIGHT = "midnight"
UI_TIMESPEC_NOON = "noon"
UI_TIMEFORMAT_ATFULLTIME = "at {hour:02}:{minute:02}:{second:02}"
UI_TIMEFORMAT_ATHOURMIN = "at {hour:02}:{minute:02}"
UI_TIMEFORMAT_ATHOUR = "at {hour} o'clock"
UI_TIMEFORMAT_ATMINSEC = "every hour at {minute}m {second}s"
UI_TIMEFORMAT_ATMIN = "every hour at {minute}m"
UI_TIMEFORMAT_ATSEC = "every minute at {second}s"
UI_TIMEFORMAT_ATHOURSEC = "at {hour} o'clock plus {second} seconds"
UI_TIMEFORMAT_ONFULLDATE = "on {year}/{month:02}/{day:02}"
UI_TIMEFORMAT_ONMONTHDAY = "on day {day} of {month}"
UI_TIMEFORMAT_ONDAY = "on day {day} of every month"
UI_TIMEFORMAT_ONWEEKDAY = "on {weekday}"
UI_TIMEFORMAT_ANY_YEAR = "ANY_YEAR"
UI_TIMEFORMAT_ANY_MONTH = "ANY_MONTH"
UI_TIMEFORMAT_ANY_DAY = "ANY_DAY"
UI_TIMEFORMAT_ANY_WEEKDAY = "ANY_WEEKDAY"
UI_TIMEFORMAT_ANY_HOUR = "ANY_HOUR"
UI_TIMEFORMAT_ANY_MINUTE = "ANY_MINUTE"
UI_TIMEFORMAT_ANY_SECOND = "ANY_SECOND"

UI_OUTCOME_NONE = "Nothing"
UI_OUTCOME_SUCCESS = "Success"
UI_OUTCOME_FAILURE = "Failure"

# streams
UI_STREAM_STDIN = "Standard input"
UI_STREAM_STDOUT = "Standard output"
UI_STREAM_STDERR = "Standard error"
UI_EXIT_CODE = "Exit code"

# common buttons
UI_OK = "OK"
UI_CANCEL = "Cancel"
UI_EXIT = "Exit"
UI_NEW = "New..."
UI_EDIT = "Edit..."
UI_BROWSE = "..."
UI_BROWSEFILE = "File..."
UI_BROWSEFOLDER = "Folder..."
UI_ADD = "Add"
UI_DEL = "Remove"
UI_CLEAR = "Clear"
UI_CLEARALL = "Clear all"
UI_UPDATE = "Update"
UI_LOAD = "Reload"
UI_SAVE = "Save"

# form captions
UI_FORM_TASK = "Task"
UI_FORM_TASKS = "Tasks"
UI_FORM_CONDITION = "Condition"
UI_FORM_CONDITIONS = "Conditions"
UI_FORM_EVENT = "Event"
UI_FORM_EVENTS = "Events"
UI_FORM_ITEM = "Item"
UI_FORM_ITEMS = "Items"

UI_FORM_COMMON_PARAMS = "Common parameters"
UI_FORM_SPECIFIC_PARAMS = "Specific parameters"

UI_FORM_ENVIRONMENT = "Environment"
UI_FORM_VARIABLE = "Variable"
UI_FORM_FILE = "File"
UI_FORM_NAME = "Name"
UI_FORM_VALUE = "Value"
UI_FORM_VARNAME = "Variable name"
UI_FORM_VARVALUE = "Variable value"
UI_FORM_TYPE = "Type"
UI_FORM_GLOBALS = "Globals"
UI_FORM_ITEMS = "Items"
UI_FORM_CHECKS = "Checks"
UI_FORM_TESTVAL = "Test value"
UI_FORM_SCRIPT = "Script"
UI_FORM_COMMAND = "Command"
UI_FORM_SEQUENCE = "Sequence"

UI_FORM_HS_TIME = "Time"
UI_FORM_HS_TASK = "Task"
UI_FORM_HS_TRIGGER = "Triggered by"
UI_FORM_HS_DURATION = "Duration"
UI_FORM_HS_SUCCESS = "OK"
UI_FORM_HS_MESSAGE = "Message"

UI_FORM_ITEMTYPE = "Choose item type"
UI_FORM_ITEMSUBTYPES = "Available items"

UI_FORM_NAME_SC = "Name:"
UI_FORM_PATH_SC = "Location:"
UI_FORM_ARGS_SC = "Arguments:"
UI_FORM_TASK_SC = "Task:"
UI_FORM_COND_SC = "Condition:"
UI_FORM_EVENT_SC = "Event:"
UI_FORM_COMMAND_SC = "Command:"
UI_FORM_STARTUPPATH_SC = "Working folder:"
UI_FORM_VARIABLES_SC = "Variables:"
UI_FORM_VALUES_SC = "Values:"
UI_FORM_RESULTS_SC = "Results:"
UI_FORM_ACTIVETASKS_SC = "Active tasks:"
UI_FORM_TICKINTERVAL_SC = "Tick interval:"
UI_FORM_CURRENTITEMS_SC = "Current items:"
UI_FORM_VARNAME_SC = "Variable name:"
UI_FORM_NEWVALUE_SC = "New value:"
UI_FORM_CHECKFOR_SC = "Check for:"
UI_FORM_CHECKAGAINST_SC = "Check against:"
UI_FORM_TESTVAL_SC = "Test value:"
UI_FORM_TIMEOUTSECS_SC = "Timeout (s):"
UI_FORM_DATE_SC = "Date:"
UI_FORM_TIME_SC = "Time:"
UI_FORM_DOW_SC = "Weekday:"
UI_FORM_ITEM_SC = "Item:"
UI_FORM_CURRENTTIMESPECS_SC = "Active time specifications:"
UI_FORM_MONITOREDFSITEMS_SC = "Monitored filesystem items:"
UI_FORM_HISTORYITEMS_SC = "Current history:"
UI_FORM_EXTRADELAY_SC = "Additional delay:"
UI_FORM_DBUS_BUS_SC = "Bus:"
UI_FORM_DBUS_SERVICE_SC = "Service:"
UI_FORM_DBUS_OBJPATH_SC = "Object path:"
UI_FORM_DBUS_INTERFACE_SC = "Interface:"
UI_FORM_DBUS_METHOD_SC = "Method:"
UI_FORM_DBUS_SIGNAL_SC = "Signal:"
UI_FORM_DBUS_PARAMS_CALL_SC = "Call with the following parameters (use JSON format):"
UI_FORM_DBUS_PARAMS_CHECK_SC = "Perform the following checks on return values (use JSON format):"
UI_FORM_ITEMTYPE_SC = "Choose item type:"
UI_FORM_ITEMSUBTYPES_SC = "Available items:"

UI_FORM_RANDCHECKSINTICKS = "Randomize checks within ticks"
UI_FORM_CHECKCONDRECURRENT = "Check condition recurrently"
UI_FORM_SUSPENDCONDATSTARTUP = "Suspend condition at startup"
UI_FORM_RUNTASKSSEQUENTIALLY = "Execute tasks sequentially"
UI_FORM_BREAKONFAILURE = "Stop running sequence when a task fails"
UI_FORM_BREAKONSUCCESS = "Stop running sequence when a task succeeds"
UI_FORM_BREAKNEVER = "Do not check for task outcome"
UI_FORM_PRESERVEENVIRONMENT = "Preserve existing environment"
UI_FORM_SETWENVIRONMENT = "Set WHENEVER environment variables"
UI_FORM_MATCHEXACT = "Exact match"
UI_FORM_MATCHREGEXP = "Regular expression"
UI_FORM_CASESENSITIVE = "Case sensitive"
UI_FORM_IDLE = "Idle time"
UI_FORM_EVENT = "Event"
UI_FORM_IDLEDURATION = "Idle session duration"
UI_FORM_DELAY = "Delay"
UI_FORM_DELAYSPEC = "Interval duration"
UI_FORM_EXTRADELAY = "Additional delay"
UI_FORM_EXTRADELAYSPEC = "Check/recheck after"
UI_FORM_TIMESPECS = "Time specifications"
UI_FORM_EXPECTRESULTS = "Expected results"
UI_FORM_MATCHALLRESULTS = "Match ALL results"
UI_FORM_RECURSIVE = "Recursively scan directories"
UI_FORM_OR = "or"


# form titles
UI_TITLE_NEWITEM = "%s: Choose New Item" % UI_APP

UI_TITLE_COMMANDTASK = "%s: Command Task Editor" % UI_APP
UI_TITLE_LUATASK = "%s: Lua Script Task Editor" % UI_APP

UI_TITLE_COMMANDCOND = "%s: Command Condition Editor" % UI_APP
UI_TITLE_LUACOND = "%s: Lua Script Condition Editor" % UI_APP
UI_TITLE_INTERVALCOND = "%s: Interval Condition Editor" % UI_APP
UI_TITLE_IDLECOND = "%s: Idle Session Condition Editor" % UI_APP
UI_TITLE_EVENTCOND = "%s: Event Condition Editor" % UI_APP
UI_TITLE_TIMECOND = "%s: Time Condition Editor" % UI_APP
UI_TITLE_DBUSCOND = "%s: DBus Method Condition Editor" % UI_APP

UI_TITLE_DBUSEVENT = "%s: DBus Signal Event Editor" % UI_APP
UI_TITLE_FSCHANGEEVENT = "%s: Filesystem Monitoring Event Editor" % UI_APP
UI_TITLE_CLIEVENT = "%s: Direct Command Event Editor" % UI_APP

UI_TITLE_HISTORY = "%s: Task History" % UI_APP
UI_TITLE_MENU = "%s: Menu" % UI_APP

UI_CAPTION_NOSPECIFICPARAMS = "This type of item does not require any specific parameter"
UI_CAPTION_NOTSUPPORTED = "This type of item is not supported"


# popup titles and messages
UI_POPUP_T_ERR = "Error"
UI_POPUP_T_WARN = "Warning"
UI_POPUP_T_INFO = "Information"
UI_POPUP_T_CONFIRM = "Confirmation required"
UI_POPUP_T_ASK = "Question"

UI_POPUP_DISCARDCONFIG_Q = "Discard current configuration?"
UI_POPUP_OVERWRITEFILE_Q = "Do you want to overwrite the specified file?"
UI_POPUP_DELETEITEM_Q = "Do you want delete the selected item?"
UI_POPUP_DELETETSPECS_Q = "Do you want to delete all the time specifications?"
UI_POPUP_RELOADCONFIG_Q = "Do you want to reload the configuration?"

UI_POPUP_FILENOTFOUND_ERR = "The specified file could not be found"
UI_POPUP_NOEVENTCONDITIONS_ERR = "There are no event based conditions that can be associated"

UI_POPUP_UNKNOWNERROR = "An unknown error occurred"
UI_POPUP_INVALIDITEMNAME = "Item name is not valid"
UI_POPUP_INVALIDPARAMETERS_T = "Some of the form fields contain invalid data:\n\n%s\n\nPlease review them before updating"
UI_POPUP_INVALIDVARNAME = "Invalid name for variable"
UI_POPUP_EMPTYVARVALUE = "No value provided for variable"
UI_POPUP_INVALIDFILEORDIR = "Invalid file or directory name"
UI_POPUP_INVALIDTIMESPEC = "Invalid or missing time specification"
UI_POPUP_REFERENCEDTASK = "The Task is still referenced in at least\none Condition: remove any references\nbefore attempting to delete it"
UI_POPUP_REFERENCEDCOND = "The Condition is still referenced in at least\none Event: remove any references before\nattempting to delete it"
UI_POPUP_MISSINGEVENTCOND = "No condition specified for event"


# about box
UI_ABOUT_TITLE = "About"
UI_ABOUT_WHENEVER_VERSION = "Scheduler version:"
UI_ABOUT_TEXT = """\
%s

Configuration utility and wrapper for the Whenever
scheduler designed to help running and controlling
the automation tool in a desktop environment.

%s
""" % (UI_APP, UI_APP_COPYRIGHT)


# tray icon menu entries
UI_TRAY_MENU_ABOUT = "About..."
UI_TRAY_MENU_EXIT = "Exit"
UI_TRAY_MENU_PAUSESCHEDULER = "Pause scheduler"
UI_TRAY_MENU_RESUMESCHEDULER = "Resume scheduler"
UI_TRAY_MENU_RESETCONDITIONS = "Reset conditions"
UI_TRAY_MENU_HISTORY = "Show history..."
UI_TRAY_MENU_CONFIGURE = "Configurator..."


# file type labels for Open File dialogs
UI_FILETYPE_EXECUTABLES = "Executable files"


# symbols
SYM_OK = "✓"
SYM_FAIL = "✕"
SYM_UNKNOWN = "∅"


# CLI strings
CLI_APP_DESCRIPTION = "Automation tool for desktop environments"
CLI_APP_HELP_EPILOG = "Please refer to the application GitHub page for more details."

CLI_ARG_HELP_COMMAND = "Desired action"
CLI_ARG_HELP_DIR_APPDATA = "Use a custom application data and configuration directory"
CLI_ARG_HELP_LOG = "Specify a custom path for the log file (applies to: start)"
CLI_ARG_HELP_LOGLEVEL = "Specify the log level (applies to: start)"
CLI_ARG_HELP_WHENEVER = "Path to a specific `whenever` executable"

CLI_ERR_WHENEVER_NOT_FOUND = "Executable for `whenever` not found or invalid"
CLI_ERR_DATADIR_UNACCESSIBLE = "The data directory could neither be found nor created"
CLI_ERR_CONFIG_UNACCESSIBLE = "The `whenever` configuration file could neither be found nor created"
CLI_ERR_ALREADY_RUNNING = "Another instance of the scheduler is running: cannot start"


# default strings for standard buttons
BTN_OK = "OK"
BTN_CANCEL = "Cancel"
BTN_CLOSE = "Close"
BTN_EXIT = "Exit"
BTN_QUIT = "Quit"
BTN_ADD = "Add"
BTN_REMOVE = "Remove"
BTN_DELETE = "Delete"
BTN_SAVE = "Save"
BTN_LOAD = "Load"
BTN_NEW = "New"
BTN_EDIT = "Edit"
BTN_MODIFY = "Modify"
BTN_RELOAD = "Reload"
BTN_RESET = "Reset"

BTN_FILE_D = "File..."
BTN_FOLDER_D = "Folder..."

BTN_CONFIG_D = "Configure..."
BTN_ABOUT_D = "About..."
BTN_PAUSE = "Pause scheduler"
BTN_RESUME = "Resume scheduler"
BTN_RESETCONDS = "Reset conditions"
BTN_HISTORY_D = "Show history..."


# new UI strings
CONFIGFORM_LBL_FILELOCATION_SC = "File:"
CONFIGFORM_LBL_ITEMS_SC = "Items:"
CONFIGFORM_LBL_RANDOMCHECKS = "Randomize checks between ticks"
CONFIGFORM_LBL_TICKDURATION_SC = "Seconds per tick:"
CONFIGFORM_LHD_NAME = "Name"
CONFIGFORM_LHD_TYPE = "Item Type"


# end.
