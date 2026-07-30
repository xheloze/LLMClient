@echo off
chcp 65001 >nul
echo ============================================================
echo   天童爱丽丝 - 桌面宠物启动器
echo   配置：i5-8400 + RTX 2060 + 32GB RAM
echo ============================================================
echo.

:menu
echo.
echo 请选择启动模式:
echo.
echo   [1] 完整桌面宠物 (语音识别+TTS+表情) ⭐推荐
echo   [2] 仅差分图显示 (轻量版)
echo   [3] 启动 B 站直播连接
echo   [4] 同时启动宠物 + 直播
echo   [0] 退出
echo.
set /p choice="请输入选项 (0-4): "

if "%choice%"=="1" goto full_pet
if "%choice%"=="2" goto avatar_only
if "%choice%"=="3" goto bilibili
if "%choice%"=="4" goto both
if "%choice%"=="0" goto end
goto menu

:full_pet
echo.
echo [🎮] 启动完整桌面宠物...
echo.
python desktop_pet_full.py --mode avatar
goto menu

:avatar_only
echo.
echo [🖼️] 启动差分图显示...
echo.
python desktop_pet.py --mode avatar
goto menu

:bilibili
echo.
echo [📺] 启动 B 站直播连接...
echo.
streamlit run webui.py
goto menu

:both
echo.
echo [🚀] 同时启动宠物和直播...
echo.
echo 正在启动桌面宠物...
start cmd /k "python desktop_pet_full.py --mode avatar"
timeout /t 3 /nobreak >nul
echo 正在启动 B 站直播...
streamlit run webui.py
goto menu

:end
echo.
echo 再见！
pause
