@echo off
setlocal

REM 定义 Python 版本
set "pythonVersion=3.13.1"

REM 只保留 pythonVersion 的纯数字部分
for /f "delims=." %%i in ("%pythonVersion%") do set "pythonVersionNumericString=%%i%%j%%k"

set "installerUrl=https://mirrors.huaweicloud.com/python/%pythonVersion%/python-%pythonVersion%-amd64.exe"
set "installerFile=python-%pythonVersion%-amd64.exe"

REM 定义安装路径
set "userInstallPath=%LOCALAPPDATA%\Programs\Python\Python%pythonVersionNumericString%"

REM 检查是否已经安装了此版本的 Python
set "pythonInstalled=false"

for /f "tokens=*" %%i in ('reg query "HKCU\SOFTWARE\Python\PythonCore" 2^>nul') do (
    for /f "tokens=*" %%j in ('reg query "HKCU\SOFTWARE\Python\PythonCore\%%i" /v "DisplayName" 2^>nul') do (
        echo 检测到本机已有 Python %%i
        if "%%i"=="%pythonVersion%" (
            set "pythonInstalled=true"
        )
    )
)

if "%pythonInstalled%"=="true" (
    echo Python %pythonVersion% 已安装在计算机上。
) else (
    echo Python %pythonVersion% 未在计算机上安装，准备自动安装Python %pythonVersion%
    echo 正在加载中，请耐心等待，切勿关闭此窗口！

    REM 下载 Python 安装程序
    echo 正在下载 Python 安装程序...
    powershell -Command "Invoke-WebRequest -Uri %installerUrl% -OutFile %installerFile%"

    REM 安装 Python
    echo 正在安装 Python，请稍候...
    start /wait "" "%installerFile%" /quiet InstallAllUsers=0 PrependPath=1 DefaultJustForMeTargetDir="%userInstallPath%"

    REM 将 Python 添加到系统环境变量中
    setx PATH "%PATH%;%userInstallPath%"

    REM 将 Python 添加到注册表
    set "pythonPath=%userInstallPath%\python.exe"
    reg add "HKCU\Software\Python\PythonCore\%pythonVersion%" /ve /d "%pythonVersion%" /f
    reg add "HKCU\Software\Python\PythonCore\%pythonVersion%" /v "InstallPath" /d "%userInstallPath%" /f
    reg add "HKCU\Software\Python\PythonCore\%pythonVersion%" /v "ExecutablePath" /d "%pythonPath%" /f

    REM 删除安装程序
    echo Python 安装完成！删除安装程序...
    del "%installerFile%"

    echo Python %pythonVersion% 已安装成功
)

REM 创建虚拟环境
%userInstallPath%\python.exe -m venv venv

REM 激活虚拟环境
call venv\Scripts\activate.bat

call run.bat

REM 运行结束后不立马退出
pause