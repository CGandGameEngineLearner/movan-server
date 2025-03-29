from common.movan_rpc import RPCClient
from typing import Callable
import inspect
import functools

class SyncServerStub:
    # 类级别装饰器工厂函数
    @staticmethod
    def stub_method(func):
        # 检查是否为异步函数
        if not inspect.iscoroutinefunction(func):
            raise SyntaxError("服务端方法的存根函数必须使用async def定义")
        
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 调用RPC客户端发送请求
            result = await self.sync_server_client.call(func.__name__, args, kwargs)
            return result
            
        return wrapper
    
    def __init__(self, host: str, port: int):
        self.sync_server_client = RPCClient(host, port)

    async def start(self):
        await self.sync_server_client.start()
    
    @stub_method
    async def allocate_user(self, uid: str, token: str, room_id: int, crypto_key: str, crypto_salt: str):
        pass

    @stub_method
    async def remove_user(self, uid):
        pass