import asyncio
import grpc
import proto
from config import config
from loguru import logger

logger.add(
    sink=config['Log']['sink'],
    rotation=config['Log']['rotation'],
    retention=config['Log']['retention'],
    compression=config['Log']['compression'],
    enqueue=config['Log']['enqueue'],
    backtrace=config['Log']['backtrace'],
    diagnose=config['Log']['diagnose'],
    level=config['Log']['level'],
)

class account_server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def run(self):
        pass