import os
import json

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 获取配置文件路径
config_path = os.path.join(current_dir, 'config.json')

# 正确的加载方式：打开文件并传入文件对象
with open(config_path, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)