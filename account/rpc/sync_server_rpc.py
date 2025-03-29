
from account.config import CONFIG
from account import proto
from sync.logger import logger

from typing import Dict
from sync_server_stub import SyncServerStub
from common.utils import extract_host_port

import asyncio

SYNC_SERVER_STUBS:Dict[int,SyncServerStub] = {}

for i,url in enumerate(CONFIG['SyncServer']['urls']):
    host,port = extract_host_port(url)
    stub = SyncServerStub(host,port)
    SYNC_SERVER_STUBS[i] = stub
        

def init():
    for stub in SYNC_SERVER_STUBS.values():
        asyncio.create_task(stub.start())
    


if __name__ == '__main__':
    crypto_key = '12345678901234567890123456789012'
    crypto_salt = '1234567890123456'
    
    import time
    time.sleep(5)
   
    async def test():
        init()
        await asyncio.sleep(5)
        respond = await SYNC_SERVER_STUBS[0].allocate_user('lifesize0', '114514', 0, crypto_key, crypto_salt)
        print(respond)
        
    asyncio.run(test())

    