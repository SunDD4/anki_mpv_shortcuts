# MPV播放器模块 - 处理MPV播放相关功能
from aqt import mw
from aqt.sound import SoundOrVideoTag
from aqt.utils import tooltip
import subprocess
import os

def play_with_mpv(tag):
    config = mw.addonManager.getConfig(__name__.split('.')[0]) or {}
    if not config.get("enabled", True):
        return False
    
    if isinstance(tag, SoundOrVideoTag):
        if hasattr(tag, "filename"):
            filename = tag.filename
        else:
            attrs = dir(tag)
            if "filename" in attrs:
                filename = tag.filename
            elif "path" in attrs:
                filename = tag.path
            else:
                tooltip(f"无法获取文件路径，可用属性: {attrs}")
                return False
    else:
        filename = str(tag)
        import re
        match = re.search(r'sound:(.*?)(?:\]|$)', filename)
        if match:
            filename = match.group(1)
    
    media_dir = os.path.join(mw.pm.profileFolder(), "collection.media")
    full_path = os.path.join(media_dir, filename)
    
    if not os.path.exists(full_path):
        tooltip(f"文件不存在: {full_path}")
        return False
    
    config = mw.addonManager.getConfig(__name__.split('.')[0]) or {}
    mpv_path = config.get("mpv_path", "/opt/homebrew/bin/mpv")
    window_scale = config.get("window_scale", 1.5)
    window_x = config.get("window_x", 50)
    window_y = config.get("window_y", 50)
    remember_position = config.get("remember_position", True)
    always_on_top = config.get("always_on_top", False)
    
    mpv_args = [mpv_path, f"--window-scale={window_scale}", "--keep-open=no"]
    
    if remember_position:
        mpv_args.append("--save-position-on-quit")
    else:
        mpv_args.append("--no-resume-playback")
    
    mpv_args.append(f"--geometry={window_x}%:{window_y}%")
    
    if always_on_top:
        mpv_args.append("--ontop")
    
    mpv_args.append(full_path)
    
    try:
        subprocess.Popen(mpv_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        tooltip(f"MPV 播放失败: {str(e)}")
        return False

def setup_hooks():
    from aqt.sound import av_player
    
    original_play_av_tags = av_player.play_tags
    
    def wrapped_play_tags(tags, *args, **kwargs):
        for tag in tags:
            if isinstance(tag, SoundOrVideoTag):
                if play_with_mpv(tag):
                    return
        return original_play_av_tags(tags, *args, **kwargs)
    
    av_player.play_tags = wrapped_play_tags