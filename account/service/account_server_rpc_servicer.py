
from account.rpc.rpc_server import RPC_SERVER


from ..config import CONFIG


from ..service import user_service 




@RPC_SERVER.method
async def account_sign_up(
    uid:str,
    password:str,
)->bool:
    return user_service.account_sign_up(uid,password)

    
@RPC_SERVER.method
async def account_login(
    uid:str,
    password:str,
)->bool:
    return user_service.account_login(uid,password)
 
