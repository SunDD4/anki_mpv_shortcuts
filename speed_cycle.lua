local speeds = {0.6, 0.7, 0.8, 1.0, 1.2}
local current_index = 1
local is_cycling = false
local timer = nil
local ab_loop_observer = nil
local first_cycle = true
local eof_handled = false
local speed_observer = nil
local auto_clear_ab_loop = false

function load_user_speeds()
    local user_speeds = mp.get_property_native("script-opts")
    if user_speeds and user_speeds["speed_cycle-speeds"] then
        local speed_str = user_speeds["speed_cycle-speeds"]
        local new_speeds = {}
        for speed in string.gmatch(speed_str, "([^,]+)") do
            local num = tonumber(speed)
            if num then table.insert(new_speeds, num) end
        end
        if #new_speeds > 0 then
            speeds = new_speeds
            mp.msg.info("已加载自定义倍速序列: " .. speed_str)
        end
    end
end

load_user_speeds()

function setup_global_ab_loop_monitor()
    mp.observe_property("ab-loop-a", "number", function(name, value)
        if value == -1 then
            if is_cycling then
                stop_cycling()
                mp.osd_message("AB循环被清除，停止倍速循环并恢复原速")
            elseif mp.get_property_number("speed") ~= 1.0 then
                mp.set_property_number("speed", 1.0)
                mp.osd_message("AB循环被清除，恢复原速")
            end
        end
    end)
end

setup_global_ab_loop_monitor()

local pause_observer = nil

function safe_get_property_number(name, default)
    local val = mp.get_property_number(name)
    return val ~= nil and val or default
end

function handle_ab_loop_mode(ab_a, ab_b)
    local loop_start = ab_a
    local loop_end = ab_b
    
    if loop_start > loop_end then
        loop_start, loop_end = loop_end, loop_start
        mp.osd_message(string.format("BA循环: 速度 %.1fx", speeds[current_index]), 1)
    else
        mp.osd_message(string.format("速度: %.1fx", speeds[current_index]), 1)
    end
    
    local loop_duration = loop_end - loop_start
    local current_speed = speeds[current_index]
    local time_needed = loop_duration / current_speed
    
    if timer then timer:kill() end
    
    local is_paused = mp.get_property_bool("pause")
    if not is_paused then
        timer = mp.add_timeout(time_needed, function()
            if is_cycling then
                current_index = current_index + 1
                
                if current_index > #speeds then
                    stop_cycling()
                    return
                end
                
                mp.set_property_number("time-pos", loop_start)
                cycle_speed()
            end
        end)
    end
end

function setup_eof_handler()
    if ab_loop_observer then
        mp.unobserve_property(ab_loop_observer)
        ab_loop_observer = nil
    end
    
    if current_index > 1 and not first_cycle then
        mp.set_property_number("time-pos", 0)
    end
    
    first_cycle = false
    eof_handled = false
    
    ab_loop_observer = mp.observe_property("eof-reached", "bool", function(name, value)
        if value and is_cycling and not eof_handled then
            eof_handled = true
            
            current_index = current_index + 1
            
            if current_index > #speeds then
                stop_cycling()
                return
            end
            
            mp.add_timeout(0.05, function()
                if is_cycling then
                    mp.set_property_number("time-pos", 0)
                    mp.set_property("pause", "no")
                    mp.set_property("eof-reached", "no")
                    
                    mp.add_timeout(0.05, function()
                        if is_cycling then
                            eof_handled = false
                            cycle_speed()
                        end
                    end)
                end
            end)
        end
    end)
end

function cycle_speed()
    if not is_cycling then return end
    
    local current_speed = speeds[current_index]
    if not current_speed then
        mp.msg.error("无效的倍速索引: " .. tostring(current_index))
        stop_cycling()
        return
    end
    
    mp.set_property_number("speed", current_speed)
    mp.osd_message(string.format("速度: %.1fx", current_speed), 1)
    
    local ab_a = safe_get_property_number("ab-loop-a", -1)
    local ab_b = safe_get_property_number("ab-loop-b", -1)
    local is_ab_loop = ab_a >= 0 and ab_b >= 0 and ab_a ~= ab_b
    
    if is_ab_loop then
        handle_ab_loop_mode(ab_a, ab_b)
    else
        setup_eof_handler()
    end
end

function show_cycling_status()
    if is_cycling then
        local status = string.format("倍速循环: 当前 %.1fx, 进度 %d/%d", 
                                    speeds[current_index], current_index, #speeds)
        mp.osd_message(status, 2)
    else
        mp.osd_message("倍速循环未启动", 2)
    end
end

function start_cycling()
    if is_cycling then
        stop_cycling()
        return
    end
    
    mp.set_property("keep-open", "yes")
    
    local ab_a = safe_get_property_number("ab-loop-a", -1)
    local ab_b = safe_get_property_number("ab-loop-b", -1)
    local is_ab_loop = ab_a >= 0 and ab_b >= 0 and ab_a ~= ab_b
    
    if is_ab_loop then
        local start_pos = math.min(ab_a, ab_b)
        mp.set_property_number("time-pos", start_pos)
        
        if ab_a > ab_b then
            mp.osd_message("在BA循环区间内开始倍速循环播放")
        else
            mp.osd_message("在AB循环区间内开始倍速循环播放")
        end
    else
        mp.osd_message("开始倍速循环播放")
    end
    
    is_cycling = true
    current_index = 1
    first_cycle = true
    eof_handled = false
    
    if pause_observer then
        mp.unobserve_property(pause_observer)
    end
    
    pause_observer = mp.observe_property("pause", "bool", function(name, value)
        if is_cycling then
            if value then
                if timer then
                    timer:kill()
                    timer = nil
                end
                mp.osd_message("倍速循环已暂停")
            else
                cycle_speed()
            end
        end
    end)
    
    cycle_speed()
end

function setup_speed_monitor()
    if speed_observer then
        mp.unobserve_property(speed_observer)
        speed_observer = nil
    end
    
    speed_observer = mp.observe_property("speed", "number", function(name, value)
        if value == 1.0 and auto_clear_ab_loop and not is_cycling then
            local ab_a = safe_get_property_number("ab-loop-a", -1)
            local ab_b = safe_get_property_number("ab-loop-b", -1)
            
            if ab_a >= 0 or ab_b >= 0 then
                mp.add_timeout(0.2, function()
                    mp.set_property("ab-loop-a", -1)
                    mp.set_property("ab-loop-b", -1)
                    mp.osd_message("倍速循环结束，已清除AB循环点，继续正常播放")
                    
                    auto_clear_ab_loop = false
                end)
            end
        end
    end)
end

setup_speed_monitor()

function stop_cycling()
    is_cycling = false
    if timer then
        timer:kill()
        timer = nil
    end
    
    if ab_loop_observer then
        mp.unobserve_property(ab_loop_observer)
        ab_loop_observer = nil
    end
    
    if pause_observer then
        mp.unobserve_property(pause_observer)
        pause_observer = nil
    end
    
    mp.set_property_number("speed", 1.0)
    mp.osd_message("倍速循环播放结束，已恢复原速")
end

mp.register_script_message("start_cycling", function()
    auto_clear_ab_loop = true
    start_cycling()
end)

mp.register_script_message("stop_cycling_if_active", function()
    if is_cycling then
        stop_cycling()
        mp.osd_message("已停止当前倍速循环播放")
    end
end)

mp.add_key_binding("r", "speed_cycle", start_cycling)
mp.add_key_binding("v", "speed_cycle_alt", start_cycling)
mp.add_key_binding("Alt+r", "speed_cycle_status", show_cycling_status)