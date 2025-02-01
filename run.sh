#!/bin/bash

if [ -f requirements.txt ]; then
    echo "have requirements.txt"
    pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
else
    echo "do not have requirements.txt"
fi