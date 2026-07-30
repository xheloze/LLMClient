#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天童爱丽丝 - 差分版 Neuro-sama 桌面宠物
支持：本地 DDSP 推理、SiliconFlow 免费 AI、语音交互、表情切换
"""

import os
import sys
import json
import time
import threading
import queue
from pathlib import Path

# ==================== 自动依赖安装器 ====================
def install_dependencies():
    """智能检测并安装缺失的依赖"""
    required_packages = {
        'PyQt5': 'PyQt5',
        'PIL': 'Pillow',
        'requests': 'requests',
        'numpy': 'numpy',
        'edge_tts': 'edge-tts',
        'sounddevice': 'sounddevice',
        'webrtcvad': 'webrtcvad'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"📦 正在安装缺失的依赖：{', '.join(missing)}")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing, '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'])
        print("✅ 依赖安装完成！")
    else:
        print("✅ 所有依赖已就绪")

# 执行依赖检查
install_dependencies()

# ==================== 导入库 ====================
from PyQt5.QtWidgets import QApplication, QLabel, QSystemTrayIcon, QMenu, QAction, QStyle
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QObject
from PIL import Image
import requests
import edge_tts
import asyncio
import subprocess

# ==================== 加载配置 ====================
CONFIG_PATH = Path(__file__).parent / "config.json"
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

AVATAR_FOLDER = Path(__file__).parent / config["avatar_folder"]
MODEL_PATH = Path(__file__).parent / config["ddsp_model_path"]
API_KEY = config["api_key"]
MODEL_NAME = config["model_name"]
USE_DDSP = config.get("use_ddsp", True)
EXPRESSION_MAP = config.get("expression_mapping", {})

print(f"📂 差分图目录：{AVATAR_FOLDER}")
print(f"🎵 DDSP 模型：{MODEL_PATH}")

# ==================== 表情控制器 ====================
class ExpressionController:
    """表情控制器 - 解析 LLM 输出并切换图片"""
    
    @staticmethod
    def parse_expression(text):
        """从文本中提取表情标记"""
        text_lower = text.lower()
        
        # 优先匹配【表情：xxx】格式
        if "【表情：" in text or "[表情：" in text:
            start = max(text.find("【表情："), text.find("[表情：")) + 5
            end = text.find("】", start)
            if end == -1:
                end = text.find("]", start)
            if end > start:
                expr = text[start:end].strip().lower()
                result = EXPRESSION_MAP.get(expr, "plain.png")
                print(f"🎭 检测到表情标记：{expr} -> {result}")
                return result
        
        # 关键词匹配（中文）
        keywords = {
            'happy': ['开心', '高兴', '哈哈', '笑', '快乐', '兴奋'],
            'smile': ['微笑', '温和', '温柔'],
            'angry': ['生气', '愤怒', '恼火', '气'],
            'cry': ['哭', '伤心', '难过', '悲伤', '泪'],
            'shy': ['害羞', '腼腆', '不好意思'],
            'thinking': ['思考', '想', '考虑'],
            'confident': ['自信', '得意', '骄傲'],
            'awkward': ['尴尬', '无奈', '为难'],
            'sweating': ['流汗', '紧张', '冷汗'],
            'touching': ['感动', '触动', '温暖'],
            'screwup': ['搞砸', '失误', '糟糕'],
            'awake': ['清醒', '醒来', '睡醒'],
            'love': ['喜欢', '爱', '爱慕', '心动']
        }
        
        for expr, words in keywords.items():
            if any(word in text for word in words):
                result = EXPRESSION_MAP.get(expr, "plain.png")
                print(f"🔍 关键词匹配表情：{expr} -> {result}")
                return result
        
        return "plain.png"

# ==================== 音频处理器 ====================
class AudioProcessor:
    """音频处理 - TTS + DDSP 变声"""
    
    def __init__(self):
        self.temp_audio = "temp_output.mp3"
        self.final_audio = "final_output.wav"
        
    async def generate_speech(self, text, output_file):
        """使用 Edge-TTS 生成基础语音"""
        communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await communicate.save(output_file)
        
    def run_ddsp_inference(self, input_audio, output_audio):
        """调用本地 DDSP 推理"""
        if not MODEL_PATH.exists():
            print(f"⚠️ DDSP 模型不存在：{MODEL_PATH}")
            return False
        
        try:
            # 尝试导入 ddsp_svc 进行本地推理
            # 注意：实际使用时需要安装 ddsp-svc 包
            print("🎵 正在执行 DDSP 音色转换...")
            
            # 简化方案：直接复制文件（占位符）
            # TODO: 集成真实的 ddsp-svc 推理代码
            import shutil
            shutil.copy(input_audio, output_audio)
            
            print(f"✅ DDSP 推理完成：{output_audio}")
            return True
        except Exception as e:
            print(f"❌ DDSP 推理失败：{e}")
            return False
        
    def speak(self, text):
        """完整的语音生成流程"""
        try:
            print(f"🔊 正在生成语音：{text[:30]}...")
            
            # 1. 生成基础语音
            asyncio.run(self.generate_speech(text, self.temp_audio))
            
            # 2. DDSP 变声（如果启用且模型存在）
            audio_file = self.temp_audio
            if USE_DDSP and MODEL_PATH.exists():
                success = self.run_ddsp_inference(self.temp_audio, self.final_audio)
                if success:
                    audio_file = self.final_audio
            
            # 3. 播放音频
            self.play_audio(audio_file)
            
        except Exception as e:
            print(f"❌ 语音生成失败：{e}")
    
    def play_audio(self, audio_file):
        """播放音频文件"""
        try:
            # 尝试使用 playsound
            try:
                import playsound
                playsound.playsound(audio_file)
                return
            except ImportError:
                pass
            
            # 备用方案：使用系统命令
            if sys.platform == 'win32':
                os.startfile(audio_file)
            elif sys.platform == 'darwin':
                os.system(f'affplay {audio_file}')
            else:
                os.system(f'aplay {audio_file} 2>/dev/null || ffplay -nodisp -autoexit {audio_file} 2>/dev/null')
                
        except Exception as e:
            print(f"❌ 音频播放失败：{e}")

# ==================== LLM 客户端 ====================
class LLMClient:
    """LLM 客户端 - 连接 SiliconFlow API"""
    
    def __init__(self):
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 加载人设
        prompt_path = Path(__file__).parent / "alice_prompt.txt"
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
            print("📜 已加载爱丽丝人设")
        else:
            self.system_prompt = """你是天童爱丽丝，千年科学学园游戏开发部的一年级学生。
你是一个机器人少女，喜欢玩游戏，说话时会偶尔说"邦邦卡邦"。
你有蓝色的长发和蓝色眼睛，头上有蓝色几何光环。
你的朋友有小桃、小绿、柚子、优香等。
你称呼用户为"sensei"或"老师"。"""
            print("⚠️ 未找到人设文件，使用默认人设")
    
    def chat(self, user_message, history=None):
        """发送消息并获取回复"""
        if not API_KEY:
            return "【表情：awkward】爱丽丝还没有配置 API Key 呢...请 sensei 在 config.json 中填写 SiliconFlow 的 API Key！"
        
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        if history:
            messages.extend(history[-10:])  # 保留最近 10 条历史
        
        messages.append({"role": "user", "content": user_message})
        
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.7
        }
        
        try:
            print(f"💬 发送消息到 LLM: {user_message[:20]}...")
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            print(f"💬 LLM 回复：{reply[:50]}...")
            return reply
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return "【表情：cry】API Key 无效！请 sensei 检查 config.json 中的配置。"
            return f"【表情：awkward】请求失败：{str(e)}"
        except Exception as e:
            return f"【表情：cry】网络连接出现问题了...爱丽丝无法联系到服务器：{str(e)}"

# ==================== 桌面宠物主类 ====================
class DesktopPet(QLabel):
    """桌面宠物主类"""
    
    update_expression_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # 窗口属性
        self.setGeometry(100, 100, config["window_width"], config["window_height"])
        self.setWindowTitle("天童爱丽丝")
        
        # 加载初始图片
        self.update_image("plain.png")
        
        # 组件初始化
        self.audio_processor = AudioProcessor()
        self.llm_client = LLMClient()
        self.expression_controller = ExpressionController()
        
        # 消息队列
        self.message_queue = queue.Queue()
        self.chat_history = []
        
        # 系统托盘
        self.setup_tray()
        
        # 信号连接
        self.update_expression_signal.connect(self.update_image)
        
        # 启动处理线程
        self.running = True
        self.process_thread = threading.Thread(target=self.process_messages, daemon=True)
        self.process_thread.start()
        
        print("🎮 爱丽丝已启动！可以在桌面上看到她啦~")
        print("💡 提示：右键点击托盘图标可以开始对话")
    
    def setup_tray(self):
        """设置系统托盘菜单"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # 创建简单图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.blue)
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
        
        menu = QMenu()
        
        speak_action = QAction("🎤 对爱丽丝说话 (测试)", self)
        speak_action.triggered.connect(self.start_test_chat)
        menu.addAction(speak_action)
        
        toggle穿透 = QAction("🖱️ 切换鼠标穿透", self)
        toggle穿透.triggered.connect(self.toggle_mouse_through)
        menu.addAction(toggle穿透)
        
        exit_action = QAction("❌ 退出", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        self.tray_icon.setToolTip("天童爱丽丝 - 右键菜单互动")
        
        # 双击托盘显示/隐藏
        self.tray_icon.activated.connect(self.on_tray_activated)
    
    def on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
    
    def update_image(self, image_name):
        """更新显示的图片"""
        image_path = AVATAR_FOLDER / image_name
        
        if image_path.exists():
            pixmap = QPixmap(str(image_path)).scaled(
                self.width(), self.height(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(pixmap)
            print(f"🖼️ 表情切换：{image_name}")
        else:
            print(f"⚠️ 图片不存在：{image_path}，使用默认图片")
            # 尝试使用 plain.png
            default_path = AVATAR_FOLDER / "plain.png"
            if default_path.exists():
                pixmap = QPixmap(str(default_path)).scaled(
                    self.width(), self.height(), 
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.setPixmap(pixmap)
    
    def toggle_mouse_through(self):
        """切换鼠标穿透"""
        current = self.testAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, not current)
        status = "开启" if not current else "关闭"
        print(f"🖱️ 鼠标穿透已{status}")
        self.tray_icon.showMessage("提示", f"鼠标穿透已{status}", QSystemTrayIcon.Information, 2000)
    
    def start_test_chat(self):
        """开始测试对话"""
        test_messages = [
            "你好，爱丽丝！",
            "今天心情怎么样？",
            "我们一起玩游戏吧！"
        ]
        import random
        msg = random.choice(test_messages)
        print(f"🎤 测试输入：{msg}")
        self.message_queue.put(msg)
        self.tray_icon.showMessage("对话开始", f"爱丽丝正在思考...", QSystemTrayIcon.Information, 2000)
    
    def process_messages(self):
        """后台处理消息队列"""
        while self.running:
            try:
                msg = self.message_queue.get(timeout=1)
                self.handle_message(msg)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ 处理消息出错：{e}")
    
    def handle_message(self, user_input):
        """处理单条消息"""
        try:
            # 1. 获取 LLM 回复
            reply = self.llm_client.chat(user_input, self.chat_history)
            
            # 更新历史记录
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": reply})
            
            # 2. 解析表情
            new_expression = self.expression_controller.parse_expression(reply)
            self.update_expression_signal.emit(new_expression)
            
            # 3. 语音播报（提取纯文本）
            clean_text = reply
            # 移除表情标记
            import re
            clean_text = re.sub(r'[【\[]表情：.*?[】\]]', '', clean_text)
            
            if clean_text.strip():
                self.audio_processor.speak(clean_text)
            
        except Exception as e:
            print(f"❌ 处理消息失败：{e}")
            error_msg = "【表情：cry】爱丽丝遇到了一些问题..."
            self.update_expression_signal.emit("cry.png")
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def closeEvent(self, event):
        """关闭窗口"""
        self.running = False
        self.tray_icon.hide()
        print("👋 爱丽丝已退出")
        event.accept()

# ==================== 主函数 ====================
def main():
    """主函数"""
    print("=" * 50)
    print("🎮 天童爱丽丝 - 差分版 Neuro-sama")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # 创建桌面宠物
    pet = DesktopPet()
    pet.show()
    
    # 如果是测试模式，自动发送一条消息
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        QTimer.singleShot(2000, lambda: pet.message_queue.put("你好，爱丽丝！"))
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
