-- mcrt: multiple conditions to run a task
-- NOTE: internals have a double underscore and will not be directly
-- used in the scripts that require the library


local __MCRT_LOCK = [[{MCRT_SHAREDSTATE_LOCK}]]
local __MCRT_PERSIST = [[{MCRT_SHAREDSTATE_PERSIST}]]


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


-- actual library functions

-- initialization just resets the shared state
function mcrt.initialize()
    if sync.lock(__MCRT_LOCK, 1.0) then
        local ok, msg = pcall(function()
            local sst = { }
            sst.persistent = ""
            sharedstate.save(__MCRT_PERSIST, sst)
        end)
        if not ok then
            log.debug("the following error occurred: " .. (msg or "<unknown>"))
            res = false
        end
        sync.release(__MCRT_LOCK)
        return res
    else
        log.debug("could not acquire shared state for condition confluence")
        return false
    end

-- set the condition bearing the provided name to verified
function mcrt.set_condition_verified(cond_name)
    if sync.lock(__MCRT_LOCK, 1.0) then
        local ok, msg = pcall(function()
            local sst = sharedstate.load(__MCRT_PERSIST)
            local persistent = sst.persistent
            if persistent ~= nil then
                if not __has_name(cond_name, persistent) then
                    persistent = __add_name(cond_name, persistent)
                end
            else
                persistent = __add_name(cond_name, "")
            end
            sst.persistent = persistent
            sharedstate.save(__MCRT_PERSIST, sst)
        end)
        if not ok then
            log.debug("the following error occurred: " .. (msg or "<unknown>"))
            res = false
        end
        sync.release(__MCRT_LOCK)
        return res
    else
        log.debug("could not acquire shared state for condition confluence")
        return false
    end
end

-- check whether the provided conditions are all verified, and if so remove
-- their names prior to returning true; otherwise return false
function mcrt.check_conditions_verified(cond_names)
    if sync.lock(__MCRT_LOCK, 1.0) then
        res = true
        local ok, msg = pcall(function()
            local sst = sharedstate.load(__MCRT_PERSIST)
            local persistent = sst.persistent
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
                    sst.persistent = persistent
                    sharedstate.save(__MCRT_PERSIST, sst)
                end
            else
                res = false
            end
        end)
        if not ok then
            log.debug("the following error occurred: " .. (msg or "<unknown>"))
            res = false
        end
        sync.release(__MCRT_LOCK)
        return res
    else
        log.debug("could not acquire shared state for condition confluence")
        return false
    end
end

-- return the library table
return mcrt


-- end.
