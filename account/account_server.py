import asyncio
# import grpc
# from grpc import Server
# from grpc_reflection.v1alpha import reflection
from common.design_pattern.singleton import singleton
# 修改这行，使用完全限定导入


from account.config import CONFIG
from logger import logger
from typing import Optional

from account.rpc.rpc_server import ACCOUNT_RPC_SERVER
import service.account_server_rpc_servicer



@singleton
class account_server:
    def __init__(self):
        self.rpc_server = ACCOUNT_RPC_SERVER

    async def shutdown(self):
        await self.rpc_server.shutdown()

    def run(self):
        asyncio.run(self.start())
        
    async def start(self):
        await self.rpc_server.start()
        

ACCOUNT_SERVER = account_server()

if __name__ == "__main__":
    ACCOUNT_SERVER.run()