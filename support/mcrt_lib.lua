-- mcrt: multiple conditions to run a task
-- NOTE: internals have a double underscore and will not be directly
-- used in the scripts that require the library


local __MCRT_LOCK_FILE = [[{MCRT_LOCK_FILE}]]
local __MCRT_PERSIST_FILE = [[{MCRT_PERSIST_FILE}]]


-- the library itself
local mcrt = {}


-- mangle names
local function __mangle_name(name)
    return ":" .. name .. ":"
end

-- find whether or not a (mangled) name is present in a string
local function __has_name(name, s)
    return string.find(s, __mangle_name(name)) ~= nil
end

-- remove a name from a string
local function __rm_name(name, s)
    return string.gsub(s, __mangle_name(name), "")
end

-- add a name to a string
local function __add_name(name, s)
    return s .. __mangle_name(name)
end


-- test if a file exists
local function __file_exists(file)
  local f = io.open(file, "rb")
  if f then f:close() end
  return f ~= nil
end

-- wait for the lock file to disappear: unfortunately stock Lua has no
-- sleep() function, so we do busy wait here hoping that it will never be
-- useful and that the lock would last possibly a bunch of usecs at most
local function __wait_lock()
    while __file_exists(__MCRT_LOCK_FILE) do end
end

-- set and reset the lock
local function __set_lock()
    local f = io.open(__MCRT_LOCK_FILE, "wb")
    f:close()
end

local function __reset_lock()
    if __file_exists(__MCRT_LOCK_FILE) then
        os.remove(__MCRT_LOCK_FILE)
    end
end

-- read the contents of the persistent file, return nil if read failed
local function __read_persistent()
    local f = io.open(__MCRT_PERSIST_FILE, "r")
    local s = nil
    if f then
        s = f:read("*all")
        f:close()
    end
    return s
end

-- write the specified contents to the persistent file, truncate the file
-- on null content, which is useful for initialization
local function __write_persistent(content)
    local f = io.open(__MCRT_PERSIST_FILE, "w")
    if content ~= nil then
        f:write(content)
    end
    f:close()
end


-- actual library functions

-- initialize the persistent file
function mcrt.initialize()
    __wait_lock()
    __set_lock()
    __write_persistent(nil)
    __reset_lock()
end

-- set the condition bearing the provided name to verified
function mcrt.set_condition_verified(cond_name)
    __wait_lock()
    __set_lock()
    local persistent = __read_persistent()
    if persistent ~= nil then
        if not __has_name(cond_name, persistent) then
            persistent = __add_name(cond_name, persistent)
        end
    else
        persistent = __add_name(cond_name, "")
    end
    __write_persistent(persistent)
    __reset_lock()
end

-- check whether the provided conditions are all verified, and if so remove
-- their names prior to returning true; otherwise return false
function mcrt.check_conditions_verified(cond_names)
    local res = true
    __wait_lock()
    __set_lock()
    local persistent = __read_persistent()
    if persistent ~= nil then
        for _, name in ipairs(cond_names) do
            if not __has_name(name, persistent) then
                res = false
                break
            end
        end
        if res then
            for _, name in ipairs(cond_names) do
                persistent = __rm_name(name, persistent)
            end
            __write_persistent(persistent)
        end
    else
        res = false
    end
    __reset_lock()
    return res
end

-- return the library table
return mcrt


-- end.
