from setuptools import setup, find_packages

def read_requirements(filename='requirements.txt'):
    with open(filename) as f:
        # 过滤掉空行和注释行
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        # 移除版本固定符号 ==，使用 >= 代替，这样可以安装最新的兼容版本
        requirements = [req.replace('==', '>=') for req in requirements]
        return requirements

setup(
    name="movan-server",
    version="0.1",
    packages=find_packages(),
    install_requires=read_requirements(),
    python_requires='>=3.8',  # 根据你的项目需求调整 Python 版本
    author="lifesize",
    author_email="lifesize1@qq.com",
    description="Movan Server Implementation",
    keywords="movan, server, sync, frame synchronization, game server",
    url="https://github.com/CGandGameEngineLearner/movan-server",  # 项目的 URL
)