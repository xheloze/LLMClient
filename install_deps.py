import subprocess
import sys
import os

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
        return True
    except Exception as e:
        print(f"安装 {package} 失败: {e}")
        return False

def main():
    print("=" * 50)
    print("天童爱丽丝 - 智能依赖安装器")
    print("=" * 50)
    
    # 核心依赖列表
    packages = [
        "PyQt5",
        "Pillow",
        "requests",
        "websockets",
        "edge-tts",
        "numpy",
        "pydub",
        "SpeechRecognition",
        "playsound==1.2.2",
    ]
    
    # DDSP相关（可选，失败则降级）
    ddsp_packages = [
        "ddsp-svc",
        "torch",
        "torchaudio",
    ]
    
    print("\n[阶段1] 安装核心依赖...")
    success_count = 0
    for pkg in packages:
        print(f"正在安装 {pkg}...", end=" ")
        if install_package(pkg):
            print("✓")
            success_count += 1
        else:
            print("✗")
    
    print(f"\n核心依赖安装完成：{success_count}/{len(packages)}")
    
    print("\n[阶段2] 尝试安装DDSP相关依赖（可选）...")
    ddsp_success = 0
    for pkg in ddsp_packages:
        print(f"正在安装 {pkg}...", end=" ")
        if install_package(pkg):
            print("✓")
            ddsp_success += 1
        else:
            print("✗ (将使用Edge-TTS降级模式)")
    
    if ddsp_success == len(ddsp_packages):
        print("\n✓ DDSP完整功能已启用")
    else:
        print("\n⚠ DDSP功能不可用，将自动降级为Edge-TTS")
    
    print("\n" + "=" * 50)
    print("依赖安装完成！")
    print("请运行 start_alice.bat 启动程序")
    print("=" * 50)

if __name__ == "__main__":
    main()
