from setuptools import setup, find_packages

def read_requirements(filename='requirements.txt'):
    with open(filename) as f:
        # 过滤掉空行和注释行
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        # 移除版本固定符号 ==，使用 >= 代替，这样可以安装最新的兼容版本
        requirements = [req.replace('==', '>=') for req in requirements]
        return requirements

setup(
    name="movan_rpc",
    version="0.1",
    packages=find_packages(),
    install_requires=read_requirements(),
    python_requires='>=3.11',
    author="lifesize",
    author_email="lifesize1@qq.com",
    description="Movan Server Implementation",
    keywords="rpc, movan, server, sync, lockstep, frame lock sync, frame synchronization, game server",
    url="https://github.com/CGandGameEngineLearner/movan-server",  # 项目的 URL
)