@echo off
setlocal EnableDelayedExpansion

echo ===================================================
echo Protocol Buffers 3 Code Generator with gRPC Support
echo ===================================================

REM �������⻷��·�����������ʵ��·���޸ģ�
set VENV_PATH=venv
set VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat

echo ===================================================
echo Checking Python virtual environment...
echo ===================================================

REM ������⻷���Ƿ����
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

REM �������⻷��
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
echo Installing required packages for protobuf3...
echo ===================================================

REM ��װ��Ҫ�İ���ȷ���汾����protobuf3�������mypy-protobuf
echo Installing/Updating packages for protobuf3 compatibility...
pip install -U grpcio-tools protobuf mypy-protobuf

if %ERRORLEVEL% neq 0 (
    echo Failed to install required packages.
    exit /b 1
)

echo Installed packages:
pip list | findstr "grpcio protobuf mypy"

echo ===================================================
echo Compiling protobuf3 files with type annotations...
echo ===================================================

REM ȷ��Ŀ��Ŀ¼����
if not exist ".\account_server\proto" mkdir ".\account_server\proto"
if not exist ".\sync_server\proto" mkdir ".\sync_server\proto"



REM ��������.proto�ļ�������Ŀ��Ŀ¼������gRPC�����������ʹ��
echo.
echo Generating Protocol Buffers 3, gRPC code and type stubs (.pyi files)...
echo.

set ERRORS=0
set TOTAL_FILES=0

REM ͳһʹ��Python��grpcio-tools�����ɴ���
for %%f in (.\movan_protobuf\*.proto) do (
    set /a TOTAL_FILES+=1
    echo Processing: %%f
    echo --------------------------------------
    
    REM ��֤proto�ļ��Ƿ�ʹ��proto3�﷨
    type "%%f" | findstr /C:"syntax = \"proto3\"" > nul
    if !ERRORLEVEL! neq 0 (
        echo [WARNING] %%f might not specify proto3 syntax explicitly.
        echo           Consider adding 'syntax = "proto3";' as the first line.
    )
    
    echo Generating for account_server...
    python -m grpc_tools.protoc -I=.\movan_protobuf ^
        --python_out=.\account_server\proto ^
        --grpc_python_out=.\account_server\proto ^
        --mypy_out=.\account_server\proto ^
        %%f
    
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to compile %%f for account_server
        set /a ERRORS+=1
    ) else (
        echo [SUCCESS] Compiled %%f for account_server
    )
    
    echo Generating for sync_server...
    python -m grpc_tools.protoc -I=.\movan_protobuf ^
        --python_out=.\sync_server\proto ^
        --grpc_python_out=.\sync_server\proto ^
        --mypy_out=.\sync_server\proto ^
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
    echo [SUCCESS] All files compiled successfully with type annotations!
)

echo ===================================================
echo Proto3 compilation with type support completed!
echo ===================================================

REM ��ʾ�û��س�����
pause

REM �������ر���������
endlocal