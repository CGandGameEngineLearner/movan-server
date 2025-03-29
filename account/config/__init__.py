import os
import tomllib


current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


config_path = os.path.join(current_dir, 'config.toml')


with open(config_path, 'rb') as config_file:
    CONFIG = tomllib.load(config_file)