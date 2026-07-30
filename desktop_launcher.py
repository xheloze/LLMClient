"""
桌面挂件启动器 - 一键启动 Live2D/差分图 桌面挂件
支持透明背景、始终置顶、鼠标穿透等功能
"""

import sys
import os
import json
import subprocess
import threading
from pathlib import Path


def check_dependencies():
    """检查依赖是否安装"""
    missing = []
    
    try:
        import PyQt5
    except ImportError:
        missing.append("PyQt5")
    
    try:
        import websockets
    except ImportError:
        missing.append("websockets")
    
    if missing:
        print(f"缺少依赖：{', '.join(missing)}")
        print(f"请运行：pip install {' '.join(missing)}")
        return False
    
    return True


def start_live2d_renderer():
    """启动 Live2D 渲染器"""
    print("正在启动 Live2D 渲染器...")
    renderer_path = Path(__file__).parent / "live2d_renderer" / "renderer.py"
    
    if not renderer_path.exists():
        print(f"错误：找不到渲染器文件 {renderer_path}")
        return None
    
    # 在新进程中启动渲染器
    process = subprocess.Popen(
        [sys.executable, str(renderer_path)],
        cwd=str(Path(__file__).parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Live2D 渲染器已启动")
    return process


def start_overlay_window():
    """启动桌面悬浮窗（简化版）"""
    print("正在启动桌面悬浮窗...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QPixmap, QPainter, QColor
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        window = QWidget()
        window.setFixedSize(400, 600)
        window.setWindowTitle("天童爱丽丝 - 桌面挂件")
        
        # 设置窗口属性
        window.setAttribute(Qt.WA_TranslucentBackground)
        window.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowTransparentForInput  # 鼠标穿透
        )
        
        # 创建布局
        layout = QVBoxLayout()
        label = QLabel(window)
        label.setAlignment(Qt.AlignCenter)
        label.setText("爱丽丝在这里！\n\n右键点击退出")
        label.setStyleSheet("""
            QLabel {
                background-color: rgba(200, 200, 255, 180);
                border-radius: 20px;
                color: #333;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        layout.addWidget(label)
        window.setLayout(layout)
        
        # 显示窗口
        window.show()
        
        print("桌面挂件已启动 (右键点击退出)")
        
        return app.exec_()
        
    except Exception as e:
        print(f"启动桌面挂件失败：{e}")
        return 1


def main():
    """主函数"""
    print("=" * 50)
    print("天童爱丽丝 - 桌面挂件启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        input("按回车键退出...")
        return
    
    # 选择模式
    print("\n请选择模式:")
    print("1. Live2D 模式 (需要 Live2D 模型)")
    print("2. 差分图模式 (使用静态图片)")
    print("3. 仅桌面挂件 (简单悬浮窗)")
    print("4. 退出")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        # Live2D 模式
        config_path = Path(__file__).parent / "config" / "live2d_config.json"
        if not config_path.exists():
            print("错误：找不到配置文件，请先配置 live2d_config.json")
            input("按回车键退出...")
            return
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        model_path = Path(__file__).parent / config.get("model_path", "")
        if not model_path.exists():
            print(f"警告：模型路径不存在 {model_path}")
            print("请确保已下载并放置 Live2D 模型文件")
        
        # 启动渲染器
        renderer_process = start_live2d_renderer()
        
        if renderer_process:
            print("\n提示：现在可以启动主程序 streamlit run webui.py")
            print("按 Ctrl+C 停止渲染器")
            
            try:
                renderer_process.wait()
            except KeyboardInterrupt:
                print("\n正在关闭...")
                renderer_process.terminate()
    
    elif choice == "2":
        # 差分图模式
        avatar_dir = Path(__file__).parent / "avatar"
        if not avatar_dir.exists():
            print("错误：找不到 avatar 目录")
            input("按回车键退出...")
            return
        
        images = list(avatar_dir.glob("*.png")) + list(avatar_dir.glob("*.jpg"))
        if not images:
            print("错误：avatar 目录中没有图片文件")
            input("按回车键退出...")
            return
        
        print(f"找到 {len(images)} 张图片")
        print("差分图模式将使用现有图片系统")
        print("请启动主程序：streamlit run webui.py")
        
        # 启动桌面挂件
        start_overlay_window()
    
    elif choice == "3":
        # 仅桌面挂件
        start_overlay_window()
    
    elif choice == "4":
        print("已退出")
        return
    
    else:
        print("无效选项")


if __name__ == "__main__":
    main()
