@echo off
setlocal EnableDelayedExpansion

REM 定义 Python 版本
set "pythonVersion=3.11.9"
set "pythonVersionBrief=3.11"

REM 只保留 pythonVersion 的纯数字部分
for /f "tokens=1-3 delims=." %%i in ("%pythonVersion%") do (
    set "pythonVersionNumericString=%%i%%j%%k"
)

set "installerUrl=https://mirrors.huaweicloud.com/python/%pythonVersion%/python-%pythonVersion%-amd64.exe"
set "installerFile=python-%pythonVersion%-amd64.exe"

REM 定义安装路径
set "userInstallPath=%LOCALAPPDATA%\Programs\Python\Python%pythonVersionNumericString%"

REM 检查是否已经安装了此版本的 Python
set "pythonInstalled=false"

echo 检测Python %pythonVersionBrief% 安装情况...

REM 方法1：检查注册表
echo 1. 从注册表检测Python...
reg query "HKCU\SOFTWARE\Python\PythonCore\%pythonVersionBrief%" >nul 2>&1
if !errorlevel! equ 0 (
    echo 在注册表中找到 Python %pythonVersionBrief%
    set "pythonInstalled=true"
)

REM 方法2：从开始菜单检测
if "%pythonInstalled%"=="false" (
    echo 2. 从开始菜单检测Python...
    set "startMenuPath=%ProgramData%\Microsoft\Windows\Start Menu\Programs"
    set "userStartMenuPath=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
    
    REM 检查系统级开始菜单
    if exist "%startMenuPath%\Python %pythonVersionBrief%" (
        echo 在系统开始菜单找到 Python %pythonVersionBrief%
        set "pythonInstalled=true"
    ) else (
        for /d %%d in ("%startMenuPath%\Python*") do (
            echo %%~nxd | findstr /c:"Python %pythonVersionBrief%" >nul
            if !errorlevel! equ 0 (
                echo 在系统开始菜单找到 Python %pythonVersionBrief%
                set "pythonInstalled=true"
            )
        )
    )
    
    REM 检查用户级开始菜单
    if exist "%userStartMenuPath%\Python %pythonVersionBrief%" (
        echo 在用户开始菜单找到 Python %pythonVersionBrief%
        set "pythonInstalled=true"
    ) else (
        for /d %%d in ("%userStartMenuPath%\Python*") do (
            echo %%~nxd | findstr /c:"Python %pythonVersionBrief%" >nul
            if !errorlevel! equ 0 (
                echo 在用户开始菜单找到 Python %pythonVersionBrief%
                set "pythonInstalled=true"
            )
        )
    )
)

REM 方法3：直接检查安装路径
if "%pythonInstalled%"=="false" (
    echo 3. 检查Python安装路径...
    if exist "%userInstallPath%\python.exe" (
        echo 在 %userInstallPath% 找到Python可执行文件
        set "pythonInstalled=true"
    )
    
    set "altPath=%LOCALAPPDATA%\Programs\Python\Python%pythonVersionBrief%"
    if exist "!altPath!\python.exe" (
        echo 在 !altPath! 找到Python可执行文件
        set "pythonInstalled=true"
    )
)

REM 方法4：尝试执行Python并检查版本
if "%pythonInstalled%"=="false" (
    echo 4. 尝试执行Python检查版本...
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2" %%v in ('python -V 2^>^&1') do (
            echo %%v | findstr /b "%pythonVersionBrief%" >nul
            if !errorlevel! equ 0 (
                echo 找到匹配版本的Python: %%v
                set "pythonInstalled=true"
            )
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
    echo 正在安装 Python，请注意弹出的权限申请窗口，请允许执行...
    start /wait "" "%installerFile%" /quiet InstallAllUsers=0 PrependPath=1 DefaultJustForMeTargetDir="%userInstallPath%"

    REM 将 Python 添加到系统环境变量中
    setx PATH "%PATH%;%userInstallPath%"

    REM 将 Python 添加到注册表
    set "pythonPath=%userInstallPath%\python.exe"
    reg add "HKCU\Software\Python\PythonCore\%pythonVersionBrief%" /ve /d "%pythonVersion%" /f
    reg add "HKCU\Software\Python\PythonCore\%pythonVersionBrief%" /v "InstallPath" /d "%userInstallPath%" /f
    reg add "HKCU\Software\Python\PythonCore\%pythonVersionBrief%" /v "ExecutablePath" /d "%pythonPath%" /f

    REM 删除安装程序
    echo Python 安装完成！删除安装程序...
    del "%installerFile%"

    echo Python %pythonVersion% 已安装成功
)

REM 确保 userInstallPath 变量已正确设置
if not exist "%userInstallPath%\python.exe" (
    for /f "tokens=*" %%p in ('where python 2^>nul') do (
        set "userInstallPath=%%~dpp"
        set "userInstallPath=!userInstallPath:~0,-1!"
    )
)

REM 创建虚拟环境
echo 创建Python虚拟环境...
python%pythonVersionBrief% -m venv venv 2>nul
if %errorlevel% neq 0 (
    echo 使用python%pythonVersionBrief%命令失败，尝试使用完整路径...
    if exist "%userInstallPath%\python.exe" (
        echo 使用安装路径: %userInstallPath%\python.exe
        "%userInstallPath%\python.exe" -m venv venv
    ) else (
        echo 尝试查找Python可执行文件...
        where python 2>nul
        if %errorlevel% equ 0 (
            echo 使用系统Python创建虚拟环境
            python -m venv venv
        ) else (
            echo 未能找到可用的Python，虚拟环境创建失败！
            exit /b 1
        )
    )
) else (
    echo 成功使用python%pythonVersionBrief%创建虚拟环境
)


REM 激活虚拟环境
call venv\Scripts\activate.bat

@REM call run.bat

REM 运行结束后不立马退出
pause