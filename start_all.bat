@echo off
chcp 65001 >nul
echo ========================================
echo   🚀 启动桌面差分图宠物 + B 站机器人
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo 📦 检查依赖...
pip show PyQt5 >nul 2>&1
if errorlevel 1 (
    echo ⚠️  正在安装 PyQt5...
    pip install PyQt5 pillow playsound
)

echo.
echo ✅ 准备就绪！
echo.
echo 🎭 启动桌面宠物...
start "桌面宠物" python desktop_diff_pet.py

timeout /t 3 /nobreak >nul

echo 💬 启动 B 站机器人界面...
start "B 站机器人" streamlit run webui.py

echo.
echo ========================================
echo   ✨ 所有服务已启动！
echo   - 桌面右下角会出现透明悬浮窗
echo   - 浏览器会自动打开配置界面
echo   - 按 Ctrl+C 可关闭此窗口 (不影响已启动的程序)
echo ========================================
pause
