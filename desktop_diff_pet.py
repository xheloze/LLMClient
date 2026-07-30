"""
桌面差分图宠物 (Neuro-sama 风格简化版)
功能：
1. 透明背景悬浮窗
2. 鼠标穿透 (可以点击宠物后面的桌面图标)
3. 语音识别听你说话
4. TTS 语音回答
5. 根据对话内容自动切换差分表情
"""

import sys
import os
import threading
import time
import json
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QIcon

# --- 配置区域 ---
CONFIG = {
    "window_width": 400,      # 窗口宽度
    "window_height": 600,     # 窗口高度
    "position_x": 100,        # 屏幕 X 坐标 (左上角)
    "position_y": 100,        # 屏幕 Y 坐标
    "always_on_top": True,    # 是否置顶
    "click_through": True,    # 是否鼠标穿透 (关键！)
    "avatar_folder": "assets/avatar", # 图片文件夹路径
    "default_expression": "plain",    # 默认表情文件名 (不带后缀)
}

# 表情映射表 (LLM 输出关键词 -> 图片文件名)
EXPRESSION_MAP = {
    "normal": "plain",
    "happy": "happy",
    "smile": "smile",
    "angry": "angry",
    "sad": "cry",
    "cry": "cry",
    "shy": "shy",
    "surprised": "surprised",
    "confused": "confused",
    "love": "love",
    "neutral": "plain",
    "default": "plain"
}

class VoiceListener(QObject):
    """模拟语音监听线程 (实际使用时需接入 FunASR 或 Whisper)"""
    text_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False

    def start_listening(self):
        self.running = True
        print("🎤 语音监听已启动 (模拟模式)...")
        # 这里只是演示，实际需要接入录音和识别逻辑
        # 为了演示效果，我们模拟每隔几秒收到一句话
        # 真实项目中请替换为真实的 STT 逻辑
        
    def stop_listening(self):
        self.running = False

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_expr = CONFIG["default_expression"]
        self.load_image(self.current_expr)
        
        # 启动语音线程 (模拟)
        self.voice_thread = VoiceListener()
        # 真实场景中，这里连接 STT 信号到 self.on_user_speak
        
    def init_ui(self):
        # 设置窗口属性
        self.setWindowTitle("Alice Desktop Pet")
        self.setFixedSize(CONFIG["window_width"], CONFIG["window_height"])
        self.move(CONFIG["position_x"], CONFIG["position_y"])
        
        # 关键：去除窗口边框
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # 关键：背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 关键：鼠标穿透 (点击事件传递给底层桌面)
        if CONFIG["click_through"]:
            self.setAttribute(Qt.WA_TransparentForMouseEvents)
            
        # 创建显示图片的 Label
        self.image_label = QLabel(self)
        self.image_label.setGeometry(0, 0, CONFIG["window_width"], CONFIG["window_height"])
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # 如果开启了鼠标穿透，Label 也需要设置
        if CONFIG["click_through"]:
            self.image_label.setAttribute(Qt.WA_TransparentForMouseEvents)

    def load_image(self, expr_name):
        """加载并切换表情图片"""
        filename = EXPRESSION_MAP.get(expr_name, CONFIG["default_expression"])
        image_path = os.path.join(CONFIG["avatar_folder"], f"{filename}.png")
        
        # 兼容大小写和常见后缀
        if not os.path.exists(image_path):
            image_path = os.path.join(CONFIG["avatar_folder"], f"{filename}.jpg")
        if not os.path.exists(image_path):
            # 尝试查找文件夹内所有图片作为备选
            if os.path.exists(CONFIG["avatar_folder"]):
                files = os.listdir(CONFIG["avatar_folder"])
                for f in files:
                    if f.startswith(filename.split('.')[0]): # 简单模糊匹配
                        image_path = os.path.join(CONFIG["avatar_folder"], f)
                        break
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(
                CONFIG["window_width"], 
                CONFIG["window_height"], 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
            print(f"🎭 切换表情：{expr_name} -> {image_path}")
        else:
            print(f"⚠️ 未找到图片：{image_path}")
            # 创建一个占位色块以防万一
            self.image_label.setStyleSheet("background-color: rgba(0,0,0,0); border: 1px dashed gray;")
            self.image_label.setText(f"Missing: {filename}.png\n请将差分图放入 {CONFIG['avatar_folder']}")
            self.image_label.setStyleSheet("color: white; background: rgba(0,0,0,0.5); font-size: 14px;")

    def set_expression(self, expr_name):
        """外部调用此方法切换表情"""
        if expr_name != self.current_expr:
            self.current_expr = expr_name
            # 使用定时器在 UI 线程更新，防止卡顿
            QTimer.singleShot(0, lambda: self.load_image(expr_name))

    def on_user_speak(self, text):
        """当识别到用户说话时调用"""
        print(f"👂 听到你说：{text}")
        # 这里可以添加逻辑：比如听到"你好"就切换成 happy
        if "你好" in text or "hello" in text.lower():
            self.set_expression("happy")
        elif "生气" in text or "angry" in text.lower():
            self.set_expression("angry")
            
    def on_bot_reply(self, text, emotion_tag):
        """当 Bot 回复时调用 (解析 LLM 输出的情绪标签)"""
        print(f"🤖 Bot 回复：{text} [情绪：{emotion_tag}]")
        self.set_expression(emotion_tag)
        # 这里还可以调用 TTS 播放声音
        # play_tts(text)

def parse_emotion_from_text(text):
    """简单的正则提取情绪标签，例如 【表情：happy】"""
    import re
    match = re.search(r'【表情[:：]\s*(\w+)】', text)
    if match:
        return match.group(1)
    # 默认根据关键词猜测
    if "开心" in text or "哈哈" in text: return "happy"
    if "生气" in text or "可恶" in text: return "angry"
    if "哭" in text or "难过" in text: return "sad"
    return "normal"

if __name__ == "__main__":
    # 检查图片目录是否存在
    if not os.path.exists(CONFIG["avatar_folder"]):
        print(f"❌ 错误：找不到文件夹 '{CONFIG['avatar_folder']}'")
        print("请确保你的项目目录下有 assets/avatar 文件夹，并且里面放好了 .png 差分图。")
        # 尝试创建空文件夹提示用户
        os.makedirs(CONFIG["avatar_folder"], exist_ok=True)
        print(f"已创建空文件夹：{CONFIG['avatar_folder']}，请把图片放进去再运行。")
        sys.exit(1)

    app = QApplication(sys.argv)
    
    # 隐藏鼠标指针在窗口区域 (可选，增加沉浸感)
    # app.setOverrideCursor(Qt.BlankCursor) 

    pet = DesktopPet()
    pet.show()
    
    print("✅ 桌面宠物已启动！")
    print("💡 提示：窗口已设置为鼠标穿透，你可以点击宠物身后的桌面图标。")
    print("💡 按 Ctrl+C 或在任务管理器中结束 python.exe 退出。")
    
    # 模拟测试：每 5 秒自动切换一个表情，方便你查看效果
    test_timer = QTimer()
    expressions = ["plain", "happy", "smile", "angry", "cry", "shy"]
    idx = 0
    def test_cycle():
        nonlocal idx
        pet.set_expression(expressions[idx])
        idx = (idx + 1) % len(expressions)
    
    # 注释掉下面这行以关闭自动测试循环
    # test_timer.timeout.connect(test_cycle)
    # test_timer.start(2000) 

    sys.exit(app.exec_())
