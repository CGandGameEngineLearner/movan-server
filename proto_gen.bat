@echo off
setlocal EnableDelayedExpansion

echo ===================================================
echo Protocol Buffers 3 Code Generator
echo ===================================================

REM 配置虚拟环境路径（根据你的实际路径修改）
set VENV_PATH=venv
set VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat
set PROTOC_PATH=movan_protobuf\protoc.exe

echo ===================================================
echo Checking Python virtual environment...
echo ===================================================

REM 检查虚拟环境是否存在
if not exist "%VENV_PATH%\" (
    echo Virtual environment not found at '%VENV_PATH%'
    
    echo Creating new virtual environment...
    python -m venv %VENV_PATH%
    
    if !ERRORLEVEL! neq 0 (
        echo Failed to create virtual environment.
        echo Please make sure Python is installed and available in PATH.
        exit /b 1
    )
    
    echo Virtual environment created successfully.
)

REM 激活虚拟环境
echo Activating virtual environment...
call "%VENV_ACTIVATE%"

if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)

echo Virtual environment activated successfully.
echo Python executable: %PYTHON%
python --version

echo ===================================================
echo Checking protoc executable...
echo ===================================================

REM 检查protoc是否存在
if not exist "%PROTOC_PATH%" (
    echo [ERROR] protoc executable not found at '%PROTOC_PATH%'
    echo Please make sure protoc.exe is available in the specified path.
    exit /b 1
)

echo Found protoc at: %PROTOC_PATH%

echo ===================================================
echo Compiling protobuf3 files...
echo ===================================================

REM 确保目标目录存在
if not exist ".\account_server\proto" mkdir ".\account_server\proto"
if not exist ".\sync_server\proto" mkdir ".\sync_server\proto"

echo.
echo Generating Protocol Buffers 3 code...
echo.

set ERRORS=0
set TOTAL_FILES=0

REM 使用本地的protoc.exe来生成代码
for %%f in (.\movan_protobuf\*.proto) do (
    set /a TOTAL_FILES+=1
    echo Processing: %%f
    echo --------------------------------------
    
    REM 验证proto文件是否使用proto3语法
    type "%%f" | findstr /C:"syntax = \"proto3\"" > nul
    if !ERRORLEVEL! neq 0 (
        echo [WARNING] %%f might not specify proto3 syntax explicitly.
        echo           Consider adding 'syntax = "proto3";' as the first line.
    )
    
    echo Generating for account_server...
    "%PROTOC_PATH%" -I=.\movan_protobuf ^
        --python_out=.\account_server\proto ^
        %%f
    
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to compile %%f for account_server
        set /a ERRORS+=1
    ) else (
        echo [SUCCESS] Compiled %%f for account_server
    )
    
    echo Generating for sync_server...
    "%PROTOC_PATH%" -I=.\movan_protobuf ^
        --python_out=.\sync_server\proto ^
        %%f
    
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to compile %%f for sync_server
        set /a ERRORS+=1
    ) else (
        echo [SUCCESS] Compiled %%f for sync_server
    )
    
    echo.
)

echo ===================================================
echo Summary of proto3 code generation:
echo ===================================================
echo Total proto files processed: !TOTAL_FILES!
echo Errors encountered: !ERRORS!
echo.

echo Files in account_server/proto:
dir /b ".\account_server\proto\"
echo.
echo Files in sync_server/proto:
dir /b ".\sync_server\proto\"
echo.

if !ERRORS! gtr 0 (
    echo [WARNING] Some files failed to compile properly.
    echo Please check the output above for details.
) else (
    echo [SUCCESS] All files compiled successfully!
)

echo ===================================================
echo Proto3 compilation completed!
echo ===================================================

REM 提示用户回车继续
pause

REM 结束本地变量作用域
endlocal