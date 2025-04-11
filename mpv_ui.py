# MPV界面模块 - 处理MPV控制面板相关功能
from aqt import mw
from aqt.utils import tooltip
from aqt.qt import QDialog, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout, QGridLayout, QCheckBox, QGroupBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen

# 添加自定义滑块类
# 修改自定义滑块类的 paintEvent 方法
class MarkedSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.markers = {}  # 格式: {value: color}
        
    def add_marker(self, value, color=QColor(255, 255, 255)):
        self.markers[value] = color
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.markers:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 简化实现，直接使用滑块的几何信息
        slider_height = self.height()
        groove_height = 8  # 估计的轨道高度
        groove_y = (slider_height - groove_height) / 2
        
        for value, color in self.markers.items():
            # 计算标记点位置
            position = self.style().sliderPositionFromValue(
                self.minimum(), 
                self.maximum(), 
                value, 
                self.width() - 16
            ) + 8
            
            # 绘制小圆形标记点
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            
            # 使用更小的标记点，与轨道融合
            marker_size = 5  # 固定大小为5像素
            
            if self.orientation() == Qt.Orientation.Horizontal:
                # 向右上方移动标记点位置，使其更好地融合到滑条中
                painter.drawEllipse(
                    position - marker_size/2 + 1,  # 向右移动1像素
                    groove_y + (groove_height - marker_size)/2 - 2,  # 向上移动2像素
                    marker_size, 
                    marker_size
                )
            else:
                painter.drawEllipse(
                    self.width()/2 - marker_size/2, 
                    position - marker_size/2, 
                    marker_size, 
                    marker_size
                )

def add_menu_item():
    from aqt.qt import QAction, qconnect
    
    for action in mw.form.menuTools.actions():
        if action.text() == "MPV播放设置":
            return
    
    mpv_action = QAction("MPV播放设置", mw)
    qconnect(mpv_action.triggered, show_mpv_control_panel)
    mw.form.menuTools.addAction(mpv_action)

def show_mpv_control_panel():
    from . import mpv_config
    
    config = mw.addonManager.getConfig(__name__.split('.')[0]) or {}
    current_scale = config.get("window_scale", 1.5)
    current_x = config.get("window_x", 50)
    current_y = config.get("window_y", 50)
    is_enabled = config.get("enabled", True)
    remember_position = config.get("remember_position", True)
    enable_speed_cycle = config.get("enable_speed_cycle", True)
    always_on_top = config.get("always_on_top", False)
    
    # 获取x和z快捷键的配置
    x_duration = config.get("x_duration", 3.0)
    x_offset = config.get("x_offset", 1.5)
    z_duration = config.get("z_duration", 2.5)
    z_offset = config.get("z_offset", 2.7)
    
    dialog = QDialog(mw)
    dialog.setWindowTitle("MPV播放器控制面板")
    dialog.setMinimumWidth(400)
    layout = QVBoxLayout(dialog)
    
    toggle_group = QGroupBox("MPV播放器开关")
    toggle_layout = QVBoxLayout()
    
    toggle_checkbox = QCheckBox("启用MPV播放器")
    toggle_checkbox.setChecked(is_enabled)
    toggle_layout.addWidget(toggle_checkbox)
    
    remember_position_checkbox = QCheckBox("记住视频播放进度")
    remember_position_checkbox.setChecked(remember_position)
    toggle_layout.addWidget(remember_position_checkbox)
    
    speed_cycle_checkbox = QCheckBox("启用倍速循环播放脚本 (r键触发)")
    speed_cycle_checkbox.setChecked(enable_speed_cycle)
    toggle_layout.addWidget(speed_cycle_checkbox)
    
    always_on_top_checkbox = QCheckBox("视频窗口置顶")
    always_on_top_checkbox.setChecked(always_on_top)
    toggle_layout.addWidget(always_on_top_checkbox)
    
    toggle_group.setLayout(toggle_layout)
    layout.addWidget(toggle_group)
    
    scale_group = QGroupBox("视频播放窗口大小调整")
    scale_layout = QVBoxLayout()
    
    scale_label = QLabel("调整MPV视频播放窗口大小 (0.5x - 3.0x):")
    scale_layout.addWidget(scale_label)
    
    scale_slider_layout = QHBoxLayout()
    
    scale_slider = QSlider(Qt.Orientation.Horizontal)
    scale_slider.setMinimum(50)
    scale_slider.setMaximum(300)
    scale_slider.setValue(int(current_scale * 100))
    scale_slider_layout.addWidget(scale_slider, 4)
    
    scale_value_label = QLabel(f"{current_scale:.1f}x")
    scale_slider_layout.addWidget(scale_value_label, 1)
    
    scale_layout.addLayout(scale_slider_layout)
    scale_group.setLayout(scale_layout)
    layout.addWidget(scale_group)
    
    position_group = QGroupBox("视频播放窗口位置调整")
    position_layout = QVBoxLayout()
    
    position_label = QLabel("调整MPV视频播放窗口位置 (0% - 100%):")
    position_layout.addWidget(position_label)
    
    position_grid_layout = QGridLayout()
    
    x_label = QLabel("水平位置 (X):")
    position_grid_layout.addWidget(x_label, 0, 0)
    
    x_slider = QSlider(Qt.Orientation.Horizontal)
    x_slider.setMinimum(0)
    x_slider.setMaximum(100)
    x_slider.setValue(current_x)
    position_grid_layout.addWidget(x_slider, 0, 1)
    
    x_value_label = QLabel(f"{current_x}%")
    position_grid_layout.addWidget(x_value_label, 0, 2)
    
    y_label = QLabel("垂直位置 (Y):")
    position_grid_layout.addWidget(y_label, 1, 0)
    
    y_slider = QSlider(Qt.Orientation.Horizontal)
    y_slider.setMinimum(0)
    y_slider.setMaximum(100)
    y_slider.setValue(current_y)
    position_grid_layout.addWidget(y_slider, 1, 1)
    
    y_value_label = QLabel(f"{current_y}%")
    position_grid_layout.addWidget(y_value_label, 1, 2)
    
    position_layout.addLayout(position_grid_layout)
    
    preview_label = QLabel(f"预览: --geometry={current_x}%:{current_y}%")
    position_layout.addWidget(preview_label)
    
    position_group.setLayout(position_layout)
    layout.addWidget(position_group)
    
    # 修改X键AB循环设置组标题
    x_ab_group = QGroupBox("X键AB循环设置")
    x_ab_layout = QVBoxLayout()
    
    x_duration_label = QLabel(f"X键AB循环持续时间 (1.0秒 - 5.0秒):")
    x_ab_layout.addWidget(x_duration_label)
    
    x_duration_slider_layout = QHBoxLayout()
    x_duration_slider = QSlider(Qt.Orientation.Horizontal)
    x_duration_slider.setMinimum(10)
    x_duration_slider.setMaximum(50)
    x_duration_slider.setValue(int(x_duration * 10))
    x_duration_slider_layout.addWidget(x_duration_slider, 4)
    
    x_duration_value_label = QLabel(f"{x_duration:.1f}秒")
    x_duration_slider_layout.addWidget(x_duration_value_label, 1)
    
    x_ab_layout.addLayout(x_duration_slider_layout)
    
    # 修改X键AB循环偏移时间滑块
    x_offset_label = QLabel(f"X键AB循环偏移时间 (-2.0秒 - 5.0秒):")
    x_ab_layout.addWidget(x_offset_label)
    
    x_offset_slider_layout = QHBoxLayout()
    # 使用自定义滑块
    x_offset_slider = MarkedSlider(Qt.Orientation.Horizontal)
    x_offset_slider.setMinimum(-20)  # -2.0秒
    x_offset_slider.setMaximum(50)   # 5.0秒
    x_offset_slider.setValue(int(x_offset * 10))
    
    # 添加标记点说明
    x_offset_marker_label = QLabel("白色: 0秒 | 黄色: 0.5秒 (时间补偿点)")
    x_offset_marker_label.setStyleSheet("font-size: 10px; color: #909090;")
    x_ab_layout.addWidget(x_offset_marker_label)
    
    # 添加标记点 - 在滑块完全显示后添加
    def add_x_markers():
        x_offset_slider.add_marker(0, QColor(255, 255, 255))  # 0秒处白色标记
        x_offset_slider.add_marker(5, QColor(176, 124, 31))   # 0.5秒处黄色标记
    
    # 使用计时器延迟添加标记点，确保滑块已完全渲染
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(100, add_x_markers)
    
    x_offset_slider_layout.addWidget(x_offset_slider, 4)
    
    x_offset_value_label = QLabel(f"{x_offset:.1f}秒")
    x_offset_slider_layout.addWidget(x_offset_value_label, 1)
    
    x_ab_layout.addLayout(x_offset_slider_layout)
    
    x_ab_group.setLayout(x_ab_layout)
    layout.addWidget(x_ab_group)
    
    # 添加Z键AB循环设置组
    z_ab_group = QGroupBox("Z键自定义AB循环设置")
    z_ab_layout = QVBoxLayout()
    
    z_duration_label = QLabel(f"Z键AB循环持续时间 (1.0秒 - 5.0秒):")
    z_ab_layout.addWidget(z_duration_label)
    
    z_duration_slider_layout = QHBoxLayout()
    z_duration_slider = QSlider(Qt.Orientation.Horizontal)
    z_duration_slider.setMinimum(10)
    z_duration_slider.setMaximum(50)
    z_duration_slider.setValue(int(z_duration * 10))
    z_duration_slider_layout.addWidget(z_duration_slider, 4)
    
    z_duration_value_label = QLabel(f"{z_duration:.1f}秒")
    z_duration_slider_layout.addWidget(z_duration_value_label, 1)
    
    z_ab_layout.addLayout(z_duration_slider_layout)
    
    # 修改Z键AB循环偏移时间滑块
    z_offset_label = QLabel(f"Z键AB循环偏移时间 (-2.0秒 - 5.0秒):")
    z_ab_layout.addWidget(z_offset_label)
    
    z_offset_slider_layout = QHBoxLayout()
    # 使用自定义滑块
    z_offset_slider = MarkedSlider(Qt.Orientation.Horizontal)
    z_offset_slider.setMinimum(-20)  # -2.0秒
    z_offset_slider.setMaximum(50)   # 5.0秒
    z_offset_slider.setValue(int(z_offset * 10))
    
    # 添加标记点说明
    z_offset_marker_label = QLabel("白色: 0秒 | 黄色: 0.5秒 (时间补偿点)")
    z_offset_marker_label.setStyleSheet("font-size: 10px; color: #909090;")
    z_ab_layout.addWidget(z_offset_marker_label)
    
    # 添加标记点 - 在滑块完全显示后添加
    def add_z_markers():
        z_offset_slider.add_marker(0, QColor(255, 255, 255))  # 0秒处白色标记
        z_offset_slider.add_marker(5, QColor(176, 124, 31))   # 0.5秒处黄色标记
    
    # 使用计时器延迟添加标记点，确保滑块已完全渲染
    QTimer.singleShot(100, add_z_markers)
    
    z_offset_slider_layout.addWidget(z_offset_slider, 4)
    
    z_offset_value_label = QLabel(f"{z_offset:.1f}秒")
    z_offset_slider_layout.addWidget(z_offset_value_label, 1)
    
    z_ab_layout.addLayout(z_offset_slider_layout)
    z_ab_group.setLayout(z_ab_layout)
    layout.addWidget(z_ab_group)
    
    button_layout = QHBoxLayout()
    ok_button = QPushButton("确定")
    cancel_button = QPushButton("取消")
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    layout.addLayout(button_layout)
    
    def update_scale_value_label(value):
        scale = value / 100
        scale_value_label.setText(f"{scale:.1f}x")
        if not scale_slider.isSliderDown():
            snap_to_nearest_half(scale_slider)
    
    def on_slider_released():
        snap_to_nearest_half(scale_slider)
    
    def snap_to_nearest_half(slider):
        current_value = slider.value()
        scale = current_value / 100
        nearest_half = round(scale * 2) / 2
        if abs(scale - nearest_half) < 0.2:
            new_value = int(nearest_half * 100)
            slider.setValue(new_value)
            scale_value_label.setText(f"{nearest_half:.1f}x")
    
    def update_x_value_label(value):
        x_value_label.setText(f"{value}%")
        update_preview()
    
    def update_y_value_label(value):
        y_value_label.setText(f"{value}%")
        update_preview()
    
    def update_preview():
        x_val = x_slider.value()
        y_val = y_slider.value()
        preview_label.setText(f"预览: --geometry={x_val}%:{y_val}%")
    
    def update_x_duration_value_label(value):
        duration = value / 10
        x_duration_value_label.setText(f"{duration:.1f}秒")
    
    def update_x_offset_value_label(value):
        offset = value / 10
        x_offset_value_label.setText(f"{offset:.1f}秒")
    
    def update_z_duration_value_label(value):
        duration = value / 10
        z_duration_value_label.setText(f"{duration:.1f}秒")
    
    def update_z_offset_value_label(value):
        offset = value / 10
        z_offset_value_label.setText(f"{offset:.1f}秒")
    
    def on_ok():
        config["enabled"] = toggle_checkbox.isChecked()
        config["remember_position"] = remember_position_checkbox.isChecked()
        old_speed_cycle_state = config.get("enable_speed_cycle", True)
        config["enable_speed_cycle"] = speed_cycle_checkbox.isChecked()
        config["always_on_top"] = always_on_top_checkbox.isChecked()
        
        scale = scale_slider.value() / 100
        config["window_scale"] = scale
        
        x_val = x_slider.value()
        y_val = y_slider.value()
        config["window_x"] = x_val
        config["window_y"] = y_val
        
        # 保存AB循环设置
        x_duration = x_duration_slider.value() / 10
        x_offset = x_offset_slider.value() / 10
        z_duration = z_duration_slider.value() / 10
        z_offset = z_offset_slider.value() / 10
        
        config["x_duration"] = x_duration
        config["x_offset"] = x_offset
        config["z_duration"] = z_duration
        config["z_offset"] = z_offset
        
        mw.addonManager.writeConfig(__name__.split('.')[0], config)
        
        # 总是重新创建配置以更新AB循环设置
        mpv_config.create_mpv_config()
        
        enabled_state = "启用" if config["enabled"] else "禁用"
        remember_state = "启用" if config["remember_position"] else "禁用"
        speed_cycle_state = "启用" if config["enable_speed_cycle"] else "禁用"
        always_on_top_state = "启用" if config["always_on_top"] else "禁用"
        tooltip(f"MPV播放器已{enabled_state}，记住播放进度已{remember_state}，倍速循环脚本已{speed_cycle_state}，窗口置顶已{always_on_top_state}，窗口大小: {scale:.1f}x，位置: X:{x_val}%, Y:{y_val}%")
        
        dialog.accept()
    
    def on_cancel():
        dialog.reject()
    
    scale_slider.valueChanged.connect(update_scale_value_label)
    scale_slider.sliderReleased.connect(on_slider_released)
    x_slider.valueChanged.connect(update_x_value_label)
    y_slider.valueChanged.connect(update_y_value_label)
    x_duration_slider.valueChanged.connect(update_x_duration_value_label)
    x_offset_slider.valueChanged.connect(update_x_offset_value_label)
    z_duration_slider.valueChanged.connect(update_z_duration_value_label)
    z_offset_slider.valueChanged.connect(update_z_offset_value_label)
    
    ok_button.clicked.connect(on_ok)
    cancel_button.clicked.connect(on_cancel)
    
    dialog.exec()