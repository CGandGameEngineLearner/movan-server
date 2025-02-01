# 定义 Python 安装程序的Python版本，跳过华为云下载指定版本的 Python 安装程序
$pythonVersion = "3.13.1"

# 只保留 $pythonVersion 的纯数字部分 后续会加上python前缀 作为安装路径的文件夹名
$pythonVersionNumericString = $pythonVersion -replace '\D', ''

$installerUrl = "https://mirrors.huaweicloud.com/python/"+$pythonVersion+"/python-“+$pythonVersion+”-amd64.exe"
$installerFile = "python-" + $pythonVersion + "-amd64.exe"

# 检查是否已经安装了此版本的Pyhon
$pythonInstalled = $false


# 定义安装路径
$userInstallPath = "$env:LOCALAPPDATA\Programs\Python\Python"+$pythonVersionNumericString

try
{
    if (Test-Path "HKCU:\SOFTWARE\Python\PythonCore")
    {

        # 获取当前Windows用户所有已安装的Python版本
        $pythonVersions = Get-ChildItem -Path "HKCU:\SOFTWARE\Python\PythonCore" | ForEach-Object { $_.PSChildName }


        foreach ($version in $pythonVersions)
        {
            Write-Host "检测到本机已有 Python $version"
            if ($version -eq $pythonVersion)
            {
                $pythonInstalled = $true
                break
            }
        }
    }
    else
    {
        Write-Host "未在注册表中发现有python的记录，说明可能没有安装过python"
    }
}
catch {
    Write-Host "An error occurred: $_"
}

# 输出结果
if ($pythonInstalled)
{
    Write-Host "Python $pythonVersion 已安装在计算机上。"
}
else
{
    Write-Host "Python $pythonVersion 未在计算机上安装，准备自动安装Python $pythonVersion"
}

Write-Host "正在加载中，请耐心等待，切勿关闭此窗口！"

try{
    # 如果没安装指定版本Python 则自动安装
    if ($pythonInstalled -eq $false)
    {
        # 下载 Python 安装程序
        Write-Host "正在下载 Python 安装程序..."
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerFile

        # 安装 Python
        Write-Host "正在安装 Python，请稍候..."
        # 运行 Python 安装程序
        Start-Process -FilePath $installerFile -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1", "DefaultJustForMeTargetDir=`"$userInstallPath`"" -Wait

        # 将 Python 添加到系统环境变量中
        $env:Path += ";$userInstallPath"

        # 将 Python 添加到注册表
        $pythonPath = Join-Path $userInstallPath "python.exe"

        $pythonKey = "HKCU:\Software\Python\PythonCore\$pythonVersion"
        New-Item -Path $pythonKey
        New-ItemProperty -Path $pythonKey -Name "(Default)" -Value $pythonVersion
        New-ItemProperty -Path $pythonKey -Name "InstallPath" -Value $userInstallPath
        New-ItemProperty -Path $pythonKey -Name "ExecutablePath" -Value $pythonPath

        # 删除安装程序
        Write-Host "Python 安装完成！删除安装程序..."
        Remove-Item $installerFile

        Write-Host "Python "+$pythonVersion+" 已安装成功"
    }


    # 创建虚拟环境
    python -m venv venv

    # 激活虚拟环境
    .\venv\Scripts\Activate.ps1


    .\run.bat
}
catch {
    Write-Host "发生异常，错误为: $_"
}

#运行结束后不立马退出
Pause