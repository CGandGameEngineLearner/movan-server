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
        crypto: AES_CBC = AES_CBC(crypto_key, crypto_salt)
        self.user_info[uid] = {
            'token': token,
            'room_id': room_id,
            'crypto': crypto,
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
                msg = self.decrypt_msg(data)
                if msg is None:
                    return
                self.sync_server.msg_received(msg)
            except Exception as e:
                logger.warning(e)
                return

    
        def encrypt_msg(self, uid: str, proto: str, data: Any, timestamp: float) -> bytes:
            user_info = self.sync_server.get_user_info(uid)
            crypto: AES_CBC = user_info["crypto"]
            
            # 加密数据
            data_bytes = msgpack.packb(data)
            encrypted_data = crypto.encrypt(data_bytes)
            
            # 加密额外数据
            extra_data = {"proto": proto, "timestamp": timestamp, "token": user_info['token']}
            extra_data_bytes = msgpack.packb(extra_data)
            encrypted_extra_data = crypto.encrypt(extra_data_bytes)
            
            # 打包消息
            msg = {"uid": uid, "data": encrypted_data, "extra_data": encrypted_extra_data}
            return msgpack.packb(msg)

        def decrypt_msg(self, data: bytes) -> Optional[dict]:
            try:
                msg = msgpack.unpackb(data)
            except Exception as e:
                logger.warning(f"Failed to unpack message: {e}")
                return None

            uid = msg.get('uid')
            if uid not in self.sync_server.user_info:
                logger.warning(f"Unknown user ID: {uid}")
                return None
            
            user_info = self.sync_server.get_user_info(uid)
            crypto: AES_CBC = user_info["crypto"]

            try:
                # 解密数据
                encrypted_data = msg.get('data')
                if not isinstance(encrypted_data, bytes):
                    logger.warning(f"Invalid data format for UID: {uid}")
                    return None
                decrypted_data = crypto.decrypt(encrypted_data)
                data = msgpack.unpackb(decrypted_data)

                # 解密额外数据
                encrypted_extra_data = msg.get('extra_data')
                if not isinstance(encrypted_extra_data, bytes):
                    logger.warning(f"Invalid extra_data format for UID: {uid}")
                    return None
                decrypted_extra_data = crypto.decrypt(encrypted_extra_data)
                extra_data = msgpack.unpackb(decrypted_extra_data)

                # 验证额外数据
                proto = extra_data.get('proto')
                if not isinstance(proto, str):
                    logger.warning(f"Invalid proto format for UID: {uid}")
                    return None
                
                token = extra_data.get('token')
                if token != user_info['token']:
                    logger.warning(f"Invalid token for UID: {uid}")
                    return None
                
                timestamp = extra_data.get('timestamp')
                if not isinstance(timestamp, float):
                    logger.warning(f"Invalid timestamp format for UID: {uid}")
                    return None

                return {"uid": uid, "data": data, "extra_data": extra_data}
            except Exception as e:
                logger.warning(f"Error decrypting message: {e}")
                return None

    async def msg_received(self,msg:dict):
        if msg['extra_data']['proto'] == 'join_room':
            logger.info(f"UID为{msg['uid']}的客户端发送了个加入请求")

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
    asyncio.run(SYNC_SERVER.start())
    crypto_key = b'12345678901234567890123456789012'
    crypto_salt = b'1234567890123456'
    SYNC_SERVER.allocate_user('lifesize','114514',1,crypto_key,crypto_salt)
    

    