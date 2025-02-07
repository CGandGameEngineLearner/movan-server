from aiokcp import create_server,create_connection, KCPStreamTransport
from aiokcp.crypto import AES_CBC
from aiokcp.sync import KCPSocket, KCPServer
import msgpack
from typing import Dict, List, Any, Optional, Union, Tuple
from room import Room
import asyncio
import toml
import os
from loguru import logger
import utils

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建 config.toml 文件的绝对路径
config_path = os.path.join(current_dir, 'config.toml')

# 读取并解析 TOML 文件
config = toml.load(config_path)

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





class SyncServer:
    def __init__(self, host: str, port: int, initial_num_of_rooms: int, max_num_of_rooms: int, kcp_kwargs=None):
        self.host = host
        self.port = port
        self.sync_core_count: int = 0
        self.transport_dict: Dict[str, KCPSocket] = {}
        self.room_dict: Dict[int, Room] = {}
        self.max_num_of_rooms = max_num_of_rooms
        self.kcp_kwargs:dict = kcp_kwargs
        for i in range(initial_num_of_rooms):
            self.room_dict[i] = Room(i)
            self.sync_core_count += 1

        self.kcp_server: Optional[KCPServer] = None
        self.user_info: Dict = {}
        self.proto_dict:Dict[str, SyncServer.Protocol] = {}
        self.token_dict:Dict[str,str] = {}
        self.crypto_dict:Dict[str,AES_CBC] = {}

    


    async def initialize_server(self):
        self.kcp_server = await create_server(
            protocol_factory=self.Protocol,
            host=self.host,
            port=self.port,
            kcp_kwargs=self.kcp_kwargs
        )
        async with self.kcp_server:
            await self.kcp_server.serve_forever()
    
    def add_proto(self,uid:str,proto):
        self.proto_dict[uid] = proto
        

    def allocate_user(self, uid: str, token: str, room_id: int, crypto_key: bytes, crypto_salt: bytes):
        self.token_dict[uid] = token
        crypto: AES_CBC = AES_CBC(crypto_key, crypto_salt)
        self.crypto_dict[uid] = crypto
        self.user_info[uid] = {
            'room_id': room_id,
        }


    def remove_user(self, uid):
        pass

    def get_user_info(self, uid: str):
        return self.user_info.get(uid)
    

    class Protocol(asyncio.Protocol):
        def __init__(self):
            self.sync_server = SYNC_SERVER
            

        def connection_made(self, transport):
            peername = transport.get_extra_info('peername')
            logger.info('Connection from {}'.format(peername))
            self.transport: KCPStreamTransport = transport

        def data_received(self, data:bytes):
            try:
                msg = utils.decrypt_msg(
                    data,
                    self.sync_server.token_dict,
                    self.sync_server.crypto_dict
                )
                if msg is None:
                    return
                self.sync_server.msg_received(msg)
            except Exception as e:
                logger.warning(e)
                return


    def msg_received(self,msg:dict):
        if msg['extra_data']['proto'] == 'join_room':
            logger.info(f"UID为\"{msg['uid']}\"的客户端发送了个加入请求")

    async def start(self):
        await self.initialize_server()
        


SYNC_SERVER = SyncServer(
    config['Network']['host'],
    config['Network']['port'],
    config['Server']['initial_num_of_rooms'],
    config['Server']['max_num_of_rooms'],
)

if __name__ == '__main__':
    logger.info("Sync server started")
    crypto_key = b'12345678901234567890123456789012'
    crypto_salt = b'1234567890123456'
    SYNC_SERVER.allocate_user('lifesize','114514',1,crypto_key,crypto_salt)
    asyncio.run(SYNC_SERVER.start())
    
    

    