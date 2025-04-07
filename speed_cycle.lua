-- 倍速循环播放脚本
local speeds = {0.7, 0.8, 1.0, 1.2}  -- 定义倍速序列
local current_index = 1
local is_cycling = false
local timer = nil
local start_time = nil
local video_duration = nil
local ab_loop_observer = nil

function cycle_speed()
    if not is_cycling then
        return
    end
    
    -- 设置当前倍速
    mp.set_property_number("speed", speeds[current_index])
    mp.osd_message(string.format("播放速度: %.1fx", speeds[current_index]))
    
    -- 检查是否在AB循环模式
    local ab_a = mp.get_property_number("ab-loop-a")
    local ab_b = mp.get_property_number("ab-loop-b")
    local is_ab_loop = ab_a ~= nil and ab_a >= 0 and ab_b ~= nil and ab_b > ab_a
    
    -- 移动到下一个倍速索引
    current_index = current_index + 1
    
    -- 如果已经完成所有倍速，停止循环
    if current_index > #speeds then
        stop_cycling()
        return
    end
    
    -- 如果在AB循环模式下
    if is_ab_loop then
        -- 计算当前倍速下完成一次AB循环需要的时间
        local loop_duration = ab_b - ab_a
        local time_needed = loop_duration / speeds[current_index - 1]
        
        -- 设置定时器，在当前速度下完成一次AB循环后切换到下一个速度
        if timer then
            timer:kill()
        end
        timer = mp.add_timeout(time_needed, function()
            -- 如果仍在循环中，切换到下一个速度
            if is_cycling then
                cycle_speed()
            end
        end)
    else
        -- 不在AB循环模式下，使用EOF事件监听
        if ab_loop_observer then
            mp.unobserve_property(ab_loop_observer)
        end
        
        ab_loop_observer = mp.observe_property("eof-reached", "bool", function(name, value)
            if value and is_cycling then
                -- 视频结束时，重置位置并切换到下一个速度
                mp.set_property_number("time-pos", 0)
                cycle_speed()
            end
        end)
    end
end

function start_cycling()
    if is_cycling then
        stop_cycling()
        return
    end
    
    -- 确保视频不会自动关闭
    mp.set_property("keep-open", "yes")
    
    -- 检查是否在AB循环模式
    local ab_a = mp.get_property_number("ab-loop-a")
    local ab_b = mp.get_property_number("ab-loop-b")
    local is_ab_loop = ab_a ~= nil and ab_a >= 0 and ab_b ~= nil and ab_b > ab_a
    
    if is_ab_loop then
        -- 如果在AB循环模式下，从A点开始播放
        mp.set_property_number("time-pos", ab_a)
        mp.osd_message("在AB循环区间内开始倍速循环播放")
    else
        -- 否则从头开始播放
        mp.set_property_number("time-pos", 0)
        mp.osd_message("开始倍速循环播放")
    end
    
    is_cycling = true
    current_index = 1
    cycle_speed()
end

function stop_cycling()
    is_cycling = false
    if timer then
        timer:kill()
        timer = nil
    end
    
    -- 停止观察EOF事件
    if ab_loop_observer then
        mp.unobserve_property(ab_loop_observer)
        ab_loop_observer = nil
    end
    
    mp.osd_message("倍速循环播放结束")
end

-- 绑定r键触发倍速循环
mp.add_key_binding("r", "speed_cycle", start_cycling)
-- 绑定v键触发相同的倍速循环功能
mp.add_key_binding("v", "speed_cycle_alt", start_cycling)