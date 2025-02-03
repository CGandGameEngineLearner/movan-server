# 关闭输出
$ErrorActionPreference = "Stop"

# 定义 Python 版本
$pythonVersion = "3.13.1"

# 只保留 pythonVersion 的纯数字部分
$pythonVersionNumericString = $pythonVersion -replace '\.', ''

$installerUrl = "https://mirrors.huaweicloud.com/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerFile = "python-$pythonVersion-amd64.exe"

# 定义安装路径
$userInstallPath = "$env:LOCALAPPDATA\Programs\Python\Python$pythonVersionNumericString"

# 检查是否已经安装了此版本的 Python
$pythonInstalled = $false

try {
    $regPath = "HKCU:\SOFTWARE\Python\PythonCore"
    $installedVersions = Get-ChildItem -Path $regPath -ErrorAction SilentlyContinue
    foreach ($version in $installedVersions) {
        $displayName = (Split-Path $version -Leaf)
        Write-Output "检测到本机已有 Python $displayName"
        if ($version.PSChildName -eq $pythonVersion) {
            $pythonInstalled = $true
        }
    }
} catch {
    if ($pythonInstalled -eq $false) {
        Write-Output "未检测到任何已安装的 Python 版本。"
    }
}

if ($pythonInstalled) {
    Write-Output "Python $pythonVersion 已安装在计算机上。"
} else {
    Write-Output "Python $pythonVersion 未在计算机上安装，准备自动安装Python $pythonVersion"
    Write-Output "正在加载中，请耐心等待，切勿关闭此窗口！"

    # 下载 Python 安装程序
    Write-Output "正在下载 Python 安装程序..."
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerFile

    # 安装 Python
    Write-Output "正在安装 Python，请稍候..."
    Start-Process -FilePath $installerFile -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 DefaultJustForMeTargetDir=$userInstallPath" -Wait

    # 将 Python 添加到系统环境变量中
    [Environment]::SetEnvironmentVariable("PATH", "$env:PATH;$userInstallPath", [EnvironmentVariableTarget]::User)

    # 将 Python 添加到注册表
    $pythonPath = "$userInstallPath\python.exe"
    New-Item -Path "HKCU:\Software\Python\PythonCore\$pythonVersion" -Force
    Set-ItemProperty -Path "HKCU:\Software\Python\PythonCore\$pythonVersion" -Name "(default)" -Value $pythonVersion
    Set-ItemProperty -Path "HKCU:\Software\Python\PythonCore\$pythonVersion" -Name "InstallPath" -Value $userInstallPath
    Set-ItemProperty -Path "HKCU:\Software\Python\PythonCore\$pythonVersion" -Name "ExecutablePath" -Value $pythonPath

    # 删除安装程序
    Write-Output "Python 安装完成！删除安装程序..."
    Remove-Item -Path $installerFile

    Write-Output "Python $pythonVersion 已安装成功"
}

# 创建虚拟环境
& "$userInstallPath\python.exe" -m venv venv

# 激活虚拟环境
& .\venv\Scripts\Activate.ps1

# 运行 run.bat
& .\run.bat

# 运行结束后不立马退出
Read-Host -Prompt "已执行完毕，按下回车键退出"