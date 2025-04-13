-- 字幕AB循环增速播放脚本
-- 按r键以当前字幕为范围进行AB循环增速播放
-- 按f键以当前字幕为范围进行AB循环播放(不改变速度)
-- 按g键创建跨字幕AB循环(第一次按g标记A点，第二次按g标记B点，第三次按g退出循环)

local options = {
    show_osd = true,  -- 默认显示OSD
    speeds = { 0.7, 0.8, 1.0, 1.2, 1.5},  -- 循环播放的速度
    repeat_times = 1  -- 每个速度重复的次数
}

mp.options = require 'mp.options'
mp.options.read_options(options, "subtitle_speed_cycle")

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

local is_cycling = false
local is_simple_looping = false
local is_cross_subtitle_looping = false
local cross_subtitle_state = 0  -- 0: 未开始, 1: 已设置A点, 2: 已设置AB循环
local original_speed = 1.0
local current_speed_index = 1
local repeat_count = 0
local timer = nil

-- 获取当前字幕的开始和结束时间
function get_current_subtitle_times()
    local sub_text = mp.get_property("sub-text")
    if not sub_text or sub_text == "" then
        mp.osd_message("当前没有字幕", 2)
        return nil, nil
    end
    
    local sub_start = mp.get_property_number("sub-start")
    local sub_end = mp.get_property_number("sub-end")
    
    if not sub_start or not sub_end then
        mp.osd_message("无法获取字幕时间", 2)
        return nil, nil
    end
    
    return sub_start, sub_end
end

-- 停止循环播放
function stop_cycling()
    if not is_cycling then return end
    
    -- 停止定时器
    if timer then
        timer:kill()
        timer = nil
    end
    
    -- 恢复原始播放速度
    mp.set_property("speed", original_speed)
    
    -- 清除AB循环点
    mp.set_property("ab-loop-a", "no")
    mp.set_property("ab-loop-b", "no")
    mp.set_property("loop", "no")
    
    is_cycling = false
    mp.osd_message("退出字幕AB循环", 1)
end

-- 停止简单循环播放
function stop_simple_looping()
    if not is_simple_looping then return end
    
    -- 清除AB循环点
    mp.set_property("ab-loop-a", "no")
    mp.set_property("ab-loop-b", "no")
    mp.set_property("loop", "no")
    
    is_simple_looping = false
    mp.osd_message("退出字幕AB循环", 1)
end

-- 停止跨字幕循环播放
function stop_cross_subtitle_looping()
    if not is_cross_subtitle_looping then return end
    
    -- 清除AB循环点
    mp.set_property("ab-loop-a", "no")
    mp.set_property("ab-loop-b", "no")
    mp.set_property("loop", "no")
    
    is_cross_subtitle_looping = false
    cross_subtitle_state = 0
    mp.osd_message("退出跨字幕AB循环", 1)
end

-- 检查是否需要切换速度或结束循环
function check_loop_end()
    if not is_cycling then return end
    
    local pos = mp.get_property_number("time-pos")
    local loop_b = mp.get_property_number("ab-loop-b")
    
    -- 如果接近循环结束点，增加重复计数
    if loop_b and pos and (loop_b - pos < 0.2) then
        repeat_count = repeat_count + 1
        
        -- 如果当前速度已重复足够次数，切换到下一个速度
        if repeat_count >= options.repeat_times then
            current_speed_index = current_speed_index + 1
            repeat_count = 0
            
            -- 如果所有速度都已循环完毕，结束循环
            if current_speed_index > #options.speeds then
                stop_cycling()
                return
            end
            
            -- 设置新的速度
            local speed = options.speeds[current_speed_index]
            mp.set_property("speed", speed)
            mp.osd_message("字幕AB循环: " .. speed .. "x", 1)
            
            -- 跳转到字幕开始位置
            local loop_a = mp.get_property_number("ab-loop-a")
            if loop_a then
                mp.set_property("time-pos", loop_a)
            end
        end
    end
end

-- 开始字幕AB循环增速播放
function start_subtitle_speed_cycling()
    -- 添加调试信息
    print("尝试启动字幕AB循环")
    mp.osd_message("尝试启动字幕AB循环", 1)
    
    if is_cycling then
        stop_cycling()
        return
    end
    
    -- 如果正在简单循环，先停止
    if is_simple_looping then
        stop_simple_looping()
    end
    
    -- 如果正在跨字幕循环，先停止并确保完全重置状态
    if is_cross_subtitle_looping then
        stop_cross_subtitle_looping()
        -- 确保AB循环点被完全清除
        mp.set_property("ab-loop-a", "no")
        mp.set_property("ab-loop-b", "no")
    end
    
    -- 获取当前字幕时间，确保重新获取正确的时间范围
    local sub_start, sub_end = get_current_subtitle_times()
    if not sub_start or not sub_end then 
        mp.osd_message("无法获取字幕时间范围", 2)
        return 
    end
    
    -- 保存原始播放速度
    original_speed = mp.get_property_number("speed", 1.0)
    
    -- 设置AB循环点，确保使用新获取的值
    mp.set_property("ab-loop-a", sub_start)
    mp.set_property("ab-loop-b", sub_end)
    mp.set_property("loop", "inf")
    
    -- 跳转到字幕开始位置
    mp.set_property("time-pos", sub_start)
    
    -- 开始循环播放
    is_cycling = true
    current_speed_index = 1
    repeat_count = 0
    
    -- 设置第一个速度
    local speed = options.speeds[current_speed_index]
    mp.set_property("speed", speed)
    mp.osd_message("字幕AB循环: " .. speed .. "x", 1)
    
    -- 设置定时器检查循环结束条件
    if timer then
        timer:kill()
    end
    timer = mp.add_periodic_timer(0.1, check_loop_end)
end

-- 开始简单字幕AB循环播放(不改变速度)
function toggle_simple_subtitle_loop()
    -- 如果正在进行增速循环，先停止
    if is_cycling then
        stop_cycling()
    end
    
    -- 如果正在跨字幕循环，先停止并确保完全重置状态
    if is_cross_subtitle_looping then
        stop_cross_subtitle_looping()
        -- 确保AB循环点被完全清除
        mp.set_property("ab-loop-a", "no")
        mp.set_property("ab-loop-b", "no")
    end
    
    -- 如果已经在简单循环，则停止
    if is_simple_looping then
        stop_simple_looping()
        return
    end
    
    -- 获取当前字幕时间，确保重新获取正确的时间范围
    local sub_start, sub_end = get_current_subtitle_times()
    if not sub_start or not sub_end then 
        mp.osd_message("无法获取字幕时间范围", 2)
        return 
    end
    
    -- 设置AB循环点，确保使用新获取的值
    mp.set_property("ab-loop-a", sub_start)
    mp.set_property("ab-loop-b", sub_end)
    mp.set_property("loop", "inf")
    
    -- 跳转到字幕开始位置
    mp.set_property("time-pos", sub_start)
    
    is_simple_looping = true
    mp.osd_message("字幕AB循环播放", 1)
end

-- 跨字幕AB循环功能
function toggle_cross_subtitle_loop()
    -- 如果正在进行增速循环，先停止
    if is_cycling then
        stop_cycling()
    end
    
    -- 如果正在简单循环，先停止
    if is_simple_looping then
        stop_simple_looping()
    end
    
    -- 根据当前状态执行不同操作
    if cross_subtitle_state == 0 then
        -- 第一次按g：设置A点为当前字幕的开始时间
        local sub_start, _ = get_current_subtitle_times()
        if not sub_start then 
            mp.osd_message("无法获取字幕开始时间", 2)
            return 
        end
        
        -- 设置A点
        mp.set_property("ab-loop-a", sub_start)
        mp.set_property("ab-loop-b", "no")
        
        -- 跳转到字幕开始位置
        mp.set_property("time-pos", sub_start)
        
        cross_subtitle_state = 1
        is_cross_subtitle_looping = true
        mp.osd_message("已设置跨字幕A点", 1)
        
    elseif cross_subtitle_state == 1 then
        -- 第二次按g：设置B点为当前字幕的结束时间
        local _, sub_end = get_current_subtitle_times()
        if not sub_end then 
            mp.osd_message("无法获取字幕结束时间", 2)
            return 
        end
        
        -- 设置B点
        mp.set_property("ab-loop-b", sub_end)
        mp.set_property("loop", "inf")
        
        cross_subtitle_state = 2
        mp.osd_message("已设置跨字幕AB循环", 1)
        
        -- 跳转到A点开始循环播放
        local loop_a = mp.get_property_number("ab-loop-a")
        if loop_a then
            mp.set_property("time-pos", loop_a)
        end
        
    elseif cross_subtitle_state == 2 then
        -- 第三次按g：退出循环
        stop_cross_subtitle_looping()
    end
end

-- 恢复原速播放
function reset_speed()
    mp.set_property("speed", 1.0)
    mp.osd_message("速度: 1.0x", 1)
    
    -- 如果正在循环，停止循环
    if is_cycling then
        stop_cycling()
    end
    
    -- 如果正在简单循环，也停止
    if is_simple_looping then
        stop_simple_looping()
    end
    
    -- 如果正在跨字幕循环，也停止
    if is_cross_subtitle_looping then
        stop_cross_subtitle_looping()
    end
end

-- 注册按键绑定
mp.add_key_binding("r", "subtitle_speed_cycle", start_subtitle_speed_cycling)
mp.add_key_binding("f", "simple_subtitle_loop", toggle_simple_subtitle_loop)
mp.add_key_binding("g", "cross_subtitle_loop", toggle_cross_subtitle_loop)

-- 注册脚本消息，这样可以通过input.conf中的script-message-to命令调用
mp.register_script_message("subtitle_speed_cycle", start_subtitle_speed_cycling)
mp.register_script_message("simple_subtitle_loop", toggle_simple_subtitle_loop)
mp.register_script_message("cross_subtitle_loop", toggle_cross_subtitle_loop)
mp.register_script_message("reset_speed", reset_speed)

-- 确保退出播放时清理资源
mp.register_event("end-file", function()
    if is_cycling then
        stop_cycling()
    end
    if is_simple_looping then
        stop_simple_looping()
    end
    if is_cross_subtitle_looping then
        stop_cross_subtitle_looping()
    end
end)

-- 添加脚本加载提示
print("字幕AB循环脚本已加载")
mp.osd_message("字幕AB循环脚本已加载", 1)