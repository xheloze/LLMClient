"""
天童爱丽丝 - 桌面宠物完整版
支持 Live2D 和差分图两种模式，透明悬浮窗，语音对话

使用方法:
1. python desktop_pet.py --mode live2d   # Live2D 模式
2. python desktop_pet.py --mode avatar   # 差分图模式
3. python desktop_pet.py --help          # 查看帮助
"""

import sys
import os
import json
import asyncio
import threading
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# 检查依赖
def check_dependencies():
    missing = []
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        missing.append("PyQt5")
    
    try:
        import websockets
    except ImportError:
        missing.append("websockets")
    
    if missing:
        print(f"❌ 缺少依赖：{', '.join(missing)}")
        print(f"✅ 请运行：pip install {' '.join(missing)}")
        return False
    return True


class DesktopPet:
    """桌面宠物主类"""
    
    def __init__(self, mode: str = "avatar", config_path: str = None):
        self.mode = mode
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.app = None
        self.window = None
        self.websocket_server = None
        
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        if self.mode == "live2d":
            return "config/live2d_config.json"
        else:
            return "config/avatar_config.json"
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 配置文件未找到：{self.config_path}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        if self.mode == "live2d":
            return {
                "model_name": "default",
                "model_path": "assets/models/default/",
                "window": {"width": 600, "height": 800, "x": 100, "y": 100},
                "expressions": {
                    "normal": "normal",
                    "happy": "smile",
                    "angry": "angry",
                    "sad": "sad"
                },
                "websocket": {"host": "127.0.0.1", "port": 8765}
            }
        else:
            return {
                "avatar_dir": "avatar/",
                "window": {"width": 500, "height": 700, "x": 100, "y": 100},
                "images": {
                    "normal": "normal.png",
                    "happy": "happy.png",
                    "angry": "angry.png",
                    "sad": "sad.png"
                },
                "websocket": {"host": "127.0.0.1", "port": 8766}
            }
    
    def start(self):
        """启动桌面宠物"""
        print("=" * 60)
        print(f"🎭 天童爱丽丝 - 桌面宠物 ({'Live2D' if self.mode == 'live2d' else '差分图'}模式)")
        print("=" * 60)
        
        # 创建 Qt 应用
        from PyQt5.QtWidgets import QApplication
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        # 创建窗口
        if self.mode == "live2d":
            self.window = Live2DWindow(self.config)
        else:
            self.window = AvatarWindow(self.config)
        
        # 启动 WebSocket 服务器
        ws_thread = threading.Thread(target=self._run_websocket_server, daemon=True)
        ws_thread.start()
        
        # 运行 Qt 主循环
        print(f"✅ 窗口已创建，位置：({self.config['window']['x']}, {self.config['window']['y']})")
        print(f"✅ WebSocket 服务器：ws://{self.config['websocket']['host']}:{self.config['websocket']['port']}")
        print("\n💡 提示:")
        print("   - 窗口将保持在桌面最上层")
        print("   - 支持鼠标穿透（点击穿透到桌面）")
        print("   - 按 Ctrl+C 退出程序")
        print("\n🚀 现在可以启动主程序：streamlit run webui.py")
        print("=" * 60)
        
        sys.exit(self.app.exec_())
    
    def _run_websocket_server(self):
        """运行 WebSocket 服务器"""
        host = self.config["websocket"]["host"]
        port = self.config["websocket"]["port"]
        
        async def handler(websocket, path):
            async for message in websocket:
                await self._handle_message(message)
        
        asyncio.run(self._start_server(host, port, handler))
    
    async def _start_server(self, host, port, handler):
        """启动 WebSocket 服务器"""
        import websockets
        self.websocket_server = await websockets.serve(handler, host, port)
        await self.websocket_server.wait_closed()
    
    async def _handle_message(self, message: str):
        """处理 WebSocket 消息"""
        try:
            data = json.loads(message)
            action = data.get("action")
            
            if action == "set_expression":
                expression = data.get("expression", "normal")
                self.window.update_expression(expression)
            elif action == "start_speaking":
                self.window.set_speaking(True)
            elif action == "stop_speaking":
                self.window.set_speaking(False)
                
        except Exception as e:
            print(f"处理消息失败：{e}")


class AvatarWindow:
    """差分图显示窗口"""
    
    def __init__(self, config: Dict[str, Any]):
        from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QPixmap, QColor
        
        self.config = config
        self.current_expression = "normal"
        self.is_speaking = False
        self.images = {}
        
        # 加载图片
        avatar_dir = Path(config.get("avatar_dir", "avatar/"))
        images_config = config.get("images", {})
        
        for expr, filename in images_config.items():
            img_path = avatar_dir / filename
            if img_path.exists():
                pixmap = QPixmap(str(img_path))
                if not pixmap.isNull():
                    self.images[expr] = pixmap
                    print(f"✅ 加载图片：{img_path}")
            else:
                print(f"⚠️ 图片不存在：{img_path}")
        
        # 创建窗口
        self.widget = QWidget()
        window_config = config.get("window", {})
        
        self.widget.setFixedSize(window_config.get("width", 500), window_config.get("height", 700))
        self.widget.setWindowTitle("天童爱丽丝")
        
        # 透明背景和置顶
        self.widget.setAttribute(Qt.WA_TranslucentBackground)
        self.widget.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        
        # 设置位置
        self.widget.move(window_config.get("x", 100), window_config.get("y", 100))
        
        # 创建标签
        self.label = QLabel(self.widget)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.widget.setLayout(layout)
        
        # 初始显示
        self._update_display()
        self.widget.show()
    
    def update_expression(self, expression: str):
        """更新表情"""
        if expression in self.images:
            self.current_expression = expression
            self._update_display()
            print(f"🎭 表情切换：{expression}")
        else:
            print(f"⚠️ 未知表情：{expression}")
    
    def set_speaking(self, speaking: bool):
        """设置说话状态"""
        self.is_speaking = speaking
        # TODO: 可以添加口型动画
    
    def _update_display(self):
        """更新显示"""
        pixmap = self.images.get(self.current_expression)
        if pixmap:
            # 缩放图片适应窗口
            scaled = pixmap.scaled(
                self.label.width(),
                self.label.height(),
                aspectRatioMode=True,
                transformMode=True
            )
            self.label.setPixmap(scaled)
        else:
            # 默认占位
            self.label.setText(f"{self.current_expression}\n(无图片)")


class Live2DWindow:
    """Live2D 显示窗口（简化版，待集成真实 Live2D SDK）"""
    
    def __init__(self, config: Dict[str, Any]):
        from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QPixmap, QColor
        
        self.config = config
        self.current_expression = "normal"
        self.is_speaking = False
        
        # 创建窗口
        self.widget = QWidget()
        window_config = config.get("window", {})
        
        self.widget.setFixedSize(window_config.get("width", 600), window_config.get("height", 800))
        self.widget.setWindowTitle(f"Live2D - {config.get('model_name', 'Model')}")
        
        # 透明背景和置顶
        self.widget.setAttribute(Qt.WA_TranslucentBackground)
        self.widget.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        
        # 设置位置
        self.widget.move(window_config.get("x", 100), window_config.get("y", 100))
        
        # 创建标签
        self.label = QLabel(self.widget)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(200, 200, 255, 150);
                border-radius: 20px;
                color: #333;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.widget.setLayout(layout)
        
        # 初始显示
        self._update_display()
        self.widget.show()
        
        print("⚠️ 当前为 Live2D 占位模式")
        print("💡 要使用真实 Live2D，请下载模型并集成 Cubism SDK")
    
    def update_expression(self, expression: str):
        """更新表情"""
        self.current_expression = expression
        self._update_display()
        print(f"🎭 Live2D 表情切换：{expression}")
    
    def set_speaking(self, speaking: bool):
        """设置说话状态"""
        self.is_speaking = speaking
    
    def _update_display(self):
        """更新显示"""
        self.label.setText(f"Live2D Mode\n表情：{self.current_expression}\n\n(占位显示)\n\n请集成真实 Live2D SDK")


def main():
    parser = argparse.ArgumentParser(description="天童爱丽丝 - 桌面宠物")
    parser.add_argument("--mode", choices=["live2d", "avatar"], default="avatar",
                       help="显示模式：live2d 或 avatar")
    parser.add_argument("--config", type=str, help="配置文件路径")
    
    args = parser.parse_args()
    
    if not check_dependencies():
        sys.exit(1)
    
    pet = DesktopPet(mode=args.mode, config_path=args.config)
    pet.start()


if __name__ == "__main__":
    main()
