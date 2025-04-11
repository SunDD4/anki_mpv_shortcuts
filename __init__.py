# MPV播放器插件 - 使用MPV播放Anki中的视频
from aqt import gui_hooks, mw
from aqt.utils import tooltip
import os
import platform

if platform.system() != "Darwin":
    tooltip("MPV 快捷键插件仅支持 macOS 系统")

# 导入模块
from . import mpv_config
from . import mpv_scripts
from . import mpv_player
from . import mpv_ui

def setup_mpv_on_startup():
    config = mw.addonManager.getConfig(__name__) or {}
    mpv_path = config.get("mpv_path", "/opt/homebrew/bin/mpv")
    
    if not os.path.exists(mpv_path):
        from aqt.utils import showInfo
        showInfo(f"MPV 可执行文件不存在: {mpv_path}\n请在插件配置中设置正确的 MPV 路径")
        return
    
    mpv_config.check_speed_cycle_script()
    
    if mpv_config.create_mpv_config():
        tooltip("MPV 快捷键配置已更新")
    else:
        from aqt.utils import showText
        debug_info = []
        debug_info.append(f"MPV 路径: {mpv_path}")
        debug_info.append(f"配置目录: {os.path.expanduser('~/.config/mpv')}")
        
        config_dir = os.path.expanduser("~/.config/mpv")
        if os.path.exists(config_dir):
            try:
                test_file = os.path.join(config_dir, "test_write.tmp")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                debug_info.append("配置目录写入权限: 正常")
            except Exception as e:
                debug_info.append(f"配置目录写入权限: 失败 - {str(e)}")
        
        showText("\n".join(debug_info))
        from aqt.utils import showInfo
        showInfo("MPV 快捷键配置失败，请检查日志")

# 初始化钩子
gui_hooks.profile_did_open.append(setup_mpv_on_startup)
gui_hooks.profile_did_open.append(lambda: mpv_ui.add_menu_item())
mpv_player.setup_hooks()