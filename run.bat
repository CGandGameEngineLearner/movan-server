@echo off
if exist requirements.txt (
    echo have requirements.txt
    pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
) else (
    echo do not have requirements.txt
)

