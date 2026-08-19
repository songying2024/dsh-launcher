@echo off
cd /d "%~dp0"
python dsh_launcher.py
if errorlevel 1 (
    echo.
    echo 启动失败，请检查 Python 环境是否正确安装。
    pause
)
