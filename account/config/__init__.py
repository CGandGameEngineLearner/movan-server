import os
import json


current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


config_path = os.path.join(current_dir, 'config.json')


with open(config_path, 'r', encoding='utf-8') as config_file:
    CONFIG = json.load(config_file)