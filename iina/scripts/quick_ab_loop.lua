-- 快速AB循环脚本
local utils = require 'mp.utils'

function set_quick_ab_loop(duration)
    mp.commandv("script-message-to", "speed_cycle", "stop_cycling_if_active")
    
    mp.add_timeout(0.1, function()
        mp.set_property("ab-loop-a", -1)
        mp.set_property("ab-loop-b", -1)
        
        mp.set_property_number("speed", 1.0)
        mp.osd_message("已重置播放状态，准备开始新的快速AB循环")
        
        mp.add_timeout(0.2, function()
            setup_ab_loop(duration)
        end)
    end)
end

function set_custom_ab_loop(duration, offset)
    mp.commandv("script-message-to", "speed_cycle", "stop_cycling_if_active")
    
    mp.add_timeout(0.1, function()
        mp.set_property("ab-loop-a", -1)
        mp.set_property("ab-loop-b", -1)
        
        mp.set_property_number("speed", 1.0)
        mp.osd_message("已重置播放状态，准备开始新的自定义AB循环")
        
        mp.add_timeout(0.2, function()
            setup_custom_ab_loop(duration, offset)
        end)
    end)
end

function setup_ab_loop(duration)
    local current_pos = mp.get_property_number("time-pos")
    if not current_pos then
        mp.osd_message("无法获取当前播放位置")
        return
    end
    
    local a_pos = current_pos - 0.3
    
    if a_pos < 0 then
        a_pos = 0
    end
    
    mp.set_property("ab-loop-a", a_pos)
    mp.osd_message(string.format("已设置A点: %.2f秒", a_pos))
    
    local b_pos = a_pos + duration
    
    local duration_total = mp.get_property_number("duration")
    
    if duration_total and b_pos > duration_total then
        b_pos = duration_total
    end
    
    mp.add_timeout(0.1, function()
        mp.set_property("ab-loop-b", b_pos)
        mp.osd_message(string.format("已设置AB循环: %.2f秒 - %.2f秒", a_pos, b_pos))
        
        mp.add_timeout(0.2, function()
            mp.commandv("script-message-to", "speed_cycle", "start_cycling")
        end)
    end)
end

function setup_custom_ab_loop(duration, offset)
    local current_pos = mp.get_property_number("time-pos")
    if not current_pos then
        mp.osd_message("无法获取当前播放位置")
        return
    end
    
    local a_pos = current_pos - offset
    
    if a_pos < 0 then
        a_pos = 0
    end
    
    mp.set_property("ab-loop-a", a_pos)
    mp.osd_message(string.format("已设置A点: %.2f秒", a_pos))
    
    local b_pos = a_pos + duration
    
    local duration_total = mp.get_property_number("duration")
    
    if duration_total and b_pos > duration_total then
        b_pos = duration_total
    end
    
    mp.add_timeout(0.1, function()
        mp.set_property("ab-loop-b", b_pos)
        mp.osd_message(string.format("已设置AB循环: %.2f秒 - %.2f秒", a_pos, b_pos))
        
        mp.add_timeout(0.2, function()
            mp.commandv("script-message-to", "speed_cycle", "start_cycling")
        end)
    end)
end

mp.register_script_message("set_quick_ab_loop", function(duration_str)
    local duration = tonumber(duration_str) or 2
    set_quick_ab_loop(duration)
end)

mp.register_script_message("set_custom_ab_loop", function(duration_str, offset_str)
    local duration = tonumber(duration_str) or 2.5
    local offset = tonumber(offset_str) or 3.5
    set_custom_ab_loop(duration, offset)
end)