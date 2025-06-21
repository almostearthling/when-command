-- update version string in strings.py according to value in pyproject.toml:
-- this script can be used in a When filesystem monitoring event, specifically
-- watching the pyproject.toml file, so that modifying its version string in
-- the `version` line, automatically synchronizes the value in strings.py too;
-- copy the text in this file to the code box, and update the parameters

-- parameters

startup_dir = "/path/to/repository/of/when-command"
project_file = "pyproject.toml"
strings_module = "lib/i18n/strings.py"

project_var = "version"
dest_var = "UI_APP_VERSION"

-- utility functions
function os_sep()
    o = os.getenv("HOME")
    if o == nil or string.find(o, "\\") then
        return "\\"
    else
        return "/"
    end
end

function os_join(a, b)
    sep = os_sep()
    s = a .. sep .. b
    s = string.gsub(s, sep .. sep, sep)
    return s
end


-- retrieve version
function get_version()
    to_find = project_var .. " = "
    f = io.open(os_join(startup_dir, project_file), "r")
    while true do
        line = f:read("*line")
        if line == nil then break end
        if string.find(line, "^" .. to_find) then
            v = string.gsub(line, to_find, "")
            return v
        end
    end
    return nil
end


-- change the file
function rewrite_file()
    line_start = dest_var .. " = "
    pattern = dest_var .. "% %=% "
    ver = get_version()
    if ver == nil then return false end
    path = os_join(startup_dir, strings_module)
    res = ""
    f = io.open(path, "r")
    l = f:read("*line")
    while l do
        if string.find(l, "^" .. pattern) then
            res = res .. line_start .. ver .. "\n"
        else
            res = res .. l .. "\n"
        end
        l = f:read("*line")
    end
    io.close(f)
    f = io.open(path, "w")
    f:write(res)
    io.close(f)
    return true
end


-- the `res` value can be tested
res = rewrite_file()

-- end.
