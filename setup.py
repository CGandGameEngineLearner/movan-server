from setuptools import setup, find_packages

setup(
    name="movan-server",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'aiokcp',
        'loguru',
        'toml',
    ],
    python_requires='>=3.12',
)