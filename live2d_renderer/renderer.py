"""
Live2D 渲染器 - 基于 PyQt5 和 Live2D Cubism SDK
支持桌面悬浮窗、表情切换、口型同步等功能
"""

import sys
import json
import asyncio
import websockets
import threading
from typing import Optional, Dict, Any

try:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QMovie, QPixmap, QPainter, QBrush, QColor
    LIVE2D_AVAILABLE = True
except ImportError:
    LIVE2D_AVAILABLE = False
    print("警告：PyQt5 未安装，Live2D 渲染将不可用。请运行：pip install PyQt5")


class Live2DRenderer:
    """Live2D 渲染器主类"""
    
    def __init__(self, config_path: str = "config/live2d_config.json"):
        self.config = self._load_config(config_path)
        self.current_expression = "normal"
        self.is_speaking = False
        self.websocket_server = None
        self.app = None
        self.window = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件未找到：{config_path}，使用默认配置")
            return {
                "model_name": "default",
                "window": {"width": 600, "height": 800},
                "websocket": {"host": "127.0.0.1", "port": 8765}
            }
    
    def start(self):
        """启动渲染器"""
        if not LIVE2D_AVAILABLE:
            print("Live2D 渲染器无法启动：缺少 PyQt5 依赖")
            return
        
        # 创建独立的线程运行 Qt 应用
        qt_thread = threading.Thread(target=self._run_qt_app, daemon=True)
        qt_thread.start()
        
        # 启动 WebSocket 服务器
        asyncio.run(self._start_websocket_server())
    
    def _run_qt_app(self):
        """运行 Qt 应用程序"""
        self.app = QApplication(sys.argv)
        self.window = Live2DWindow(self.config)
        self.window.show()
        sys.exit(self.app.exec_())
    
    async def _start_websocket_server(self):
        """启动 WebSocket 服务器接收控制指令"""
        host = self.config["websocket"]["host"]
        port = self.config["websocket"]["port"]
        
        async def handler(websocket, path):
            async for message in websocket:
                await self._handle_message(message)
        
        self.websocket_server = await websockets.serve(handler, host, port)
        print(f"Live2D WebSocket 服务器已启动：ws://{host}:{port}")
        await self.websocket_server.wait_closed()
    
    async def _handle_message(self, message: str):
        """处理 WebSocket 消息"""
        try:
            data = json.loads(message)
            action = data.get("action")
            
            if action == "set_expression":
                expression = data.get("expression", "normal")
                self.set_expression(expression)
            elif action == "start_speaking":
                self.start_speaking()
            elif action == "stop_speaking":
                self.stop_speaking()
            elif action == "play_motion":
                motion = data.get("motion", "idle")
                self.play_motion(motion)
                
        except json.JSONDecodeError:
            print(f"无效的 JSON 消息：{message}")
    
    def set_expression(self, expression: str):
        """设置表情"""
        if expression in self.config.get("expressions", {}):
            self.current_expression = expression
            if self.window:
                self.window.update_expression(expression)
            print(f"表情已切换：{expression}")
        else:
            print(f"未知表情：{expression}")
    
    def start_speaking(self):
        """开始说话（启用口型动画）"""
        self.is_speaking = True
        if self.window:
            self.window.set_speaking(True)
    
    def stop_speaking(self):
        """停止说话"""
        self.is_speaking = False
        if self.window:
            self.window.set_speaking(False)
    
    def play_motion(self, motion: str):
        """播放动作"""
        if self.window:
            self.window.play_motion(motion)


class Live2DWindow(QWidget):
    """Live2D 显示窗口"""
    
    update_signal = pyqtSignal(str)
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.current_expression = "normal"
        self.is_speaking = False
        
        # 窗口设置
        self._setup_window()
        # UI 初始化
        self._setup_ui()
        # 连接信号
        self.update_signal.connect(self._update_display)
    
    def _setup_window(self):
        """设置窗口属性"""
        window_config = self.config.get("window", {})
        self.setFixedSize(window_config.get("width", 600), window_config.get("height", 800))
        self.setWindowTitle(f"Live2D - {self.config.get('model_name', 'Model')}")
        
        # 透明背景设置
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout()
        self.display_label = QLabel(self)
        self.display_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.display_label)
        self.setLayout(layout)
        
        # 初始显示
        self._update_display("normal")
    
    def _update_display(self, expression: str):
        """更新显示内容"""
        # TODO: 实际项目中这里应该加载 Live2D 模型
        # 当前使用占位实现
        pixmap = QPixmap(400, 600)
        pixmap.fill(QColor(255, 255, 255, 0))  # 透明背景
        
        painter = QPainter(pixmap)
        painter.setBrush(QBrush(QColor(200, 200, 255, 200)))
        painter.drawRoundedRect(50, 50, 300, 500, 20, 20)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, f"{expression}\n(placeholder)")
        painter.end()
        
        self.display_label.setPixmap(pixmap)
    
    def update_expression(self, expression: str):
        """更新表情（线程安全）"""
        self.update_signal.emit(expression)
    
    def set_speaking(self, speaking: bool):
        """设置说话状态"""
        self.is_speaking = speaking
        # TODO: 触发动画
    
    def play_motion(self, motion: str):
        """播放动作"""
        print(f"播放动作：{motion}")
        # TODO: 实现动作播放


def main():
    """主函数"""
    renderer = Live2DRenderer()
    renderer.start()


if __name__ == "__main__":
    main()
