@echo off
chcp 65001 >nul
title 天童爱丽丝 - 一键启动

echo ========================================
echo   天童爱丽丝 桌面宠物一键启动包
echo   配置：差分图 + DDSP变声 + 免费AI
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python环境，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 正在安装依赖...
python install_deps.py
if %errorlevel% neq 0 (
    echo [警告] 部分依赖安装失败，将使用降级模式
)

echo.
echo [2/4] 检查配置文件...
if not exist config_alice.json (
    echo [错误] 配置文件缺失
    pause
    exit /b 1
)

echo [3/4] 检查资源文件...
if not exist assets\models (
    mkdir assets\models
    echo [提示] 请将DDSP模型(.sf_pkg)放入 assets\models\
)
if not exist assets\avatar (
    mkdir assets\avatar
    echo [提示] 请将差分图放入 assets\avatar\
)

echo.
echo [4/4] 启动爱丽丝...
echo.
echo ========================================
echo   启动成功！爱丽丝已在桌面等候
echo   右键点击头像可进行更多操作
echo ========================================
echo.

python neuro_alice_core.py

pause
