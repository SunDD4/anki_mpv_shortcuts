# MPV脚本模块 - 包含Lua脚本生成功能
from aqt.utils import tooltip

def create_speed_cycle_script(script_path):
    script_content = """-- 倍速循环播放脚本
-- 按r键循环切换播放速度

-- 添加配置选项
local options = {
    show_osd = true  -- 默认显示OSD
}
mp.options = require 'mp.options'
mp.options.read_options(options, "speed_cycle")

local speeds = {0.5, 0.7, 1.0, 1.3, 1.5, 2.0}
local current_index = 3  -- 默认从1.0x开始

-- 重写osd_message函数，在禁用OSD时不显示任何内容
local original_osd_message = mp.osd_message
mp.osd_message = function(text, duration, level)
    if options.show_osd then
        original_osd_message(text, duration, level)
    else
        -- 不显示任何OSD消息
        print(text) -- 仅输出到控制台
    end
end

function start_cycling()
    current_index = current_index + 1
    if current_index > #speeds then
        current_index = 1
    end
    
    local speed = speeds[current_index]
    mp.set_property("speed", speed)
    
    -- 使用修改后的osd_message函数
    mp.osd_message("速度: " .. speed .. "x", 1)
end

mp.add_key_binding("r", "speed_cycle", start_cycling)
mp.add_key_binding("v", "speed_cycle_alt", start_cycling)
"""
    
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        return True
    except Exception as e:
        from aqt.utils import tooltip
        tooltip(f"创建倍速循环脚本失败: {str(e)}")
        return False

def create_quick_ab_loop_script(script_path):
    script_content = """-- 快速AB循环脚本
-- 按x键设置自定义AB循环

-- 添加配置选项
local options = {
    show_osd = true  -- 默认显示OSD
}
mp.options = require 'mp.options'
mp.options.read_options(options, "quick_ab_loop")

-- 重写osd_message函数，在禁用OSD时不显示任何内容
local original_osd_message = mp.osd_message
mp.osd_message = function(text, duration, level)
    if options.show_osd then
        original_osd_message(text, duration, level)
    else
        -- 不显示任何OSD消息
        print(text) -- 仅输出到控制台
    end
end

function set_custom_ab_loop(duration, offset)
    local current_pos = mp.get_property_number("time-pos")
    if not current_pos then return end
    
    local a_point = current_pos - offset
    local b_point = a_point + duration
    
    mp.set_property("ab-loop-a", a_point)
    mp.set_property("ab-loop-b", b_point)
    mp.set_property("loop", "inf")
    
    -- 使用修改后的osd_message函数
    mp.osd_message("已设置AB循环点。继续正常播放↓", 1)
end

mp.register_script_message("set_custom_ab_loop", set_custom_ab_loop)
"""
    
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        return True
    except Exception as e:
        from aqt.utils import tooltip
        tooltip(f"创建快速AB循环脚本失败: {str(e)}")
        return False