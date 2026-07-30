import os
import sys
import json
import time
import threading
import subprocess
import tempfile
from pathlib import Path

# --- 配置部分 (傻瓜式修改这里) ---
CONFIG_FILE = "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "siliconflow_api_key": "",  # 【必填】去 https://cloud.siliconflow.cn/ 获取免费 Key
    "ddsp_model_path": "",      # 【必填】您的 DDSP 模型路径 (.pth)
    "ddsp_script_path": "",     # 【必填】DDSP 推理脚本路径 (例如 ddsp-inference/infer.py)
    "python_path": sys.executable, # 自动使用当前环境的 Python
    "avatar_folder": "assets/avatar",
    "tts_voice": "zh-CN-XiaoxiaoNeural" # 基础 TTS 音色 (女声，适合转爱丽丝)
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("⚠️ 未找到配置文件，正在生成 config.json...")
        print("❗ 请先编辑 config.json 填入 API Key 和 DDSP 路径后再运行！")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        sys.exit(0)
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

# 检查必要配置
if not config["siliconflow_api_key"]:
    print("❌ 错误：请在 config.json 中填入 siliconflow_api_key")
    sys.exit(1)
if not config["ddsp_model_path"] or not config["ddsp_script_path"]:
    print("⚠️ 警告：未配置 DDSP 路径，将仅使用基础 TTS 声音。如需变声请填写路径。")

# --- 核心功能模块 ---

# 1. AI 对话模块 (SiliconFlow)
import requests

SYSTEM_PROMPT = """
(此处省略您提供的超长天童爱丽丝 Prompt，实际使用时请完整粘贴到这里)
你只是爱丽丝，一名千年科技学院的游戏开发部的一年级学生而已...
(为了代码简洁，实际文件中请填入完整 Prompt)
"""

def get_ai_response(user_text):
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config['siliconflow_api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct", # 免费且智能
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        content = data['choices'][0]['message']['content']
        
        # 解析表情标记 (假设格式为【表情：happy】)
        emotion = "normal"
        if "【表情：" in content:
            start = content.find("【表情：") + 5
            end = content.find("】", start)
            if end > start:
                emotion = content[start:end]
                # 从文本中移除标记
                content = content.replace(f"【表情：{emotion}】", "")
        
        return content, emotion
    except Exception as e:
        print(f"AI 请求失败: {e}")
        return "爱丽丝的网络连接好像出了点问题...邦邦卡邦！", "sad"

# 2. 语音流水线模块 (TTS -> DDSP -> Play)
import edge_tts
import asyncio
import playsound
from playsound import playsound as sync_playsound

async def generate_base_tts(text, output_path):
    """使用 Edge-TTS 生成基础语音"""
    communicate = edge_tts.Communicate(text, config["tts_voice"])
    await communicate.save(output_path)

def run_ddsp_inference(input_wav, output_wav):
    """调用本地 DDSP 脚本进行推理"""
    if not config["ddsp_script_path"]:
        return False
    
    cmd = [
        config["python_path"],
        config["ddsp_script_path"],
        "-m", config["ddsp_model_path"],
        "-i", input_wav,
        "-o", output_wav
    ]
    # 注意：这里假设您的 DDSP 脚本支持命令行参数 -m, -i, -o
    # 如果脚本不同，请修改此处参数
    try:
        print(f"🎤 正在进行 DDSP 音色转换... (GPU 加速中)")
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ DDSP 推理失败: {e.stderr.decode()}")
        return False

def speak_alice(text, emotion):
    """完整的说话流程"""
    if not text.strip():
        return

    # 创建临时文件
    temp_dir = tempfile.gettempdir()
    base_wav = os.path.join(temp_dir, "alice_base.wav")
    final_wav = os.path.join(temp_dir, "alice_final.wav")

    try:
        # 步骤 1: 生成基础语音
        print(f"💬 爱丽丝正在说话: {text[:20]}...")
        asyncio.run(generate_base_tts(text, base_wav))
        
        # 步骤 2: DDSP 变声 (如果配置了)
        if config["ddsp_script_path"] and os.path.exists(config["ddsp_script_path"]):
            success = run_ddsp_inference(base_wav, final_wav)
            if success:
                sync_playsound(final_wav)
            else:
                print("⚠️ DDSP 失败，播放原声")
                sync_playsound(base_wav)
        else:
            # 没配置 DDSP，直接播
            sync_playsound(base_wav)
            
    except Exception as e:
        print(f"🔊 播放出错: {e}")
    finally:
        # 清理临时文件
        for f in [base_wav, final_wav]:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass

# 3. 桌面宠物界面 (PyQt5)
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QIcon

class VoiceThread(QThread):
    def __init__(self, text, emotion):
        super().__init__()
        self.text = text
        self.emotion = emotion
    
    def run(self):
        speak_alice(self.text, self.emotion)

class AliceDesktopPet(QMainWindow):
    update_emotion_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("天童爱丽丝 - 桌面宠物")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始化变量
        self.current_emotion = "normal"
        self.avatar_map = {}
        self.load_avatars()
        
        # 界面
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.set_avatar("normal")
        
        # 模拟交互 (右键菜单简化为双击说话测试)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_interaction)
        self.timer.start(1000) # 每秒检查一次
        
        self.show()
        print("✅ 爱丽丝已启动！右键点击托盘图标退出 (需自行实现托盘) 或直接关闭窗口。")
        print("💡 演示模式：每隔 10 秒会自动说一句话，您可以修改代码接入麦克风。")

    def load_avatars(self):
        """加载差分图"""
        folder = config["avatar_folder"]
        emotions = ["normal", "happy", "sad", "angry", "shy", "surprised"]
        for emo in emotions:
            path = os.path.join(folder, f"{emo}.png")
            if os.path.exists(path):
                self.avatar_map[emo] = path
            else:
                # 尝试其他命名
                if emo == "normal" and os.path.exists(os.path.join(folder, "plain.png")):
                    self.avatar_map[emo] = os.path.join(folder, "plain.png")
                else:
                    self.avatar_map[emo] = None # 占位

    def set_avatar(self, emotion):
        if emotion in self.avatar_map and self.avatar_map[emotion]:
            pixmap = QPixmap(self.avatar_map[emotion])
            # 缩放适应
            scaled = pixmap.scaled(300, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(scaled)
            self.label.resize(scaled.size())
            self.resize(scaled.size())
            self.current_emotion = emotion
        else:
            print(f"⚠️ 未找到表情图片: {emotion}")

    def check_interaction(self):
        # 这里可以接入麦克风识别逻辑
        # 为了演示，我们模拟一个自动对话
        if not hasattr(self, 'last_speak_time'):
            self.last_speak_time = 0
            self.demo_count = 0
            
        if time.time() - self.last_speak_time > 10: # 每 10 秒说一次
            self.demo_count += 1
            messages = [
                ("邦邦卡邦！sensei，爱丽丝发现了一个新游戏！", "happy"),
                ("经验值增加了！爱丽丝等级提升了！", "surprised"),
                ("小桃又借走了我的游戏机...苦呀西。", "sad"),
                ("今天的任务是什么？爱丽丝随时待命！", "normal")
            ]
            msg, emo = messages[self.demo_count % len(messages)]
            self.respond(msg, emo)
            self.last_speak_time = time.time()

    def respond(self, text, emotion):
        # 切换表情
        self.set_avatar(emotion)
        # 异步播放声音
        self.voice_thread = VoiceThread(text, emotion)
        self.voice_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 简单的启动检查
    if not os.path.exists(config["avatar_folder"]):
        os.makedirs(config["avatar_folder"])
        print(f"📁 已创建文件夹: {config['avatar_folder']}")
        print("请将差分图 (normal.png, happy.png 等) 放入该文件夹。")
    
    pet = AliceDesktopPet()
    sys.exit(app.exec_())
