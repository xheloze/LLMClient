"""
天童爱丽丝 - 完整桌面宠物版
功能：透明悬浮窗 + 语音识别 + TTS 语音 + 表情切换
适用于 Windows 11 + i5-8400 + RTX 2060 + 32GB RAM

使用方法:
1. 安装依赖：pip install PyQt5 websockets SpeechRecognition pyttsx3 playsound pillow numpy
2. 运行：python desktop_pet_full.py --mode avatar
3. 对麦克风说话，爱丽丝会听到并回应！
"""

import sys
import os
import json
import asyncio
import threading
import argparse
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# ============== 配置检查 ==============
def check_dependencies():
    """检查并提示安装依赖"""
    missing = []
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        missing.append("PyQt5")
    
    try:
        import websockets
    except ImportError:
        missing.append("websockets")
    
    try:
        import speech_recognition as sr
    except ImportError:
        missing.append("SpeechRecognition")
    
    try:
        import pyttsx3
    except ImportError:
        missing.append("pyttsx3")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    
    if missing:
        print(f"❌ 缺少依赖：{', '.join(missing)}")
        print(f"✅ 请运行：pip install {' '.join(missing)}")
        return False
    return True


# ============== 语音识别模块 ==============
class VoiceRecognizer:
    """语音识别 - 听您说话"""
    
    def __init__(self, language: str = "zh-CN"):
        self.recognizer = None
        self.language = language
        self.is_listening = False
        self.callback = None
        
        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            print("✅ 语音识别模块已初始化")
        except Exception as e:
            print(f"⚠️ 语音识别模块初始化失败：{e}")
    
    def start_listening(self, callback_func):
        """开始监听麦克风"""
        self.callback = callback_func
        self.is_listening = True
        
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
        print("🎤 开始监听麦克风...（对麦克风说话）")
    
    def _listen_loop(self):
        """监听循环"""
        while self.is_listening:
            try:
                with self.sr.Microphone() as source:
                    # 环境噪音校准
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    print("👂 正在听...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    try:
                        # 使用 Google 语音识别（离线可用中文）
                        text = self.recognizer.recognize_google(audio, language=self.language)
                        print(f"🎯 识别结果：{text}")
                        
                        if self.callback and text.strip():
                            self.callback(text)
                            
                    except self.sr.UnknownValueError:
                        pass  # 未识别到语音
                    except self.sr.RequestError as e:
                        print(f"⚠️ 语音识别服务错误：{e}")
                        
            except Exception as e:
                print(f"⚠️ 监听错误：{e}")
                time.sleep(1)
    
    def stop_listening(self):
        """停止监听"""
        self.is_listening = False


# ============== TTS 语音合成模块 ==============
class TTSSpeaker:
    """TTS 语音合成 - 让爱丽丝说话"""
    
    def __init__(self, voice_name: str = None, rate: int = 150):
        self.engine = None
        self.rate = rate
        self.is_speaking = False
        self.on_speak_start = None
        self.on_speak_end = None
        
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            
            # 设置语速
            self.engine.setProperty('rate', rate)
            
            # 尝试设置中文语音
            voices = self.engine.getProperty('voices')
            if voice_name:
                for voice in voices:
                    if voice_name.lower() in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        print(f"✅ 使用语音：{voice.name}")
                        break
            else:
                # 自动选择中文语音
                for voice in voices:
                    if 'chinese' in voice.name.lower() or 'zh' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        print(f"✅ 自动选择中文语音：{voice.name}")
                        break
            
            print("✅ TTS 语音合成模块已初始化")
        except Exception as e:
            print(f"⚠️ TTS 模块初始化失败：{e}")
    
    def speak(self, text: str, on_start=None, on_end=None):
        """说话"""
        if not self.engine or not text:
            return
        
        self.is_speaking = True
        
        if on_start:
            on_start()
        
        def speak_thread():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                
                if on_end:
                    on_end()
            except Exception as e:
                print(f"⚠️ TTS 播放错误：{e}")
            finally:
                self.is_speaking = False
        
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()
    
    def stop(self):
        """停止说话"""
        if self.engine:
            self.engine.stop()
        self.is_speaking = False


# ============== 差分图显示窗口 ==============
class AvatarWindow:
    """差分图显示窗口 - 透明悬浮窗"""
    
    def __init__(self, config: Dict[str, Any]):
        from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QPixmap, QColor
        
        self.config = config
        self.current_expression = "normal"
        self.is_speaking = False
        self.images = {}
        self.blink_timer = None
        
        # 加载图片
        avatar_dir = Path(config.get("avatar_dir", "avatar/"))
        images_config = config.get("images", {})
        
        print("\n📂 加载差分图:")
        for expr, filename in images_config.items():
            img_path = avatar_dir / filename
            if img_path.exists():
                pixmap = QPixmap(str(img_path))
                if not pixmap.isNull():
                    self.images[expr] = pixmap
                    print(f"   ✅ {expr}: {filename}")
            else:
                print(f"   ⚠️ 图片不存在：{img_path}")
        
        if not self.images:
            print("❌ 未加载到任何图片！请检查 avatar/ 目录")
        
        # 创建窗口
        self.widget = QWidget()
        window_config = config.get("window", {})
        
        width = window_config.get("width", 500)
        height = window_config.get("height", 700)
        x = window_config.get("x", 100)
        y = window_config.get("y", 100)
        
        self.widget.setFixedSize(width, height)
        self.widget.setWindowTitle("天童爱丽丝")
        
        # 关键设置：透明背景 + 鼠标穿透 + 置顶
        self.widget.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        self.widget.setAttribute(Qt.WA_TransparentForMouseEvents)  # 鼠标穿透（点击穿透到桌面）
        self.widget.setWindowFlags(
            Qt.FramelessWindowHint |      # 无边框
            Qt.WindowStaysOnTopHint |     # 始终置顶
            Qt.Tool |                     # 工具窗口（不在任务栏显示）
            Qt.WindowTransparentForInput  # 输入透明
        )
        
        # 设置位置（右下角）
        screen = QApplication.primaryScreen().geometry()
        if x < 0:  # 负数表示从右边计算
            x = screen.width() + x - width
        if y < 0:
            y = screen.height() + y - height
        
        self.widget.move(x, y)
        print(f"\n🖥️ 窗口位置：({x}, {y}), 大小：{width}x{height}")
        print(f"📐 屏幕分辨率：{screen.width()}x{screen.height()}")
        
        # 创建标签
        self.label = QLabel(self.widget)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.widget.setLayout(layout)
        
        # 初始显示
        self._update_display()
        self.widget.show()
        
        # 眨眼定时器（每 3-6 秒眨一次眼）
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._blink)
        self.blink_timer.start(4000)
        
        print("✅ 差分图窗口已创建")
    
    def _blink(self):
        """眨眼效果"""
        # 简单实现：暂时切换到眨眼表情（如果有）
        if "blink" in self.images and self.current_expression != "blink":
            old_expr = self.current_expression
            self.update_expression("blink")
            QTimer.singleShot(200, lambda: self.update_expression(old_expr))
    
    def update_expression(self, expression: str):
        """更新表情"""
        if expression in self.images:
            self.current_expression = expression
            self._update_display()
            print(f"🎭 表情切换：{expression}")
        else:
            # 尝试匹配相似表情
            for key in self.images.keys():
                if key in expression or expression in key:
                    self.current_expression = key
                    self._update_display()
                    print(f"🎭 表情切换：{expression} -> {key}")
                    return
            print(f"⚠️ 未知表情：{expression}，保持当前表情")
    
    def set_speaking(self, speaking: bool):
        """设置说话状态"""
        self.is_speaking = speaking
        if speaking:
            print("💬 正在说话...")
        else:
            print("🔇 停止说话")
    
    def _update_display(self):
        """更新显示"""
        pixmap = self.images.get(self.current_expression)
        if pixmap:
            # 缩放图片适应窗口
            scaled = pixmap.scaled(
                self.label.width(),
                self.label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.label.setPixmap(scaled)
        else:
            self.label.setText(f"{self.current_expression}\n(无图片)")


# ============== 主程序 ==============
class DesktopPetFull:
    """完整桌面宠物 - 集成所有功能"""
    
    def __init__(self, mode: str = "avatar", config_path: str = None):
        self.mode = mode
        self.config_path = config_path or "config/avatar_config.json"
        self.config = self._load_config()
        
        self.app = None
        self.window = None
        self.voice_recognizer = None
        self.tts_speaker = None
        self.websocket_server = None
        
        # 简单的对话响应逻辑
        self.response_map = {
            "你好": "【表情：happy】老师好！今天也要一起努力哦！",
            "早上好": "【表情：awake】早上好，老师！新的一天开始了呢！",
            "晚安": "【表情：smile】晚安，老师~做个好梦！",
            "谢谢": "【表情：shy】不用谢，这是我应该做的！",
            "喜欢": "【表情：happy】我也最喜欢老师了！",
            "生气": "【表情：angry】不要生气嘛，我会担心的...",
            "开心": "【表情：happy】看到老师开心，我也很开心！",
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 配置文件未找到，使用默认配置")
            return {
                "avatar_dir": "avatar/",
                "window": {"width": 500, "height": 700, "x": -600, "y": -100},  # 右下角
                "images": {
                    "normal": "plain.png",
                    "happy": "happy.png",
                    "smile": "smile.png",
                    "angry": "angry.png",
                    "sad": "cry.png",
                    "shy": "shy.png"
                },
                "websocket": {"host": "127.0.0.1", "port": 8766}
            }
    
    def start(self):
        """启动程序"""
        print("=" * 70)
        print("🎮 天童爱丽丝 - 完整桌面宠物")
        print("🖥️ 您的配置：i5-8400 + RTX 2060 + 32GB RAM - ✅ 完美支持")
        print("=" * 70)
        
        # 创建 Qt 应用
        from PyQt5.QtWidgets import QApplication
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        # 创建窗口
        print(f"\n🎨 模式：{'Live2D' if self.mode == 'live2d' else '差分图'}")
        self.window = AvatarWindow(self.config)
        
        # 初始化语音识别
        print("\n🎤 初始化语音识别...")
        self.voice_recognizer = VoiceRecognizer(language="zh-CN")
        
        # 初始化 TTS
        print("🔊 初始化 TTS 语音合成...")
        self.tts_speaker = TTSSpeaker(rate=160)
        
        # 启动 WebSocket 服务器（用于接收外部指令）
        ws_thread = threading.Thread(target=self._run_websocket_server, daemon=True)
        ws_thread.start()
        
        # 设置语音回调
        def on_voice_detected(text):
            """当识别到语音时的处理"""
            self._handle_user_input(text)
        
        print("\n" + "=" * 70)
        print("🚀 启动完成！")
        print("=" * 70)
        print("\n💡 使用说明:")
        print("   1. 爱丽丝已出现在桌面右下角（透明悬浮窗）")
        print("   2. 对她说话，她会听到并回应")
        print("   3. 支持命令：你好、早上好、晚安、谢谢等")
        print("   4. 按 Ctrl+C 退出程序")
        print("\n🎯 现在就开始和爱丽丝互动吧！")
        print("=" * 70 + "\n")
        
        # 开始监听（延迟 2 秒启动）
        QTimer = self.app.__class__
        from PyQt5.QtCore import QTimer as QtQTimer
        QtQTimer.singleShot(2000, lambda: self.voice_recognizer.start_listening(on_voice_detected))
        
        # 运行 Qt 主循环
        sys.exit(self.app.exec_())
    
    def _handle_user_input(self, text: str):
        """处理用户输入"""
        print(f"\n👤 用户说：{text}")
        
        # 简单关键词匹配
        response = None
        for keyword, reply in self.response_map.items():
            if keyword in text:
                response = reply
                break
        
        if not response:
            # 默认回应
            response = f"【表情：smile】老师说了「{text}」呢，爱丽丝明白了！"
        
        # 回复
        self._respond(response)
    
    def _respond(self, text: str):
        """回复用户"""
        print(f"🤖 爱丽丝：{text}")
        
        # 提取表情
        import re
        expr_match = re.search(r'【表情 [:：=]\s*(\w+)】', text)
        expression = expr_match.group(1) if expr_match else "normal"
        
        # 切换表情
        self.window.update_expression(expression)
        
        # 清理文本（移除表情标记）
        clean_text = re.sub(r'【表情 [:：=]\s*\w+】', '', text).strip()
        
        # TTS 播放
        def on_speak_start():
            self.window.set_speaking(True)
        
        def on_speak_end():
            self.window.set_speaking(False)
        
        self.tts_speaker.speak(clean_text, on_speak_start, on_speak_end)
    
    def _run_websocket_server(self):
        """WebSocket 服务器"""
        try:
            import websockets
            
            host = self.config.get("websocket", {}).get("host", "127.0.0.1")
            port = self.config.get("websocket", {}).get("port", 8766)
            
            async def handler(websocket, path):
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        action = data.get("action")
                        
                        if action == "set_expression":
                            self.window.update_expression(data.get("expression", "normal"))
                        elif action == "start_speaking":
                            self.window.set_speaking(True)
                        elif action == "stop_speaking":
                            self.window.set_speaking(False)
                        elif action == "speak":
                            text = data.get("text", "")
                            self._respond(text)
                    except Exception as e:
                        print(f"处理消息失败：{e}")
            
            asyncio.run(self._start_ws_server(host, port, handler))
        except Exception as e:
            print(f"⚠️ WebSocket 服务器启动失败：{e}")
    
    async def _start_ws_server(self, host, port, handler):
        """启动 WebSocket 服务器"""
        import websockets
        server = await websockets.serve(handler, host, port)
        print(f"✅ WebSocket 服务器：ws://{host}:{port}")
        await server.wait_closed()


# ============== 主函数 ==============
def main():
    parser = argparse.ArgumentParser(description="天童爱丽丝 - 完整桌面宠物")
    parser.add_argument("--mode", choices=["live2d", "avatar"], default="avatar",
                       help="显示模式：live2d 或 avatar")
    parser.add_argument("--config", type=str, help="配置文件路径")
    
    args = parser.parse_args()
    
    if not check_dependencies():
        sys.exit(1)
    
    pet = DesktopPetFull(mode=args.mode, config_path=args.config)
    pet.start()


if __name__ == "__main__":
    main()
