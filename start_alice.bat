@echo off
chcp 65001 >nul
echo ================================================
echo 🎮 天童爱丽丝 - 差分版 Neuro-sama 一键启动
echo ================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python 已就绪

REM 运行主程序（会自动安装依赖）
echo 🚀 正在启动爱丽丝...
echo.
python neuro_alice_core.py

if errorlevel 1 (
    echo.
    echo ❌ 启动失败，请检查错误信息
    pause
)
