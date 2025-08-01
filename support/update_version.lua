-- update version script

-- Update version string in strings.py according to value in pyproject.toml:
-- this script can be used in a When filesystem monitoring event, specifically
-- watching the pyproject.toml file, so that modifying its version string in
-- the `version` line, automatically synchronizes the value in strings.py too;
-- copy the text in this file to the code box, and update the parameters
-- according to the current setup.
--
-- NOTE: the updatever.lua script must be copied to a subdirectory of the
--       application data (APPDATA) directory, that is APPDATA/lua/updatever
--       (APPDATA\Lua\updatever on Windows), which has to be created.

require "updatever"

-- parameters
startup_dir = "/path/to/repository/of/when-command"
project_file = "pyproject.toml"
strings_module = "lib/i18n/strings.py"

-- the following should be left untouched
project_var = "version"
strings_var = "UI_APP_VERSION"


-- calculate paths
source_path = os_join(startup_dir, project_file)
dest_path = os_join(startup_dir, strings_module)
version = get_version(project_var, source_path)

-- the `res` value can be tested
res = rewrite_file(version, strings_var, dest_path)

-- end.
