
import proto

from common.movan_rpc.server import RPCServer

from account_server.config import config


import service.user_service as user_service  # 使用完全限定导入



RPC_SERVER = RPCServer(config['Network']['account_server_host'], config['Network']['account_server_post'])



@RPC_SERVER.method
async def account_register(
    uid:str,
    password:str,
)->bool:
    return user_service.account_register(uid,password)

    
@RPC_SERVER.method
async def account_login(
    uid:str,
    password:str,
)->bool:
    return user_service.account_login(uid,password)
 
