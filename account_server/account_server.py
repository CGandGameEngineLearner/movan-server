import asyncio
import grpc
from grpc import Server
from grpc_reflection.v1alpha import reflection
from common.singleton import singleton
# 修改这行，使用完全限定导入
from proto import client_pb2, client_pb2_grpc

from config import config
from logger import logger
from typing import Optional






@singleton
class account_server:
    def __init__(self):
        self.rpc_server:Optional[Server] = None

    async def shutdown(self):
        await self.rpc_server.stop()

    async def run(self):
        await self.serve()
        
    async def serve(self):
        self.rpc_server = grpc.aio.server()
        from service.account_server_rpc_servicer import AccountServerRpcServicer
        client_pb2_grpc.add_AccountServerServicer_to_server(AccountServerRpcServicer(),self.rpc_server)
        SERVICE_NAMES = (
            client_pb2.DESCRIPTOR.services_by_name["AccountServer"].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, self.rpc_server)
        self.rpc_server.add_insecure_port(config["Network"]["account_server_host"]+":"+str(config["Network"]["account_server_port"]))
        await self.rpc_server.start()
        await self.rpc_server.wait_for_termination()

ACCOUNT_SERVER = account_server()
if __name__ == "__main__":
    asyncio.run(ACCOUNT_SERVER.run())