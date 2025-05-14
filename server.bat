@echo off
setlocal

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"

REM 设置 PYTHONPATH 环境变量
set "PYTHONPATH=%SCRIPT_DIR%"

REM 设置虚拟环境 Python 路径
set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"

REM 设置 account_server.py 路径
set "ACCOUNT_SERVER=%SCRIPT_DIR%account\account_server.py"

REM 启动命令
"%PYTHON_EXE%" "%ACCOUNT_SERVER%"

endlocal