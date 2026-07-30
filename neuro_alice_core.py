"""
天童爱丽丝 - 桌面宠物核心程序
功能：差分图显示 + 语音交互 + LLM对话 + DDSP变声
作者：Momotalk Project
"""

import sys
import os
import json
import threading
import time
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QIcon, QImage
import requests
import edge_tts
import asyncio
from playsound import playsound
import speech_recognition as sr
import tempfile
import re

# 全局配置
CONFIG_FILE = "config_alice.json"
PROMPT_FILE = "alice_prompt.txt"

class Config:
    """配置管理器"""
    def __init__(self):
        self.config = {}
        self.load()
    
    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            print(f"[错误] 配置文件 {CONFIG_FILE} 不存在")
            sys.exit(1)
    
    def get(self, *keys, default=None):
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

class ExpressionMapper:
    """表情映射器 - 将LLM输出的表情标记映射到图片文件"""
    def __init__(self, images_path):
        self.images_path = images_path
        self.mapping = {
            'normal': ['normal', 'plain', 'default', '平静', '普通'],
            'happy': ['happy', '开心', '高兴', '笑'],
            'smile': ['smile', '微笑'],
            'angry': ['angry', '生气', '愤怒'],
            'sad': ['sad', 'cry', '伤心', '哭', '难过'],
            'shy': ['shy', '害羞', '脸红'],
            'surprised': ['surprised', '惊讶', '吃惊'],
            'excited': ['excited', '兴奋', '激动'],
            'thinking': ['thinking', '思考', '疑惑'],
            'sleepy': ['sleepy', '困', '睡觉'],
            'love': ['love', '喜欢', '爱'],
            'cool': ['cool', '酷', '得意'],
            'embarrassed': ['embarrassed', '尴尬', '无奈'],
            'determined': ['determined', '坚定', '认真'],
        }
        self.available_images = self.scan_images()
    
    def scan_images(self):
        """扫描可用的图片文件"""
        available = {}
        if not os.path.exists(self.images_path):
            os.makedirs(self.images_path)
            return available
        
        for filename in os.listdir(self.images_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                name = os.path.splitext(filename)[0].lower()
                available[name] = os.path.join(self.images_path, filename)
        return available
    
    def get_image_path(self, emotion_text):
        """根据情感文本获取图片路径"""
        emotion_text = emotion_text.lower()
        
        # 直接匹配
        if emotion_text in self.available_images:
            return self.available_images[emotion_text]
        
        # 模糊匹配
        for expr_name, keywords in self.mapping.items():
            for keyword in keywords:
                if keyword in emotion_text:
                    if expr_name in self.available_images:
                        return self.available_images[expr_name]
        
        # 默认返回第一个可用图片
        if self.available_images:
            return list(self.available_images.values())[0]
        
        return None

class LLMClient:
    """LLM客户端 - 使用SiliconFlow免费API"""
    def __init__(self, config):
        self.api_key = config.get('ai', 'api_key')
        self.model = config.get('ai', 'model', default='Qwen/Qwen2.5-7B-Instruct')
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.prompt = self.load_prompt()
        self.history = []
    
    def load_prompt(self):
        if os.path.exists(PROMPT_FILE):
            with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        return "你是爱丽丝，千年科技学院游戏开发部的一年级学生。"
    
    def chat(self, user_message):
        """发送消息并获取回复"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.history.append({"role": "user", "content": user_message})
        
        # 保留最近10轮对话
        if len(self.history) > 20:
            self.history = self.history[-20:]
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.prompt},
                *self.history
            ],
            "max_tokens": 300,
            "temperature": 0.8
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            assistant_message = result['choices'][0]['message']['content']
            self.history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        except Exception as e:
            print(f"[LLM错误] {e}")
            return "邦邦卡邦!! 爱丽丝的网络连接好像出问题了...（信号不良）"

class TTSProcessor:
    """语音处理器 - Edge-TTS + DDSP变声"""
    def __init__(self, config):
        self.config = config
        self.ddsp_enabled = config.get('voice', 'ddsp_enabled', default=False)
        self.ddsp_model_path = config.get('voice', 'ddsp_model_path', default='')
        self.edge_voice = config.get('voice', 'edge_voice', default='zh-CN-XiaoxiaoNeural')
        self.temp_dir = tempfile.gettempdir()
        
        if self.ddsp_enabled and not os.path.exists(self.ddsp_model_path):
            print(f"[警告] DDSP模型文件不存在: {self.ddsp_model_path}")
            self.ddsp_enabled = False
    
    async def generate_speech(self, text, output_file):
        """生成语音（Edge-TTS）"""
        communicate = edge_tts.Communicate(text, self.edge_voice)
        await communicate.save(output_file)
        return output_file
    
    def apply_ddsp(self, input_file, output_file):
        """应用DDSP变声（预留接口）"""
        # TODO: 集成ddsp-svc库进行推理
        # 目前暂时复制原文件
        import shutil
        shutil.copy(input_file, output_file)
        print("[DDSP] 变声处理完成")
    
    def speak(self, text):
        """播放语音"""
        async def _speak():
            temp_input = os.path.join(self.temp_dir, f"alice_input_{int(time.time())}.mp3")
            temp_output = os.path.join(self.temp_dir, f"alice_output_{int(time.time())}.wav")
            
            try:
                # 生成基础语音
                await self.generate_speech(text, temp_input)
                
                # 应用DDSP变声
                if self.ddsp_enabled:
                    self.apply_ddsp(temp_input, temp_output)
                    playsound(temp_output)
                else:
                    playsound(temp_input)
                
                # 清理临时文件
                for f in [temp_input, temp_output]:
                    if os.path.exists(f):
                        try:
                            os.remove(f)
                        except:
                            pass
            except Exception as e:
                print(f"[TTS错误] {e}")
        
        # 在新线程中运行
        thread = threading.Thread(target=lambda: asyncio.run(_speak()))
        thread.daemon = True
        thread.start()

class STTListener:
    """语音识别监听器"""
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.running = False
    
    def listen_once(self):
        """监听一次语音输入"""
        try:
            with sr.Microphone() as source:
                print("[STT] 正在监听...")
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language='zh-CN')
                return text
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"[STT错误] {e}")
            return None

class AliceWindow(QMainWindow):
    """爱丽丝桌面窗口"""
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.expression_mapper = ExpressionMapper(config.get('avatar', 'images_path', default='assets/avatar'))
        self.llm = LLMClient(config)
        self.tts = TTSProcessor(config)
        self.stt = STTListener()
        
        self.current_emotion = 'normal'
        self.click_through = False
        
        self.init_ui()
        self.show()
    
    def init_ui(self):
        """初始化界面"""
        # 窗口设置
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # 尺寸和位置
        width = self.config.get('avatar', 'window_width', default=400)
        height = self.config.get('avatar', 'window_height', default=600)
        
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - width - 50
        y = screen.height() - height - 50
        
        self.setGeometry(x, y, width, height)
        
        # 图片标签
        self.image_label = QLabel(self)
        self.image_label.setGeometry(0, 0, width, height)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # 加载初始图片
        self.update_image('normal')
        
        # 系统托盘
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromStyle(QStyle.SP_ComputerIcon))
        self.tray_menu = QMenu()
        
        speak_action = QAction("对爱丽丝说话", self)
        speak_action.triggered.connect(self.on_speak_trigger)
        self.tray_menu.addAction(speak_action)
        
        toggle穿透_action = QAction("切换鼠标穿透", self)
        toggle穿透_action.triggered.connect(self.toggle_click_through)
        self.tray_menu.addAction(toggle穿透_action)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        self.tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
        # 右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def update_image(self, emotion):
        """更新显示的图片"""
        image_path = self.expression_mapper.get_image_path(emotion)
        
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(
                self.image_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
            self.current_emotion = emotion
        else:
            print(f"[警告] 图片不存在: {image_path}")
    
    def parse_expression(self, text):
        """从LLM回复中解析表情标记"""
        # 支持格式：【表情：happy】或 [表情：开心]
        match = re.search(r'【表情：(.*?)】|\[表情：(.*?)\]', text)
        if match:
            emotion = match.group(1) or match.group(2)
            return emotion.strip()
        return None
    
    def process_message(self, user_input):
        """处理用户消息"""
        # 获取LLM回复
        response = self.llm.chat(user_input)
        print(f"[爱丽丝] {response}")
        
        # 解析表情
        emotion = self.parse_expression(response)
        if emotion:
            self.update_image(emotion)
        
        # 播放语音
        self.tts.speak(response)
    
    def on_speak_trigger(self):
        """触发语音输入"""
        text = self.stt.listen_once()
        if text:
            print(f"[用户] {text}")
            self.process_message(text)
    
    def toggle_click_through(self):
        """切换鼠标穿透"""
        self.click_through = not self.click_through
        self.setAttribute(Qt.WA_TransparentForMouseEvents, self.click_through)
        status = "开启" if self.click_through else "关闭"
        self.tray_icon.showMessage("提示", f"鼠标穿透已{status}")
    
    def show_context_menu(self, pos):
        """显示右键菜单"""
        self.tray_menu.exec_(self.mapToGlobal(pos))
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 实现拖拽"""
        if event.button() == Qt.LeftButton and not self.click_through:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖拽窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None and not self.click_through:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

def main():
    """主函数"""
    print("=" * 50)
    print("天童爱丽丝 桌面宠物启动中...")
    print("=" * 50)
    
    # 加载配置
    config = Config()
    
    # 检查API Key
    api_key = config.get('ai', 'api_key')
    if not api_key:
        print("[错误] 请在 config_alice.json 中配置 SiliconFlow API Key")
        print("获取地址：https://cloud.siliconflow.cn/")
        input("按回车退出...")
        sys.exit(1)
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建窗口
    window = AliceWindow(config)
    
    print("\n✓ 启动成功！")
    print("提示：右键点击窗口可进行操作")
    print("      拖拽窗口可调整位置")
    print("=" * 50)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
