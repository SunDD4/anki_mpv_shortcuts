- - - - - # Anki MPV 快捷键插件

          ### 解决：ANKI自带MPV播放器，无法实现的精听/循环激发问题

          ##想法（场景）：
          - 用视频/音频学英语（任何语言）， 1分钟或仅10秒钟的材料，例期间3~4秒间内容（听不清）如单词/短语/语块等，这时想精听这个地方，（并让它不断的循环，且自动从低倍速→高倍速循环：例，从0.6倍速到1.2倍速循环） 实现✅：慢速理解→ 升速激发→ 高速巩固（听力难点逐一击破）

          ## 功能特点

          - 使用Homebrew下载最新版的MPV播放器，取代Anki默认的自带的mpv播放器
          - 取代后实现：提供丰富的键盘快捷键控制播放
          - 取代后实现：支持整个视频/音频， 自动→同速/或逐步倍速循环播放功能
          - 取代后实现：支持AB循环区间内的，自动→同速/或逐步倍速循环播放

          ## 快捷键

          - `SPACE`: 暂停/恢复播放
          - `LEFT`/`a`: 后退2秒
          - `RIGHT`/`d`: 前进2秒
          - `UP`/`w`: 增加播放速度（1.1倍）
          - `DOWN`/`s`: 减少播放速度（0.85倍）
          - `q`: 退出播放
          - `e`: 恢复原速播放（1.0倍）

          - 重点功能：
          - `f`: 循环播放整个视频
          - `c`: AB循环（按一次设置A点，再按一次设置B点）
          - `r`或`v`: 倍速循环播放（从0.6倍速开始，依次切换到0.7倍速、0.8倍速、1.0倍速、1.2倍速）✅
          - `x`: 自定义• 一键触发：设置一个当前帧，往后2秒（可设置）的 AB 循环 → 倍速循环播放 → 自动清除 AB 循环 → 继续正常播放✅
          - `z`: 自定义• 一键触发：设置一个当前帧，回溯之前2.5秒（可设置）的 AB 循环 → 倍速循环播放 → 自动清除 AB 循环 → 继续正常播放✅

          -  建议 c/ v 配合使用, 先按两次c确定” a→b loop” 可以快速设置AB循环区间, 再按v, 可以在该区间内进行倍速循环播放✅
          - 本插件在ANKI设置好后，还可以配合INNA 播放器使用（启用advanced功能即可），适合用INNA看美剧时利用上述设置好的快捷键进行操作，实现跨应用学习逻辑一致🔥

          ## 使用方法

          1. 安装插件前，确保通过homebrew,已安装MPV播放器
          2. 在Anki中播放媒体文件时，将自动使用MPV播放器
          3. 使用上述快捷键控制播放
          4. 可以先按两次`c`键设置AB循环区间，然后按`r`或`v`键在该区间内进行倍速循环播放

          ## 系统要求

          - 目前仅测试了macOS系统
          - 需要安装MPV播放器（建议通过Mac终端，Homebrew安装：`brew install mpv`）
