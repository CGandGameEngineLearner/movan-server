@echo off
setlocal

REM ���� Python �汾
set "pythonVersion=3.12.8"

REM ֻ���� pythonVersion �Ĵ����ֲ���
set "pythonVersionNumericString=%pythonVersion:.=%"

set "installerUrl=https://mirrors.huaweicloud.com/python/%pythonVersion%/python-%pythonVersion%-amd64.exe"
set "installerFile=python-%pythonVersion%-amd64.exe"

REM ���尲װ·��
set "userInstallPath=%LOCALAPPDATA%\Programs\Python\Python%pythonVersionNumericString%"

REM ����Ƿ��Ѿ���װ�˴˰汾�� Python
set "pythonInstalled=false"

for /f "tokens=*" %%i in ('reg query "HKCU\SOFTWARE\Python\PythonCore" 2^>nul') do (
    for /f "tokens=*" %%j in ('reg query "%%i" /v "DisplayName" 2^>nul') do (
        set "displayName=%%~nxj"
        echo ��⵽�������� Python %displayName%
        if "%%~nxj"=="%pythonVersion%" (
            set "pythonInstalled=true"
        )
    )
)

if "%pythonInstalled%"=="true" (
    echo Python %pythonVersion% �Ѱ�װ�ڼ�����ϡ�
) else (
    echo Python %pythonVersion% δ�ڼ�����ϰ�װ��׼���Զ���װPython %pythonVersion%
    echo ���ڼ����У������ĵȴ�������رմ˴��ڣ�

    REM ���� Python ��װ����
    echo �������� Python ��װ����...
    powershell -Command "Invoke-WebRequest -Uri %installerUrl% -OutFile %installerFile%"

    REM ��װ Python
    echo ���ڰ�װ Python�����Ժ�...
    start /wait "" "%installerFile%" /quiet InstallAllUsers=0 PrependPath=1 DefaultJustForMeTargetDir="%userInstallPath%"

    REM ��� Python �Ƿ�ɹ���װ
    if exist "%userInstallPath%\python.exe" (
        echo Python ��װ�ɹ���

        REM �� Python ��ӵ�ϵͳ����������
        setx PATH "%PATH%;%userInstallPath%"

        REM �� Python ��ӵ�ע���
        reg add "HKCU\Software\Python\PythonCore\%pythonVersion%" /ve /d "%pythonVersion%" /f
        reg add "HKCU\Software\Python\PythonCore\%pythonVersion%" /v InstallPath /d "%userInstallPath%" /f
        reg add "HKCU\Software\Python\PythonCore\%pythonVersion%" /v ExecutablePath /d "%userInstallPath%\python.exe" /f

        REM ɾ����װ����
        echo Python ��װ��ɣ�ɾ����װ����...
        del "%installerFile%"

        echo Python %pythonVersion% �Ѱ�װ�ɹ�
    ) else (
        echo Python ��װʧ�ܣ����鰲װ����Ͱ�װ·����
        exit /b 1
    )
)

REM �������⻷��
echo ���ڴ������⻷��...
"%userInstallPath%\python.exe" -m venv venv

REM �������⻷��
call venv\Scripts\activate.bat

REM ���� run.bat
call run.bat

REM ���н����������˳�
pause