#!/bin/bash
set -e

# 定义 Python 版本
pythonVersion="3.13"

echo "Python $pythonVersion 未安装，准备自动安装 Python $pythonVersion"
echo "加载中，请耐心等待，切勿关闭此窗口！"

# 安装 Python 3.13 及其 venv 模块
installPythonCommand="sudo apt install python${pythonVersion} python${pythonVersion}-venv"
eval ${installPythonCommand}

echo "Python $pythonVersion 已成功安装。"

# 创建虚拟环境
echo "创建虚拟环境..."
venvCommand="python${pythonVersion} -m venv venv"
eval ${venvCommand}

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate


# 运行 run.sh 脚本
# chmod +x run.sh
bash ./run.sh


# 运行结束后等待用户按键退出
read -p "运行结束，请按回车键退出..."