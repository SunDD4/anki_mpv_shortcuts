# MPV脚本模块 - 包含Lua脚本生成功能
from aqt.utils import tooltip

def create_speed_cycle_script(script_path):
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("""-- 倍速循环播放脚本
local speeds = {0.7, 0.8, 1.0, 1.2}
local current_index = 1
local is_cycling = false
local timer = nil

function cycle_speed()
    if not is_cycling then return end
    mp.set_property_number("speed", speeds[current_index])
    mp.osd_message(string.format("播放速度: %.1fx", speeds[current_index]))
    current_index = current_index + 1
    if current_index > #speeds then
        stop_cycling()
        return
    end
    local remaining = mp.get_property_number("time-remaining")
    if timer then timer:kill() end
    timer = mp.add_timeout(remaining, cycle_speed)
end

function start_cycling()
    if is_cycling then
        stop_cycling()
        return
    end
    is_cycling = true
    current_index = 1
    mp.set_property("keep-open", "yes")
    mp.osd_message("开始倍速循环播放")
    cycle_speed()
end

function stop_cycling()
    is_cycling = false
    if timer then
        timer:kill()
        timer = nil
    end
    mp.set_property("keep-open", "no")
    mp.osd_message("倍速循环播放结束")
end

mp.add_key_binding("r", "speed_cycle", start_cycling)
mp.add_key_binding("v", "speed_cycle_alt", start_cycling)
mp.register_script_message("start_cycling", start_cycling)
mp.register_script_message("stop_cycling_if_active", function()
    if is_cycling then stop_cycling() end
end)
""")
        return True
    except Exception as e:
        tooltip(f"创建倍速循环脚本失败: {str(e)}")
        return False

def create_quick_ab_loop_script(script_path):
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("""-- 快速AB循环脚本
local utils = require 'mp.utils'

function set_quick_ab_loop(duration, offset)
    mp.commandv("script-message-to", "speed_cycle", "stop_cycling_if_active")
    
    mp.add_timeout(0.1, function()
        mp.set_property("ab-loop-a", -1)
        mp.set_property("ab-loop-b", -1)
        
        mp.set_property_number("speed", 1.0)
        mp.osd_message("已重置播放状态，准备开始新的AB循环")
        
        mp.add_timeout(0.2, function()
            setup_custom_ab_loop(duration, offset)
        end)
    end)
end

function set_custom_ab_loop(duration, offset)
    mp.commandv("script-message-to", "speed_cycle", "stop_cycling_if_active")
    
    mp.add_timeout(0.1, function()
        mp.set_property("ab-loop-a", -1)
        mp.set_property("ab-loop-b", -1)
        
        mp.set_property_number("speed", 1.0)
        mp.osd_message("已重置播放状态，准备开始新的AB循环")
        
        mp.add_timeout(0.2, function()
            setup_custom_ab_loop(duration, offset)
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
    
    -- 根据偏移值显示不同的消息
    if offset < 0 then
        mp.osd_message(string.format("已设置A点: %.2f秒 (右偏%.1f秒)", a_pos, math.abs(offset)))
    else
        mp.osd_message(string.format("已设置A点: %.2f秒", a_pos))
    end
    
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

mp.register_script_message("set_quick_ab_loop", function(duration_str, offset_str)
    local duration = tonumber(duration_str) or 3.0
    local offset = tonumber(offset_str) or 1.5
    set_quick_ab_loop(duration, offset)
end)

mp.register_script_message("set_custom_ab_loop", function(duration_str, offset_str)
    local duration = tonumber(duration_str) or 2.5
    local offset = tonumber(offset_str) or 2.7
    set_custom_ab_loop(duration, offset)
end)
""")
        return True
    except Exception as e:
        tooltip(f"创建快速AB循环脚本失败: {str(e)}")
        return False