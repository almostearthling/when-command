-- Utilities to change the version string in a second file according to the
-- version found in a certain file: the syntax of the two files must comply
-- to the "common sense", that is, in both files the variable definition
-- should be in the following form:
--
--  VERSION_VAR = "version_string"
--
-- whiich yelds in most scripting languages and in TOML, with the notable
-- exception of the UNIX shell.
--
-- This script should be installed in $APPDATA/lua/updatevar to be loaded.

-- join two path elements
function os_join(a, b)
    sep = package.config:sub(1,1)
    s = a .. sep .. b
    s = string.gsub(s, sep .. sep, sep)
    return s
end

-- retrieve version
function get_version(source_var, source_file)
    to_find = source_var .. " = "
    f = io.open(source_file, "r")
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
function rewrite_file(ver, dest_var, dest_file)
    line_start = dest_var .. " = "
    pattern = dest_var .. "% %=% "
    res = ""
    f = io.open(dest_file, "r")
    l = f:read("*line")
    ret = false
    while l do
        if string.find(l, "^" .. pattern) then
            res = res .. line_start .. ver .. "\n"
            ret = true
        else
            res = res .. l .. "\n"
        end
        l = f:read("*line")
    end
    io.close(f)
    f = io.open(dest_file, "w")
    f:write(res)
    io.close(f)
    return ret
end

