# �ر����
$ErrorActionPreference = "Stop"

# ���� Python �汾
$pythonVersion = "3.13.1"

# ֻ���� pythonVersion �Ĵ����ֲ���
$pythonVersionNumericString = $pythonVersion -replace '\.', ''

$installerUrl = "https://mirrors.huaweicloud.com/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerFile = "python-$pythonVersion-amd64.exe"

# ���尲װ·��
$userInstallPath = "$env:LOCALAPPDATA\Programs\Python\Python$pythonVersionNumericString"

# ����Ƿ��Ѿ���װ�˴˰汾�� Python
$pythonInstalled = $false

try {
    $regPath = "HKCU:\SOFTWARE\Python\PythonCore"
    $installedVersions = Get-ChildItem -Path $regPath -ErrorAction SilentlyContinue
    foreach ($version in $installedVersions) {
        $displayName = (Split-Path $version -Leaf)
        Write-Output "��⵽�������� Python $displayName"
        if ($version.PSChildName -eq $pythonVersion) {
            $pythonInstalled = $true
        }
    }
} catch {
    if ($pythonInstalled -eq $false) {
        Write-Output "δ��⵽�κ��Ѱ�װ�� Python �汾��"
    }
}

if ($pythonInstalled) {
    Write-Output "Python $pythonVersion �Ѱ�װ�ڼ�����ϡ�"
} else {
    Write-Output "Python $pythonVersion δ�ڼ�����ϰ�װ��׼���Զ���װPython $pythonVersion"
    Write-Output "���ڼ����У������ĵȴ�������رմ˴��ڣ�"

    # ���� Python ��װ����
    Write-Output "�������� Python ��װ����..."
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerFile

    # ��װ Python
    Write-Output "���ڰ�װ Python�����Ժ�..."
    Start-Process -FilePath $installerFile -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 DefaultJustForMeTargetDir=$userInstallPath" -Wait

    # �� Python ��ӵ�ϵͳ����������
    [Environment]::SetEnvironmentVariable("PATH", "$env:PATH;$userInstallPath", [EnvironmentVariableTarget]::User)

    # �� Python ��ӵ�ע���
    $pythonPath = "$userInstallPath\python.exe"
    New-Item -Path "HKCU:\Software\Python\PythonCore\$pythonVersion" -Force
    Set-ItemProperty -Path "HKCU:\Software\Python\PythonCore\$pythonVersion" -Name "(default)" -Value $pythonVersion
    Set-ItemProperty -Path "HKCU:\Software\Python\PythonCore\$pythonVersion" -Name "InstallPath" -Value $userInstallPath
    Set-ItemProperty -Path "HKCU:\Software\Python\PythonCore\$pythonVersion" -Name "ExecutablePath" -Value $pythonPath

    # ɾ����װ����
    Write-Output "Python ��װ��ɣ�ɾ����װ����..."
    Remove-Item -Path $installerFile

    Write-Output "Python $pythonVersion �Ѱ�װ�ɹ�"
}

# �������⻷��
& "$userInstallPath\python.exe" -m venv venv

# �������⻷��
& .\venv\Scripts\Activate.ps1

# ���� run.bat
& .\run.bat

# ���н����������˳�
Read-Host -Prompt "��ִ����ϣ����»س����˳�"